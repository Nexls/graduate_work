from pydantic.main import BaseModel
import orjson
import uuid
from typing import List

from core.helpers import orjson_dumps


class PersonResponse(BaseModel):
    '''Информация о персонаже'''
    uuid: uuid.UUID
    full_name: str
    role: str
    film_ids: List[uuid.UUID] = []

    class Config:
        title = 'Person (full info)'
        json_loads = orjson.loads
        json_dumps = orjson_dumps
