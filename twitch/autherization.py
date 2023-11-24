import os

import aiohttp
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class Authorize:
    @classmethod
    async def get_auth_token(cls) -> str:
        """
        Get the authorization token for the Twitch API.

        Returns:
            The access token for authorization.

        Raises:
            aiohttp.ClientError: If there is an error while making the HTTP request.
        """
        url = "https://id.twitch.tv/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        parameters = {
            "client_id": f"{os.environ.get('CLIENT_ID')}",
            "client_secret": f"{os.environ.get('CLIENT_SECRET')}",
            "grant_type": "client_credentials",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=url, headers=headers, data=parameters
            ) as response:
                get_auth = await response.json()
        return get_auth["access_token"]
