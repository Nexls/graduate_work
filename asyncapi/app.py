import aioredis
from api.v1 import film, film_list, person_list, person, genre, genre_list
import settings
from db import db_client, storage
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from security.security import init_jwt_public_key

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/docs/',
    openapi_url='/api/docs.json',
    default_response_class=ORJSONResponse,
    version='1.0.0',
)


@app.on_event('startup')
async def startup():
    await init_jwt_public_key()
    storage.redis = await aioredis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASS if settings.REDIS_PASS else None,
        ssl=settings.REDIS_USE_SSL,
        ssl_cert_reqs="none",
    )
    db_client.es = AsyncElasticsearch(
        hosts=[f'{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'],
        http_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD),
        use_ssl=settings.ELASTIC_USE_SSL,
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
