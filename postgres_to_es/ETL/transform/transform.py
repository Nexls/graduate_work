from abc import ABC, abstractmethod
from typing import Any, List, Coroutine, Dict, Union

from psycopg2.extras import DictCursor

from ..utils import coroutine
from ..movies import Movie, Genre, Person
from ..extract import ETLType


class BaseTransformer(ABC):
    """
    Базовый класс Transformer
    """
    @abstractmethod
    def transform(self) -> Coroutine[Any, None, None]:
        pass


class PostgresTransformer(BaseTransformer):
    """
    Реализация Postgres Transformer. Переопределяет абстрактную корутину, получающую данные в формате DictCursor,
    и возращает Dict для отправки на ES.
    """
    def _transform_list(self, data: List[DictCursor], class_obj: Union[Movie, Person, Genre]) -> List[dict]:
        return [class_obj(**raw_movie).to_json() for raw_movie in data]

    @coroutine
    def transform(self) -> Coroutine[List[Dict], None, None]:
        """
        Трансформирует список из DictCursor в документы для elasticsearch.
        :return:
        """
        raw = None
        while data := (yield raw):
            cls_ = Movie
            if data[0] == ETLType.GENRE.value:
                cls_ = Genre
            elif data[0] == ETLType.PERSON.value:
                cls_ = Person
            raw = self._transform_list(data[1], cls_)
