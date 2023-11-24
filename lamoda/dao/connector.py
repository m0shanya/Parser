from typing import List

from ..models import Coat
from ..exeptions import validate
from database import Mongo
from settings import get_config

setup = get_config()


class MongoClient:
    """MongoDB client for database operations."""
    _db = Mongo().get_database(setup.lamoda_database)


class MongoSaver(MongoClient):
    def __init__(self):
        """MongoDB's collection for coat data in the Lamoda database."""
        self.collection = self._db.get_collection(setup.lamoda_collection)

    @classmethod
    async def bulk_save(cls, coats: list[dict]):
        """
        Bulk save coats to the database.

        Args:
            coats: List of coat dictionaries to be saved.
        """
        await cls().collection.insert_many(coats)

    @classmethod
    async def get_coat(cls, category: str, brand: str) -> Coat:
        """
        Retrieve a coat from the database.

        Args:
            category: Category of the coat.
            brand: Brand of the coat.

        Raises:
            ValidationError: If the retrieved coat does not pass validation.
        """
        coat = await cls().collection.find_one({"brand": brand, "category": category})
        await validate(coat=coat)
        coat.pop("_id", None)
        coat["created_at"] = coat["created_at"].isoformat()
        return coat

    @classmethod
    async def get_coats(cls, category: str, brand: str) -> List[Coat]:
        """
        Retrieve coats from the database.

        Args:
            category: Category of the coats.
            brand: Brand of the coats.

        Raises:
            ValidationError: If the retrieved coats do not pass validation.
        """
        coats = await cls().collection.find({"brand": brand, "category": category}).to_list(None)
        first_coat = coats[0] if coats else None
        await validate(coat=first_coat)
        for coat in coats:
            coat["created_at"] = coat["created_at"].isoformat()
            coat.pop("_id", None)
        return coats

    @classmethod
    async def remove_all_coats(cls):
        """
        Remove all coats from the database.
        """
        collection = cls().collection
        await collection.delete_many({})
