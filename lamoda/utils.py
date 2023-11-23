import json
from _decimal import Decimal
from typing import Any

from fastapi import Response
from bson import Decimal128
from starlette import status

from lamoda.dao.connector import MongoSaver
from lamoda.exeptions import validate


def json_encoder(obj: Any) -> str:
    """
    Custom JSON encoder function.

    This function is used as the default argument for the `default` parameter of `json.dumps()`.
    It handles serialization of `Decimal128` objects by converting them to strings.
    """
    if isinstance(obj, Decimal128):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def to_decimal128(price: Decimal) -> Decimal128:
    """
    Convert a Decimal object to Decimal128.
    """
    price_in_128 = Decimal128(str(price))
    return price_in_128


async def get_response(many: bool, request: dict) -> Response:
    """
    Get the response based on the request data.

    Args:
        many (bool): A flag indicating whether to retrieve multiple coats or a single coat.
        request (dict): The request data containing the category and brand.

    Raises:
        KeyError: If the required keys are not present in the request data.
    """
    try:
        coat = await validate(category=request["category"], brand=request["brand"])
        response = await MongoSaver.get_coat(brand=coat.brand, category=coat.category)
        if many:
            response = await MongoSaver.get_coats(brand=coat.brand, category=coat.category)
        return Response(content=json.dumps({"detail": response}, default=json_encoder),
                        status_code=status.HTTP_200_OK,
                        media_type="application/json")
    except KeyError:
        return Response(content=json.dumps({"detail": "KeyError. Check the data that you send."}),
                        status_code=status.HTTP_400_BAD_REQUEST,
                        media_type="application/json")
