from fastapi.exceptions import HTTPException
from pydantic import ValidationError

from twitch.models import Game, SearchableStream, SearchableStreamer
from .validators import game_validate, stream_validate, streamer_validate


async def validate_game(**data) -> Game:
    """
    Validate the input data and return a validated Game object.

    This function takes in keyword arguments as data and validates the "name" value.
    If the validation is successful, a Game object is returned with the validated values.
    If the validation fails, appropriate HTTPExceptions are raised.

    Raises:
        HTTPException: If the input data fails validation or is missing required keys.
    """
    try:
        response = await game_validate(
            name=data["name"],
        )
    except ValidationError:
        raise HTTPException(status_code=400, detail="Name must be a string!")

    return response


async def validate_stream(**data) -> SearchableStream:
    """
    Validate the input data and return a validated SearchableStream object.

    This function takes in keyword arguments as data and validates the "user_name" and "game_name" values.
    If the validation is successful, a SearchableStream object is returned with the validated values.
    If the validation fails, appropriate HTTPExceptions are raised.

    Raises:
        HTTPException: If the input data fails validation or is missing required keys.
    """
    response = None
    try:
        response = await stream_validate(
            user_name=data["user_name"], game_name=data["game_name"]
        )
    except ValidationError:
        raise HTTPException(status_code=400, detail="Parameters must be a string!")
    except KeyError:
        if "stream" in data.keys():
            if data["stream"] is None:
                raise HTTPException(status_code=404, detail="No such data matching")
        else:
            raise HTTPException(
                status_code=400, detail="KeyError. Check the data that you send."
            )

    return response


async def validate_streamer(**data) -> SearchableStreamer:
    """
    Validate the input data and return a validated SearchableStreamer object.

    This function takes in keyword arguments as data and validates the "login" value.
    If the validation is successful, a SearchableStreamer object is returned with the validated values.
    If the validation fails, appropriate HTTPExceptions are raised.

    Raises:
        HTTPException: If the input data fails validation or is missing required keys.
    """
    try:
        response = await streamer_validate(login=data["login"])
    except ValidationError:
        raise HTTPException(status_code=400, detail="Login must be a string!")

    return response
