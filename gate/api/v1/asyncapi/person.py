from typing import List

from aiohttp import ClientSession
from core import context_logger
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from models.asyncapi.film_response import FilmResponse
from models.asyncapi.person_response import PersonResponse
from settings import ASYNC_API_URL
from starlette.requests import Request

logger = context_logger.get(__name__)

router = APIRouter()


@router.get(
    '/person/{person_id}/',
    response_model=PersonResponse,
    summary='Информация о персонаже',
    description='Информация об участнике фильма',
    response_description='ФИО, роли в фильмах, список фильмов'
)
async def person_details(
    person_id: str,
    request: Request,
) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=ASYNC_API_URL + f'/person/{person_id}/',
        params=request.query_params,
        headers=request.headers
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.get(
    '/person/{person_id}/film/',
    response_model=List[FilmResponse],
    summary='Список фильмов конкретного персонажа',
    description='Список фильмов с участием конкретного персонажа',
    response_description='Список фильмов: название и рейтинг',
    deprecated=True
)
async def person_films(
    person_id: str,
    request: Request,
) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=ASYNC_API_URL + f'/person/{person_id}/film/',
        params=request.query_params,
        headers=request.headers
    ) as resp:
        return ORJSONResponse(content=await resp.json())
