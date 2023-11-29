import requests
import pytest

from settings import get_config
from ..autherization import Authorize

setup = get_config()


@pytest.mark.asyncio
@pytest.fixture
async def get_token():
    return await Authorize.get_auth_token()


@pytest.mark.asyncio
@pytest.fixture
async def get_headers(get_token):
    token = await get_token
    headers = {
        "Client-ID": f"{setup.client_id}",
        "Authorization": f"Bearer {token}"
    }
    return headers


class TestTwitch:
    @pytest.mark.asyncio
    async def test_games_api(self, get_headers):
        url = setup.twitch_url + setup.games_url
        headers = await get_headers
        response = requests.get(url, headers=headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_streams_api(self, get_headers):
        url = setup.twitch_url + setup.streams_url
        headers = await get_headers
        response = requests.get(url, headers=headers)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_streamers_api(self, get_headers):
        url = setup.twitch_url + setup.streams_url
        headers = await get_headers
        params = {"first": 1}
        response = requests.get(url, headers=headers, params=params)
        assert response.status_code == 200

        data = response.json()
        streamers = data.get("data", [])[0]
        user_url = setup.twitch_url + setup.streamers_url
        user_params = {"id": str(streamers["user_id"])}
        user_response = requests.get(user_url, headers=headers, params=user_params)
        assert user_response.status_code == 200
