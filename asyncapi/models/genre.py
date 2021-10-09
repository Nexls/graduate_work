import orjson
import uuid

from pydantic import BaseModel, validator
from core.helpers import orjson_dumps


class Genre(BaseModel):
    '''Иинформация о жанре'''
    uuid: uuid.UUID
    name: str

    @validator('uuid', pre=True)
    def convert_to_uuid(cls, v):
        if isinstance(v, str):
            return uuid.UUID(v)
        return v

    class Config:
        title = 'Genre'
        json_loads = orjson.loads
        json_dumps = orjson_dumps
