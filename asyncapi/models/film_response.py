import orjson
import uuid
from typing import Optional

from pydantic import BaseModel
from core.helpers import orjson_dumps


class FilmResponse(BaseModel):
    '''Краткая информация о фильме'''
    uuid: uuid.UUID
    title: str
    imdb_rating: Optional[float]

    class Config:
        title = 'Film (short info)'
        json_loads = orjson.loads
        json_dumps = orjson_dumps
