import logging

import settings
from aiohttp import ClientSession
from api.v1 import alice
from core import context_logger
from core.session import get_session
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

logging.config.dictConfig(settings.LOGGING)
logger = context_logger.get(__name__)
logging.getLogger('elasticsearch').propagate = False

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/docs/',
    openapi_url='/api/docs.json',
    default_response_class=ORJSONResponse,
    version='1.0.0',
)


@app.on_event('startup')
async def startup():
    app.state.session = await get_session()


@app.on_event('shutdown')
async def shutdown():
    session: ClientSession = app.state.session
    await session.close()


app.include_router(alice.router, prefix='/api/v1', tags=['Алиса'])
