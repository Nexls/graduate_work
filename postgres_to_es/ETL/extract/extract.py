import logging
from abc import ABC, abstractmethod
from typing import List, Generator

from psycopg2._psycopg import connection
from psycopg2.extras import DictCursor

from .postgres_components import Enricher, Producer, ETLType, Merger
from ..state import State


class BaseExtractor(ABC):
    """
    Базовый класс Extractor.
    """
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def extract_data(self) -> Generator[dict, None, None]:
        pass


class PostgresExtractor(BaseExtractor):
    """
    Реализация Postgres Extractor. Класс использует 3 смешанных класса для получения обновленных данных.
    """
    def __init__(self,
                 _type: ETLType,
                 state: State,
                 conn: connection,
                 limit: int = 100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producer = Producer(_type=_type, state=state, conn=conn, limit=limit)
        self.enricher = Enricher(_type=_type, state=state, conn=conn, limit=limit)
        self.merger = Merger(_type=_type, state=state, conn=conn, limit=limit)
        self.logger = logging.getLogger(f'{self.__class__.__name__}_{_type.value}')

    def extract_data(self) -> Generator[List[DictCursor], None, None]:
        """
        Гланвый метод класса Extract. Генерирует данные из заданного источника.
        :return:
        """
        merg = self.merger.merg()
        enrich = self.enricher.enrich(merg)
        self.logger.info('Extract is starting')
        yield from self.producer.generate_ids(enrich)
