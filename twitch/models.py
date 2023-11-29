import datetime
from typing import List

from pydantic import BaseModel, Field


class Base(BaseModel):
    inserted_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class SearchableStream(Base):
    user_name: str
    game_name: str


class SearchableStreamer(Base):
    login: str


class Game(Base):
    name: str


class Stream(SearchableStream):
    user_login: str
    title: str
    tags: List[str]
    started_at: str


class Streamer(SearchableStreamer):
    display_name: str
    description: str
    created_at: str
