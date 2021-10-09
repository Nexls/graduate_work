import abc
import json
from typing import Optional

from redis import Redis


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        try:
            with open(self.file_path, 'w') as f:
                json.dump(state, f)
        except BaseException as exc:
            raise exc

    def retrieve_state(self) -> dict:
        data = {}
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.save_state({})
        finally:
            return data


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def save_state(self, state: dict) -> None:
        self.redis_adapter.set('data', json.dumps(state))

    def retrieve_state(self) -> dict:
        raw_data = self.redis_adapter.get('data')
        if raw_data is None:
            return {}
        return json.loads(raw_data)
