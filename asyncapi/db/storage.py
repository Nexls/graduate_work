from aioredis import Redis
import abc
from typing import Optional, Union, Awaitable

redis: Optional[Redis] = None


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def set(self, key: str, value: str, expire=None) -> Optional[Awaitable]:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def get(self, key: str) -> Union[str, Awaitable]:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    async def set(self, key: str, value: str, expire=None) -> None:
        await self.redis_adapter.set(key, value, expire=expire)

    async def get(self, key: str) -> str:
        raw_data = await self.redis_adapter.get(key)
        return raw_data


# Функция понадобится при внедрении зависимостей
async def get_redis() -> RedisStorage:
    return RedisStorage(redis_adapter=redis)
