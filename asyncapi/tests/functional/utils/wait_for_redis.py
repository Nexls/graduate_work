import logging
import os
from time import sleep

import redis
from backoff import backoff
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class RedisWaiter:
    def __init__(self, host: str, port: int):
        self.redis = redis.Redis(host=host, port=port, db=0)

    @backoff()
    def test_redis_conn(self) -> bool:
        '''Создает соединение с Redis'''
        response = self.redis.ping()
        if not response:
            return False
        return True

    def test_til_success(self) -> None:
        '''Тестируем пока не получим подряд 3 ответа о доступности'''
        success_attempts = 3
        while success_attempts > 0:
            response = self.test_redis_conn()
            if response:
                logger.warning('Connect to Redis established')
                success_attempts -= 1
            else:
                success_attempts = 3
                logger.warning('No response from Redis, trying more...')
                sleep(1)


if __name__ == '__main__':
    # загружаем настройки из .env файла
    load_dotenv()

    # logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.ERROR)

    RedisWaiter(host=os.getenv('REDIS_HOST', '127.0.0.1'),
                port=int(os.getenv('REDIS_PORT', 6379))
                ).test_til_success()
