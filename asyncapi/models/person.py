from typing import List, Optional
import orjson
import uuid

from pydantic import BaseModel, validator
from core.helpers import orjson_dumps


class FilmRole(BaseModel):
    uuid: Optional[uuid.UUID]
    role: Optional[str]

    @validator('uuid', pre=True)
    def convert_to_uuid(cls, v):
        if isinstance(v, str):
            try:
                v = uuid.UUID(v)
            except:
                v = None
        return v

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(BaseModel):
    uuid: uuid.UUID
    full_name: str
    filmworks: List[FilmRole]

    @validator('uuid', pre=True)
    def convert_to_uuid(cls, v) -> uuid.UUID:
        if isinstance(v, str):
            return uuid.UUID(v)
        return v

    @validator('filmworks')
    def filter_empty_roles(cls, v: list[FilmRole]) -> list[FilmRole]:
        res = []
        for film_role in v:
            if None in [film_role.uuid, film_role.role]:
                continue
            res.append(film_role)
        return res

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
