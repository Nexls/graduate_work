import logging
import ssl

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import film, film_list, person_list, person, genre, genre_list
from core import config
from core.logger import LOGGING
from db import db_client, storage
from security.security import init_jwt_public_key

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/docs/',
    openapi_url='/api/docs.json',
    default_response_class=ORJSONResponse,
    version='1.0.0',
)


@app.on_event('startup')
async def startup():
    await init_jwt_public_key()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    storage.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT),
        password=config.REDIS_PASS,
        minsize=10,
        maxsize=20,
        ssl=ctx,
    )
    db_client.es = AsyncElasticsearch(
        hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'],
        http_auth=(config.ELASTIC_USER, config.ELASTIC_PASSWORD),
        use_ssl=config.ELASTIC_USE_SSL,
        verify_certs=False
    )


@app.on_event('shutdown')
async def shutdown():
    await storage.redis.close()
    await db_client.es.close()


# Подключаем роутер к серверу, указав префикс /v1/film
# Теги указываем для удобства навигации по документации
# !Порядок следования имеет значение!
# /api/v1/film/search - это должно уходить в первый маршрутизатор
# иначе он рассматривается как /api/v1/film/<uuid:UUID>
app.include_router(film_list.router, prefix='/api/v1', tags=['Фильмы'])
app.include_router(film.router, prefix='/api/v1', tags=['Фильмы'])
app.include_router(person_list.router, prefix='/api/v1', tags=['Люди'])
app.include_router(person.router, prefix='/api/v1', tags=['Люди'])
app.include_router(genre.router, prefix='/api/v1', tags=['Жанры'])
app.include_router(genre_list.router, prefix='/api/v1', tags=['Жанры'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )
