import os
from logging import config as logging_config

from environs import Env
# загружаем настройки из .env файла
from pythonjsonlogger import jsonlogger

env = Env()
env.read_env()
LIMIT_PER_PAGE = 50
# Название проекта. Используется в Swagger-документации
PROJECT_NAME = env('PROJECT_NAME', 'API для онлайн-кинотеатра')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Настройки Redis
REDIS_HOST = env('REDIS_HOST', '127.0.0.1')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_PASS = env('REDIS_PASSWORD', '')
REDIS_USE_SSL = env.bool('REDIS_USE_SSL', False)

JWT_KEY_URL = env('JWT_KEY_URL', 'http://localhost:8002/public_key')
JWT_PUBLIC_KEY = env('JWT_PUBLIC_KEY', None)

ASYNC_API_HOST = env('ASYNC_API_HOST', 'localhost')
ASYNC_API_PORT = env('ASYNC_API_PORT', '8001')
ASYNC_API_URL = f'http://{ASYNC_API_HOST}:{ASYNC_API_PORT}/api/v1'

AUTH_API_HOST = env('AUTH_API_HOST', '0.0.0.0')
AUTH_API_PORT = env('AUTH_API_PORT', '8002')
AUTH_API_URL = f'http://{AUTH_API_HOST}:{AUTH_API_PORT}'

VOICE_ASSISTANT_HOST = env('VOICE_ASSISTANT_HOST', '0.0.0.0')
VOICE_ASSISTANT_PORT = env('VOICE_ASSISTANT_PORT', '8003')
VOICE_ASSISTANT_URL = f'http://{VOICE_ASSISTANT_HOST}:{VOICE_ASSISTANT_PORT}/api/v1'

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DEFAULT_HANDLERS = ['console', ]

# В логгере настраивается логгирование uvicorn-сервера.
# Про логирование в Python можно прочитать в документации
# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html

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

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)
