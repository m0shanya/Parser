import asyncio
from typing import List

import aiohttp
from bs4 import BeautifulSoup

from lamoda.models import Coat
from .dao.connector import MongoSaver
from .utils import to_decimal128
from settings import get_config

setup = get_config()


class CoatParser:
    """
    Class responsible for parsing coat data from a website and saving it to a database.
    """
    __link = setup.lamoda_url + setup.lamoda_url_target
    __pages = setup.pages

    @staticmethod
    async def _extract_info(html: str):
        """
        Extracts coat information from HTML.
        """
        soup = BeautifulSoup(html, "html.parser")
        grid = soup.find_all(class_=setup.grid)

        coats_list = []
        for element in grid:
            link = setup.lamoda_url + str(element.find("a")).split('"')[3]
            new_price_from_card = element.find("span", class_=setup.new_price_from_card)
            old_price_from_card = element.find("span", class_=setup.old_price_from_card)
            single_price_from_card = element.find("span", class_=setup.single_price_from_card)
            brand = element.find(class_=setup.card_brand).text.strip()
            category = element.find(class_=setup.category_name).text.strip()

            try:
                price = single_price_from_card.text.replace(" ", "").replace("р.", "")
                coat = Coat(price=price, category=category, brand=brand, link=link, sale_price=None)
                coat.price = to_decimal128(coat.price)
                coats_list.append(coat)
            except AttributeError:
                sale_price = new_price_from_card.text.replace(" ", "").replace("р.", "")
                price = old_price_from_card.text.replace(" ", "").replace("р.", "")
                coat = Coat(price=price, sale_price=sale_price, category=category, brand=brand, link=link)
                coat.sale_price = to_decimal128(coat.sale_price)
                coat.price = to_decimal128(coat.price)
                coats_list.append(coat)

        return coats_list

    @classmethod
    async def _get_page(cls, session: aiohttp.ClientSession, url: str) -> List[Coat]:
        """
        Retrieves coat information from a specific page.
        """
        async with session.get(url) as response:
            response_info = await response.text()
            return await cls._extract_info(html=response_info)

    @classmethod
    async def _load(cls) -> List[List[Coat]]:
        """
        Loads coat information from multiple pages.
        """
        tasks = []
        async with aiohttp.ClientSession() as session:
            for page in range(1, cls.__pages + 1):
                url = cls.__link + str(page)
                task = cls._get_page(session, url)
                tasks.append(task)
            return await asyncio.gather(*tasks)

    @classmethod
    async def _insert_data(cls, coats: List[List[Coat]]):
        """
        Inserts coat data into the database.
        """
        all_coats = [coat.dict() for item in coats for coat in item]
        await MongoSaver.bulk_save(all_coats)

    async def parse_coats(self):
        """
        Parses coat data from the website and saves it to the database.
        """
        await MongoSaver.remove_all_coats()
        load_tasks = asyncio.create_task(self._load())
        coats = await load_tasks
        await self._insert_data(coats)
