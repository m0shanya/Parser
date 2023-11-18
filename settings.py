import os
from typing import Any

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv())


class Setup(BaseSettings):
    """
    Configuration settings for the application.
    """
    lamoda_prefix: str = "/lamoda"
    cache_prefix: str = "fastapi-cache"

    mongodb_url: Any = os.environ.get("MONGO_URL")
    redis_url: Any = os.environ.get("REDIS_URL")

    lamoda_database: str = "lamoda"
    lamoda_collection: str = "coats"

    lamoda_url: str = os.environ.get("LAMODA_URL")
    lamoda_url_target: str = os.environ.get("LAMODA_URL_TARGET")
    pages: int = os.environ.get("LAMODA_PAGES")

    grid: str = "x-product-card__card"
    card_brand: str = "x-product-card-description__brand-name"
    category_name: str = "x-product-card-description__product-name"

    single_price_from_card: str = "x-product-card-description__price-single"
    old_price_from_card: str = "x-product-card-description__price-old"
    new_price_from_card: str = "x-product-card-description__price-new"


def get_config() -> Setup:
    """
     Retrieve the configuration settings.

     Returns:
         Setup: An instance of the Setup class with the configuration settings.
     """
    return Setup()
