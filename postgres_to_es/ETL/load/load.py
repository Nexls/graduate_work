from abc import ABC, abstractmethod
from typing import Generator, Any, List, Coroutine, Optional, Union
import logging
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from ..extract import ETLType
from ..state import State
from ..utils import coroutine, backoff


class BaseLoader(ABC):
    @abstractmethod
    def load(self) -> Generator[Any, None, None]:
        pass


class ElasticLoader(BaseLoader):
    """
    Реализация Elastic Loader. Класс получает на вход настройки для подключения к серверу Elasticsearch.
    Для отправки данных исползуется метод bulk обернутый декоратором для повторных попыток при ошибках.
    """
    def __init__(self,
                 _type: ETLType,
                 state: State,
                 es_host: str,
                 es_port: Union[str, int],
                 index_name: str,
                 es_user: Optional[str] = None,
                 es_pass: Optional[str] = None):
        self.type = _type
        self.state = state
        self._auth = (es_user, es_pass) if es_user and es_pass else ('', '')
        self.es_client = Elasticsearch(hosts=es_host, port=es_port, http_auth=self._auth, use_ssl=True,
                                       verify_certs=False)
        self.index = index_name
        self.logger = logging.getLogger(f'{self.__class__.__name__}_{self.type.value}')

    @backoff()
    def _load_es(self, prepared_query: List[dict]):
        return helpers.bulk(self.es_client, prepared_query, stats_only=False)

    @coroutine
    def load(self) -> Coroutine[None, None, None]:
        """
        Отправка запроса в ES
        """
        while records := (yield):
            prepared_query = self._get_es_bulk_query(records, self.index)
            success_count, error_list = self._load_es(prepared_query)
            if success_count != len(records):
                for error in error_list:
                    self.logger.error('Error with:', error)
            else:
                self.logger.debug(f'Success load data - {len(records)} documents')

    def _get_es_bulk_query(self, rows: List[dict], index_name: str) -> List[dict]:
        """
        Подготавливает bulk-запрос в Elasticsearch
        """
        for row in rows:
            yield {'_id': row['uuid'], '_index': index_name, '_source': row}
