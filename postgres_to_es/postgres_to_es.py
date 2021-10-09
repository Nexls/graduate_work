import logging
import os
import sys

import urllib3
from redis import Redis

from ETL import PostgresElasticsearchETL, State, ETLType, RedisStorage
from ETL.utils import backoff

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(name)s %(funcName)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(os.path.basename(sys.argv[0]).replace('.py', ''))
logging.getLogger('elasticsearch').propagate = False
logging.getLogger('urllib3.connectionpool').propagate = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@backoff()
def get_redis_conn(
    redis_host: str,
    redis_port: int,
    redis_pass: str
) -> Redis:
    return Redis(host=redis_host, port=redis_port, password=redis_pass)


if __name__ == '__main__':
    ps_db = os.environ.get('POSTGRES_DB')
    ps_user = os.environ.get('POSTGRES_USER')
    ps_pass = os.environ.get('POSTGRES_PASSWORD')
    ps_host = os.environ.get('POSTGRES_HOST')
    ps_port = os.environ.get('POSTGRES_PORT')
    es_host = os.environ.get('ELASTIC_HOST')
    es_port = os.environ.get('ELASTIC_PORT')
    es_user = os.environ.get('ELASTIC_USER')
    es_pass = os.environ.get('ELASTIC_PASSWORD')
    index_name = os.environ.get('ELASTIC_INDEX')
    redis_host = os.environ.get('REDIS_HOST')
    redis_port = int(os.environ.get('REDIS_PORT'))
    redis_pass = os.environ.get('REDIS_PASSWORD')

    redis_conn = get_redis_conn(redis_host, redis_port, redis_pass)
    state = State(RedisStorage(redis_conn))
    for _type in ETLType:
        try:
            etl = PostgresElasticsearchETL(
                _type=_type,
                state=state,
                postgres_host=ps_host,
                postgres_db=ps_db,
                postgres_user=ps_user,
                postgres_pass=ps_pass,
                postgres_port=ps_port,
                es_host=es_host,
                es_port=es_port,
                es_user=es_user,
                es_pass=es_pass,
                index_name=index_name,
            )
            etl.process()
        except Exception as exc:
            logger.error(f'Error with {_type}: {exc}')
