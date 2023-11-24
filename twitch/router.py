import json
from typing import Literal

from starlette import status
from starlette.responses import JSONResponse
from fastapi_cache.decorator import cache

from lamoda.router import TimedRoute
from fastapi import APIRouter, BackgroundTasks, Response, Request
from .parser import TwitchParser
from .exceptions import validate_game, validate_stream, validate_streamer
from .dao.connector import Saver

twitch_router = APIRouter(route_class=TimedRoute)


@twitch_router.get("/parse/")
@cache(expire=3600)
async def parser(
    parse_case: Literal["games", "streams", "streamers"],
    background_task: BackgroundTasks,
) -> JSONResponse:
    match parse_case:
        case "games":
            background_task.add_task(TwitchParser().parse_games)
        case "streams":
            background_task.add_task(TwitchParser().parse_streams)
        case "streamers":
            background_task.add_task(TwitchParser().parse_streamers)

    return JSONResponse({"detail": "success"})


@twitch_router.post("/get_game/")
@cache(expire=3600)
async def get_game(game_data: Request) -> Response:
    data = await game_data.json()
    try:
        game = await validate_game(name=data["name"])
        response = await Saver.get_game(name=game.name)
        return Response(
            content=json.dumps({"detail": response}),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except KeyError:
        return Response(
            content=json.dumps({"detail": "KeyError. Check the data that you send."}),
            status_code=status.HTTP_400_BAD_REQUEST,
            media_type="application/json",
        )


@twitch_router.post("/get_streams/")
@cache(expire=3600)
async def get_streams(stream_data: Request) -> Response:
    data = await stream_data.json()
    try:
        streams_set = await validate_stream(
            user_name=data["user_name"], game_name=data["game_name"]
        )
        response = await Saver.get_streams(
            user_name=streams_set.user_name, game_name=streams_set.game_name
        )
        return Response(
            content=json.dumps({"detail": response}),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except KeyError:
        return Response(
            content=json.dumps({"detail": "KeyError. Check the data that you send."}),
            status_code=status.HTTP_400_BAD_REQUEST,
            media_type="application/json",
        )


@twitch_router.post("/get_streamer/")
@cache(expire=3600)
async def get_streamer(streamer_data: Request) -> Response:
    data = await streamer_data.json()
    try:
        streamer = await validate_streamer(login=data["login"])
        response = await Saver.get_streamer(login=streamer.login)
        return Response(
            content=json.dumps({"detail": response}),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except KeyError:
        return Response(
            content=json.dumps({"detail": "KeyError. Check the data that you send."}),
            status_code=status.HTTP_400_BAD_REQUEST,
            media_type="application/json",
        )
