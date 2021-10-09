import os
from environs import Env
from pathlib import Path

# загружаем настройки из .env файла
env = Env()
env.read_env()

# Настройки Redis
REDIS_HOST = env('REDIS_HOST', '127.0.0.1')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

# Настройки Elasticsearch
ELASTIC_HOST = env('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = env.int('ELASTIC_PORT', 9200)
ELASTIC_USER = env('ELASTIC_USER')
ELASTIC_PASSWORD = env('ELASTIC_PASSWORD')
ELASTIC_USE_SSL = env.bool('ELASTIC_USE_SSL', True)
ELASTIC_INDEX_FILM = env('ELASTIC_INDEX_FILM', 'test_movies')
ELASTIC_INDEX_PERSON = env('ELASTIC_INDEX_PERSON', 'test_persons')
ELASTIC_INDEX_GENRE = env('ELASTIC_INDEX_GENRE', 'test_genres')

# Корень проекта
BASE_DIR = Path(__file__).parent

# корневой URL
SERVICE_URL = os.getenv('SERVICE_URL', 'http://127.0.0.1:8000/api/v1')
