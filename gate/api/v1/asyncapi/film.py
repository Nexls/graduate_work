from typing import List

from aiohttp import ClientSession
from core import context_logger
from core.logger_route import LoggerRoute
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from models.asyncapi.film import Film
from security.security import jwt_permissions_required
from settings import ASYNC_API_URL
from starlette.requests import Request

logger = context_logger.get(__name__)

router = APIRouter(route_class=LoggerRoute)


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get(
    '/film/{film_id}/',
    response_model=Film,
    summary='Информация о фильме',
    description='Детальная информация о фильме',
    response_description='Название, рейтинг, описание фильма и список участников'
)
async def film_details(film_id: str, request: Request) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=ASYNC_API_URL + f'/film/{film_id}/',
        params=request.query_params,
        headers=request.headers
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.get(
    '/security_films/',
    response_model=List[Film],
    summary='Иинформация о фильмах с доступами',
    description='Детальная информация о фильмах с доступом',
    response_description='Просмотреть список фильмов с различным доступом'
)
@jwt_permissions_required(response_model=List[Film])
async def security_films(request: Request) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=ASYNC_API_URL + f'/security_films/',
        params=request.query_params,
        headers=request.headers
    ) as resp:
        return await resp.json()
