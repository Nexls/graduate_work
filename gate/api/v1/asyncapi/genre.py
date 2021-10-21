from aiohttp import ClientSession
from core import context_logger
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from models.asyncapi.genre import Genre
from settings import ASYNC_API_URL
from starlette.requests import Request

logger = context_logger.get(__name__)

router = APIRouter()


@router.get(
    '/genre/{genre_id}/',
    response_model=Genre,
    summary='Информация о жанре',
    response_description='Наименование жанра'
)
async def genre_details(
    request: Request,
    genre_id: str,
) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=ASYNC_API_URL + f'/genre/{genre_id}/',
        params=request.query_params,
        headers=request.headers
    ) as resp:
        return ORJSONResponse(content=await resp.json())
