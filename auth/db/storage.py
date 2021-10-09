from redis import Redis
import abc
from typing import Optional, Union, Awaitable, Iterable
from settings import REDIS_DB, REDIS_HOST, REDIS_PORT, REDIS_PASS


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def set(self, key: str, value: str, expire=None) -> Optional[Awaitable]:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def get(self, key: str) -> Union[str, Awaitable]:
        """Загрузить состояние локально из постоянного хранилища"""
        pass

    @abc.abstractmethod
    def get_many_key_by_pattern(self, key: str) -> Iterable:
        """Получить все ключи по паттерну"""
        pass

    @abc.abstractmethod
    def delete(self, key: str) -> None:
        """Удалить ключ из хранилища"""
        pass


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def set(self, key: str, value: str, expire: Optional[int] = None) -> None:
        if expire is not None:
            self.redis_adapter.setex(key, expire, value)
        else:
            self.redis_adapter.set(key, value)

    def get(self, key: str) -> str:
        raw_data = self.redis_adapter.get(key)
        return raw_data

    def get_many_key_by_pattern(self, search_key: str) -> Iterable:
        for key in self.redis_adapter.scan_iter(search_key):
            yield key

    def delete(self, key: str) -> None:
        self.redis_adapter.delete(key)


jwt_storage = RedisStorage(redis_adapter=Redis(host=REDIS_HOST,
                                               port=REDIS_PORT,
                                               password=REDIS_PASS,
                                               db=REDIS_DB))
