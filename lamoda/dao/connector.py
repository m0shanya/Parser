from typing import List

from ..models import Coat
from ..exeptions import validate
from database import Mongo
from settings import get_config

setup = get_config()


class MongoClient:
    _db = Mongo().get_database(setup.lamoda_database)


class MongoSaver(MongoClient):
    def __init__(self):
        self.collection = self._db.get_collection(setup.lamoda_collection)

    @classmethod
    async def bulk_save(cls, coats: list[dict]):
        await cls().collection.insert_many(coats)

    @classmethod
    async def get_coat(cls, category: str, brand: str) -> Coat:
        coat = await cls().collection.find_one({"brand": brand, "category": category})
        await validate(coat=coat)
        coat.pop("_id", None)
        return coat

    @classmethod
    async def get_coats(cls, category: str, brand: str) -> List[Coat]:
        coats = await cls().collection.find({"brand": brand, "category": category}).to_list(None)
        first_coat = coats[0] if coats else None
        await validate(coat=first_coat)
        [coat.pop("_id", None) for coat in coats]
        return coats

    @classmethod
    async def remove_all_coats(cls):
        collection = cls().collection
        await collection.delete_many({})
