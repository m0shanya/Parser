from .models import Searchable


async def coat_validate(**data) -> Searchable:
    """
    Validate and create a Searchable object with the provided data.
    """
    return Searchable(**data)
