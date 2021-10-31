import os

from environs import Env
# Применяем настройки логирования
from pythonjsonlogger import jsonlogger

# загружаем настройки из .env файла
env = Env()
env.read_env()

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = env('PROJECT_NAME', 'Голосовые помощники')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASYNC_API_HOST = env('ASYNC_API_HOST', 'localhost')
ASYNC_API_PORT = env('ASYNC_API_PORT', '8001')
ASYNC_API_URL = f'http://{ASYNC_API_HOST}:{ASYNC_API_PORT}/api/v1'

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
