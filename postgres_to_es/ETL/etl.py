import logging
from abc import ABC, abstractmethod
from datetime import datetime

from psycopg2 import connect
from psycopg2._psycopg import connection
from psycopg2.extras import register_uuid

from .extract import ETLType, PostgresExtractor
from .transform import PostgresTransformer
from .load import ElasticLoader
from .state import State
from .utils import backoff


class BaseETL(ABC):
    """
    Базовый класс ETL
    """
    @abstractmethod
    def process(self) -> None:
        pass


class PostgresElasticsearchETL(ABC):
    """
    Реализация Postgres Elasticsearch ETL.
    Класс получает все необходимые настройки для подключения к БД (Postgres) и отправки на ES.
    """
    def __init__(self,
                 _type: ETLType,
                 state: State,
                 postgres_host: str,
                 postgres_port: str,
                 postgres_user: str,
                 postgres_pass: str,
                 postgres_db: str,
                 es_host: str,
                 es_port: str,
                 es_user: str,
                 es_pass: str,
                 index_name: str,
                 ):
        self.type = _type
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.postgres_user = postgres_user
        self.postgres_pass = postgres_pass
        self.postgres_db = postgres_db
        self.es_host = es_host
        self.es_port = es_port
        self.es_user = es_user
        self.es_pass = es_pass
        self.index_name = index_name
        self.state = state
        self.logger = logging.getLogger(f'{self.__class__.__name__}_{self.type.value}')

    @backoff()
    def _connect_to_postgres(self) -> connection:
        """
        Получение объекта connection для PostgresSQL с ретраем в виде backoff.
        :return:
        """
        dsl = {'dbname': self.postgres_db,
               'user': self.postgres_user,
               'password': self.postgres_pass,
               'host': self.postgres_host,
               'port': self.postgres_port}
        return connect(**dsl)

    def process(self) -> None:
        """
        Основной процесс работы ETL.
        1. Подключаемся к БД. Подключение обернуто в декоратор с установленным количеством попыток по времени.
        2. Выкачиваем данные с помощью Extract класса.
        3. Трансформируем данные под нашу вторую БД. В данном случае Elasticsearch - документоориентированный подход.
        4. Загружаем данные в ES с помощью метода load(). Внутри также используем backoff для попыток.
        5. Закрываем подключение к БД и в state заносим актуальную дату обновления.
        :return:
        """
        register_uuid()
        self.logger.info('Connect to PostgresSQL server...')
        pg_conn = self._connect_to_postgres()
        self.logger.info('Success connection to PostgresSQL server!')
        try:
            ps_extract = PostgresExtractor(_type=self.type, state=self.state, conn=pg_conn)
            ps_transform = PostgresTransformer()
            es_loader = ElasticLoader(_type=self.type, state=self.state,
                                      es_host=self.es_host, es_port=self.es_port, index_name=self.index_name,
                                      es_user=self.es_user, es_pass=self.es_pass)
            for rows in ps_extract.extract_data():
                es_loader.index = rows[0] if rows[0] == 'movies' else f'{rows[0]}s'
                transform_dict = ps_transform.transform().send(rows)
                es_loader.load().send(transform_dict)
            self.state.set_state(f'{self.type.value}_modified', datetime.now().strftime('%Y-%m-%d'))
            self.logger.info(f'Success {self.type} loading!')
        except Exception as exc:
            raise exc
        finally:
            pg_conn.close()
