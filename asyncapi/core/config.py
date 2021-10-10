import os
from logging import config as logging_config
from environs import Env

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# загружаем настройки из .env файла
env = Env()
env.read_env()

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = env('PROJECT_NAME', 'API для онлайн-кинотеатра')

# Настройки Redis
REDIS_HOST = env('REDIS_HOST', '127.0.0.1')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_PASS = env('REDIS_PASSWORD', '')
REDIS_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

# Настройки Elasticsearch
ELASTIC_HOST = env('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = env.int('ELASTIC_PORT', 9200)
ELASTIC_USER = env('ELASTIC_USER')
ELASTIC_PASSWORD = env('ELASTIC_PASSWORD')
ELASTIC_USE_SSL = env.bool('ELASTIC_USE_SSL', True)
ELASTIC_INDEX_FILM = env('ELASTIC_INDEX_FILM', 'movies')
ELASTIC_INDEX_PERSON = env('ELASTIC_INDEX_PERSON', 'persons')
ELASTIC_INDEX_GENRE = env('ELASTIC_INDEX_GENRE', 'genres')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JWT_KEY_URL = env('JWT_KEY_URL', 'http://127.0.0.1:5000/public_key')
JWT_PUBLIC_KEY = env('JWT_PUBLIC_KEY', None)
