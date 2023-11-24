from typing import List

from ..models import Game, Stream, Streamer
from ..exceptions import validate_game, validate_streamer, validate_stream
from database import Mongo
from settings import get_config

setup = get_config()


class MongoClient:
    """MongoDB client for database operations."""

    _db = Mongo().get_database(setup.twitch_database)


class Saver(MongoClient):
    def __init__(self, collection: str):
        """MongoDB's collection for data in the specified collection."""
        self.collection = self._db.get_collection(collection)

    @classmethod
    async def bulk_save(cls, items: list[dict], collection_name: str):
        """
        Bulk save items to the specified collection in the database.

        Args:
            items: List of item dictionaries to be saved.
            collection_name: Name of the collection to save the items to.
        """
        await cls(collection=collection_name).collection.insert_many(items)

    @classmethod
    async def get_game(cls, name: str) -> Game:
        """
        Retrieve a game from the database.

        Args:
            name: Name of the game.

        Raises:
            ValidationError: If the retrieved game does not pass validation.
        """
        game = await cls(collection=setup.games_collection).collection.find_one(
            {"name": name}
        )
        await validate_game(name=game["name"])
        game.pop("_id", None)
        game["inserted_at"] = game["inserted_at"].isoformat()
        return game

    @classmethod
    async def get_streams(cls, user_name: str, game_name: str) -> List[Stream]:
        """
        Retrieve streams from the database.

        Args:
            user_name: Name of the user associated with the streams.
            game_name: Name of the game associated with the streams.

        Raises:
            ValidationError: If the retrieved streams do not pass validation.
        """
        streams = (
            await cls(collection=setup.streams_collection)
            .collection.find({"user_name": user_name, "game_name": game_name})
            .to_list(None)
        )
        first_stream = streams[0] if streams else None
        await validate_stream(stream=first_stream)
        for stream in streams:
            stream.pop("_id", None)
            stream["inserted_at"] = stream["inserted_at"].isoformat()
        return streams

    @classmethod
    async def get_streamer(cls, login: str) -> Streamer:
        """
        Retrieve a streamer from the database.

        Args:
            login: Login of the streamer.

        Returns:
            The retrieved streamer.

        Raises:
            ValidationError: If the retrieved streamer does not pass validation.
        """
        streamer = await cls(collection=setup.streamers_collection).collection.find_one(
            {"login": login}
        )
        await validate_streamer(login=streamer.login)
        streamer.pop("_id", None)
        streamer["inserted_at"] = streamer["inserted_at"].isoformat()
        return streamer

    @classmethod
    async def remove_all(cls, collection_name: str):
        """
        Remove all items from the specified collection in the database.

        Args:
            collection_name: Name of the collection to remove items from.
        """
        collection = cls(collection=collection_name).collection
        await collection.delete_many({})
