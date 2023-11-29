from .models import Game, SearchableStreamer, SearchableStream


async def game_validate(**data) -> Game:
    """
    Validate and create a Game object with the provided data.
    """
    return Game(**data)


async def stream_validate(**data) -> SearchableStream:
    """
    Validate and create a SearchableStream object with the provided data.
    """
    return SearchableStream(**data)


async def streamer_validate(**data) -> SearchableStreamer:
    """
    Validate and create a SearchableStreamer object with the provided data.
    """
    return SearchableStreamer(**data)
