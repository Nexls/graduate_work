import logging
import os
from time import sleep

from dotenv import load_dotenv

from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)


class ElasticWaiter:
    def __init__(self, elastic_conn_dict: dict):
        '''
        Создает экземпляр класса Elasticsearch
        вне зависимости от фактического наличия соединения
        '''
        self.elastic = Elasticsearch(hosts=[elastic_conn_dict, ])

    def test_til_success(self) -> None:
        '''Тестируем пока не получим подряд 3 ответа о доступности'''
        success_attempts = 3
        while success_attempts > 0:
            response = self.elastic.ping()
            if response:
                logger.warning('Connect to Elastic established')
                success_attempts -= 1
            else:
                success_attempts = 3
                logger.warning('No response from elastic, trying more...')
            sleep(1)


if __name__ == '__main__':
    # загружаем настройки из .env файла
    load_dotenv()

    # logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.ERROR)

    elastic_conn_dict = {'host': os.getenv('ELASTIC_HOST', '127.0.0.1'), 'port': int(os.getenv('ELASTIC_PORT', 9200))}
    ElasticWaiter(elastic_conn_dict).test_til_success()
