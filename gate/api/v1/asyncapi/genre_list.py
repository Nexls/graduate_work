from typing import List

from aiohttp import ClientSession
from core import context_logger
from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse
from models.asyncapi.genre import Genre
from settings import ASYNC_API_URL

logger = context_logger.get(__name__)

router = APIRouter()


@router.get(
    '/genre/',
    response_model=List[Genre],
    summary='Список жанров',
    response_description='Id и наименование жанра'
)
async def genre_list(
    request: Request,
) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=ASYNC_API_URL + f'/genre/',
        params=request.query_params,
        headers=request.headers
    ) as resp:
        return ORJSONResponse(content=await resp.json())
