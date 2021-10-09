from typing import List
import orjson
import uuid

from pydantic import BaseModel, validator
from core.helpers import orjson_dumps


class FilmRole(BaseModel):
    uuid: uuid.UUID
    role: str

    @validator('uuid', pre=True)
    def convert_to_uuid(cls, v):
        if isinstance(v, str):
            return uuid.UUID(v)
        return v

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(BaseModel):
    uuid: uuid.UUID
    full_name: str
    filmworks: List[FilmRole]

    @validator('uuid', pre=True)
    def convert_to_uuid(cls, v):
        if isinstance(v, str):
            return uuid.UUID(v)
        return v

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
