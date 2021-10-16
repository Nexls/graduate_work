from elasticsearch import AsyncElasticsearch
import abc
from typing import Optional, Awaitable, Union, List

es: Optional[AsyncElasticsearch] = None


class BaseDatabaseClient(abc.ABC):
    @abc.abstractmethod
    def get(self, search_path: str, id: str) -> Union[str, dict, Awaitable[dict]]:
        """Загрузить состояние локально из постоянного хранилища"""
        pass

    @abc.abstractmethod
    def search(self, index: str, body: Optional[dict] = None, size: int = None) -> Union[List[dict], Awaitable]:
        pass

    @abc.abstractmethod
    def mget(self, index: str, body: Optional[dict] = None) -> Union[List[dict], Awaitable]:
        pass


class EsDatabaseClient(BaseDatabaseClient):
    def __init__(self, es_client: AsyncElasticsearch):
        self.es_client = es_client

    async def get(self, search_path: str, doc_id: str) -> str:
        raw_data = await self.es_client.get(search_path, doc_id)
        return raw_data['_source']

    async def search(self, index: str, body: Optional[dict] = None,
                     size: int = None) -> Union[List[dict], Awaitable]:
        results = await self.es_client.search(index=index, body=body, size=size)
        return [doc['_source'] for doc in results['hits']['hits']]

    async def mget(self, index: str, body: Optional[dict] = None) -> Union[List[dict], Awaitable]:
        results = await self.es_client.mget(body=body, index=index)
        return [doc['_source'] for doc in results['docs']]


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> EsDatabaseClient:
    return EsDatabaseClient(es)
