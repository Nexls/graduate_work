from enum import Enum


class QueryType(Enum):
    FILTER = 1
    SEARCH = 2


class ItemType(Enum):
    FILM = 1
    PERSON = 2
    GENRE = 3
