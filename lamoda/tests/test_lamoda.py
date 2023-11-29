import pytest
import aiohttp

from bs4 import BeautifulSoup

from settings import get_config

setup = get_config()


@pytest.mark.asyncio
async def test_lamoda():
    url = setup.lamoda_url + setup.lamoda_url_target + "1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_info = await response.text()
            assert response.status == 200
            soup = BeautifulSoup(response_info, "html.parser")
            count_of_products = (int(soup.find('span', class_='d-catalog-header__product-counter')
                                     .text.split()[0]))
            assert count_of_products > 0
