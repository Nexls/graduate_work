import orjson
import uuid

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel, validator, PrivateAttr
from typing import List, Optional

from core.helpers import orjson_dumps


class FilmGenre(BaseModel):
    """Жанр"""
    uuid: uuid.UUID
    name: str

    @validator('uuid', pre=True)
    def convert_to_uuid(cls, v):
        if isinstance(v, str):
            return uuid.UUID(v)
        return v

    class Config:
        title = 'Genre (for film info)'
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FilmPerson(BaseModel):
    """Участник фильма"""
    uuid: uuid.UUID
    full_name: str

    @validator('uuid', pre=True)
    def convert_to_uuid(cls, v):
        if isinstance(v, str):
            return uuid.UUID(v)
        return v

    class Config:
        title = 'Person (for film info)'
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Film(BaseModel):
    '''Полная информация о фильме'''
    uuid: uuid.UUID
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: List[FilmGenre] = []
    actors: List[FilmPerson] = []
    writers: List[FilmPerson] = []
    directors: List[FilmPerson] = []
    _permissions: int = PrivateAttr()

    # валидатор, т.к. elastic возвращает строку в ID
    @validator('uuid', pre=True)
    def convert_to_uuid(cls, v):
        if isinstance(v, str):
            return uuid.UUID(v)
        return v

    def __init__(self, permissions=0, **kwargs):
        super().__init__(**kwargs)
        self._permissions = permissions

    class Config:
        title = 'Film (full info)'
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
