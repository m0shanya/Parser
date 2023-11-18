from fastapi.exceptions import HTTPException
from pydantic import ValidationError

from lamoda.models import Searchable
from .validators import coat_validate


async def validate(**data) -> Searchable:
    """
    Validate the input data and return a validated Searchable object.

    This function takes in keyword arguments as data and validates the "brand" and "category" values.
    If the validation is successful, a Searchable object is returned with the validated values.
    If the validation fails, appropriate HTTPExceptions are raised.

    Raises:
        HTTPException: If the input data fails validation or is missing required keys.
    """
    response = None
    try:
        response = await coat_validate(
            brand=data["brand"],
            category=data["category"]
        )
    except ValidationError:
        raise HTTPException(status_code=400, detail="Brand and Category must be a string!")
    except KeyError:
        if "coat" in data.keys():
            if data["coat"] is None:
                raise HTTPException(status_code=404, detail="No such data matching")
        else:
            raise HTTPException(status_code=400, detail="KeyError. Check the data that you send.")

    return response
