import requests

from typing import List, Any
from copy import deepcopy
from .models import Game, Stream, Streamer
from .dao.connector import Saver
from settings import get_config
from .autherization import Authorize
from broker import KafkaWorker

setup = get_config()


class TwitchParser(Authorize):
    def __init__(self):
        self._token = None
        self._headers = None

    async def token(self) -> str:
        """
        Get the authorization token for Twitch API.

        Returns:
            The access token for authorization.

        Raises:
            aiohttp.ClientError: If there is an error while making the HTTP request.
        """
        if self._token is None:
            self._token = await self.get_auth_token()
        return self._token

    async def headers(self, token) -> dict:
        """
        Get the headers for Twitch API requests.

        Args:
            token (str): The access token for authorization.

        Returns:
            The headers dictionary containing Client-ID and Authorization.

        Raises:
            aiohttp.ClientError: If there is an error while making the HTTP request.
        """
        if self._headers is None:
            self._headers = {
                "Client-ID": f"{setup.client_id}",
                "Authorization": f"Bearer {token}",
            }
        return self._headers

    async def _get_base_params(self) -> dict:
        """
        Get the base parameters for Twitch API requests.

        Returns:
            The dictionary containing token, headers, and params.

        Raises:
            aiohttp.ClientError: If there is an error while making the HTTP request.
        """
        token = await self.token()
        headers = await self.headers(token)
        params = {"first": 100}  # The maximum number of streams per request

        return {"token": token, "headers": headers, "params": params}

    async def _parse_games(self):
        """
        Parse games data from Twitch API and save it to the database.
        """
        url = setup.twitch_url + setup.games_url

        request_params = await self._get_base_params()
        params = deepcopy(request_params["params"])

        all_games = []

        while True:
            response = requests.get(
                url, headers=request_params["headers"], params=params
            )
            data = response.json()

            if "error" in data:
                print("Error:", data["error"])
                break

            games = data.get("data", [])

            if not games:
                break

            all_games.extend([Game(name=game["name"]) for game in games])

            cursor = data.get("pagination", {}).get("cursor")
            if not cursor:
                break

            params[
                "after"
            ] = cursor  # Paginate through the results until all streams are fetched

        await self._insert_data(data=all_games, collection_name=setup.games_collection)

    async def _parse_streams(self):
        """
        Parse streams data from Twitch API and save it to the database.
        """
        url = setup.twitch_url + setup.streams_url

        request_params = await self._get_base_params()
        params = deepcopy(request_params["params"])
        params["game_id"] = str(setup.target_game_id)

        all_streams = []

        while True:
            response = requests.get(
                url, headers=request_params["headers"], params=params
            )
            data = response.json()

            if "error" in data:
                print("Error:", data["error"])
                break

            streams = data.get("data", [])

            if not streams:
                break

            all_streams.extend(
                [
                    Stream(
                        user_login=stream["user_login"],
                        user_name=stream["user_name"],
                        game_name=stream["game_name"],
                        title=stream["title"],
                        tags=stream["tags"] if stream["tags"] is not None else ["-"],
                        started_at=stream["started_at"],
                    )
                    for stream in streams
                ]
            )

            cursor = data.get("pagination", {}).get("cursor")
            if not cursor:
                break

            params[
                "after"
            ] = cursor  # Paginate through the results until all streams are fetched

        await self._insert_data(
            data=all_streams, collection_name=setup.streams_collection
        )

    async def _parse_streamers_id(self):
        """
        Parse streamers' IDs from Twitch API and send them to Kafka for further processing.
        """
        url = setup.twitch_url + setup.streams_url
        request_params = await self._get_base_params()
        params = deepcopy(request_params["params"])
        params["game_id"] = str(setup.target_game_id)

        while True:
            all_streamers_for_parse = []
            response = requests.get(
                url, headers=request_params["headers"], params=params
            )
            data = response.json()

            if "error" in data:
                print("Error:", data["error"])
                break

            streamers = data.get("data", [])

            if not streamers:
                break

            all_streamers_for_parse.extend(
                [str(stream["user_id"]) for stream in streamers]
            )
            await KafkaWorker().producing(
                topic="topic_for_users", data=all_streamers_for_parse
            )

            cursor = data.get("pagination", {}).get("cursor")
            if not cursor:
                break

            params[
                "after"
            ] = cursor  # Paginate through the results until all streams are fetched

    @staticmethod
    async def _clear_collection(collection_name: str):
        """
        Clear the specified collection in the database.

        Args:
            collection_name (str): The name of the collection to be cleared.

        Raises:
            aiohttp.ClientError: If there is an error while making the HTTP request.
        """
        await Saver.remove_all(collection_name=collection_name)

    @classmethod
    async def _insert_data(cls, data: List[Any], collection_name: str):
        """
        Insert data into the specified collection in the database.

        Args:
            data (List[Any]): The data to be inserted.
            collection_name (str): The name of the collection to insert the data into.

        Raises:
            aiohttp.ClientError: If there is an error while making the HTTP request.
        """
        await cls._clear_collection(collection_name=collection_name)
        all_items = [item.dict() for item in data]
        await Saver.bulk_save(all_items, collection_name)

    async def _parse_streamer(self, user_id: int):
        """
        Parse streamer data from Twitch API and save it to the database.

        Args:
            user_id (int): The ID of the streamer.

        Raises:
            aiohttp.ClientError: If there is an error while making the HTTP request.
        """
        user_url = setup.twitch_url + setup.streamers_url
        request_params = await self._get_base_params()
        user_params = deepcopy(request_params["params"])
        user_params["id"] = str(user_id)
        user_response = requests.get(
            user_url, headers=request_params["headers"], params=user_params
        )
        users = user_response.json()
        user_info = users.get("data", [])[0]
        streamer = Streamer(
            login=user_info["login"],
            display_name=user_info["display_name"],
            description=user_info["description"],
            created_at=user_info["created_at"],
        )
        all_items = [item.dict() for item in [streamer]]
        await Saver.bulk_save(all_items, setup.streamers_collection)

    async def parse_games(self):
        """
        Parse games data from Twitch API.
        """
        await self._parse_games()

    async def parse_streams(self):
        """
        Parse streams data from Twitch API.
        """
        await self._parse_streams()

    async def parse_streamers(self):
        """
        Parse streamers' IDs from Twitch API and send them to Kafka.
        """
        await self._parse_streamers_id()

    async def parse_streamer(self, user_id: int):
        """
        Parse streamer data from Twitch API.

        Args:
            user_id (int): The ID of the streamer.
        """
        await self._parse_streamer(user_id)
