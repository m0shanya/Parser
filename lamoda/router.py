import time
from typing import Callable

from fastapi import APIRouter, Request, Response, Body
from fastapi.routing import APIRoute
from fastapi_cache.decorator import cache

from .parser import CoatParser
from .utils import get_response


class TimedRoute(APIRoute):
    """
    Custom APIRoute class that adds response time measurement to each route.

    This class extends the default APIRoute provided by FastAPI and overrides the `get_route_handler` method
    to add response time measurement to each route. The response time is added as a header in the response.

    Methods:
        get_route_handler: Returns the custom route handler function.
    """
    def get_route_handler(self) -> Callable:
        """
        Get the custom route handler function.
        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """
            Custom route handler function that measures response time.
            """
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            return response

        return custom_route_handler


lamoda_router = APIRouter(route_class=TimedRoute)


@lamoda_router.get('/parse/')
@cache(expire=3600)
async def parse() -> dict:
    """
    Parse coats data and return a success message.
    """
    await CoatParser().parse_coats()
    return {"ditail": "Success"}


@lamoda_router.post('/coat/')
@cache(expire=3600)
async def get_coat(data=Body()) -> Response:
    """
    Get a single coat based on the request data.
    """
    response = await get_response(many=False, request=data)
    return response


@lamoda_router.post('/coats/')
@cache(expire=3600)
async def get_coats(data=Body()) -> Response:
    """
    Get multiple coats based on the request data.
    """
    response = await get_response(many=True, request=data)
    return response
