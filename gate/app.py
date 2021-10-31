import logging

import aioredis
import api.v1 as api
import settings
from aiohttp import ClientSession
from core import context_logger
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from security.limiter import FastAPILimiter
from security.security import init_jwt_public_key

logging.config.dictConfig(settings.LOGGING)
logger = context_logger.get(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/docs/',
    openapi_url='/api/docs.json',
    default_response_class=ORJSONResponse,
    version='1.0.0',
)


@app.on_event('startup')
async def startup():
    app.state.jwt_public_key = await init_jwt_public_key()
    app.state.session = ClientSession()
    redis = aioredis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASS if settings.REDIS_PASS else None,
        ssl=settings.REDIS_USE_SSL,
        ssl_cert_reqs='none',
    )
    await FastAPILimiter.init(redis)


@app.on_event('shutdown')
async def shutdown():
    await app.state.session.close()

app.include_router(api.asyncapi.film_list.router, prefix='/api/v1', tags=['AsyncAPI'])
app.include_router(api.asyncapi.film.router, prefix='/api/v1', tags=['AsyncAPI'])
app.include_router(api.asyncapi.person_list.router, prefix='/api/v1', tags=['AsyncAPI'])
app.include_router(api.asyncapi.person.router, prefix='/api/v1', tags=['AsyncAPI'])
app.include_router(api.asyncapi.genre.router, prefix='/api/v1', tags=['AsyncAPI'])
app.include_router(api.asyncapi.genre_list.router, prefix='/api/v1', tags=['AsyncAPI'])

app.include_router(api.authapi.routes.router, prefix='/api/v1', tags=['AuthAPI'])

app.include_router(api.voice_assistant.voices_assistants.router, prefix='/api/v1', tags=['Voice Assistants'])
