import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Searchable(BaseModel):
    """
    Model representing a searchable item.

    Attributes:
        category (str): The category of the item.
        brand (str): The brand of the item.
    """
    category: str
    brand: str


class Coat(Searchable):
    """
    Model representing a coat.

    Attributes:
        link (str): The link to the coat.
        price (Optional[Decimal]): The price of the coat.
        sale_price (Optional[Decimal]): The sale price of the coat.
        created_at (datetime.datetime): The datetime when the coat was created.
    """
    link: str
    price: Optional[Decimal] = Field(None)
    sale_price: Optional[Decimal] = Field(None)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
