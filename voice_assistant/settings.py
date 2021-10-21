import os

from environs import Env
# Применяем настройки логирования
from pythonjsonlogger import jsonlogger

# загружаем настройки из .env файла
env = Env()
env.read_env()

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = env('PROJECT_NAME', 'Голосовые помощники')

# Настройки Redis
REDIS_HOST = env('REDIS_HOST', '127.0.0.1')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_PASS = env('REDIS_PASSWORD', '')
REDIS_USE_SSL = env.bool('REDIS_USE_SSL', False)
REDIS_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

# Настройки Elasticsearch
ELASTIC_HOST = env('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = env.int('ELASTIC_PORT', 9200)
ELASTIC_USER = env('ELASTIC_USER')
ELASTIC_PASSWORD = env('ELASTIC_PASSWORD')
ELASTIC_USE_SSL = env.bool('ELASTIC_USE_SSL', False)
ELASTIC_INDEX_FILM = env('ELASTIC_INDEX_FILM', 'movies')
ELASTIC_INDEX_PERSON = env('ELASTIC_INDEX_PERSON', 'persons')
ELASTIC_INDEX_GENRE = env('ELASTIC_INDEX_GENRE', 'genres')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JWT_KEY_URL = env('JWT_KEY_URL', 'http://127.0.0.1:5000/public_key')
JWT_PUBLIC_KEY = env('JWT_PUBLIC_KEY', 'test')

SERVICE_URL = os.getenv('SERVICE_URL', 'http://127.0.0.1:8000/api/v1')

DEBUG = bool(os.getenv('DEBUG', False))
LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': lambda: jsonlogger.JsonFormatter(
                '%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s %(pathname)s %(lineno)s'),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'level': LOGGING_LEVEL
        },
    },
    'loggers': {
        '': {
            'handlers': ['debug_mode' if DEBUG else 'console'],
            'level': 'DEBUG'
        },
        'aiohttp.access': {
            'level': 'WARNING'
        }
    }
}
