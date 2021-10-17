from typing import List

from aiohttp import ClientSession
from core import context_logger
from core.logger_route import LoggerRoute
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from models.asyncapi.film_response import FilmResponse
from schemas.film_list import FilmFilterRequest, FilmSearchRequest
from settings import ASYNC_API_URL
from starlette.requests import Request

logger = context_logger.get(__name__)

router = APIRouter(route_class=LoggerRoute)


@router.get(
    '/film',
    response_model=List[FilmResponse],
    summary='Список фильмов',
    description='Список фильмов, отсортированный по указанному полю, с фильтром по жанрам (если фильтр задан)',
    response_description='Название и рейтинг фильма'
)
async def film_list_with_filter(
    request: Request,
    model: FilmFilterRequest = Depends(),
) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(url=ASYNC_API_URL + '/film', params=request.query_params, headers=request.headers) as resp:
        return ORJSONResponse(content=await resp.json())


@router.get(
    '/film/search',
    response_model=List[FilmResponse],
    summary='Поиск фильмов',
    description='Полнотекстовый поиск фильмов',
    response_description='Название и рейтинг фильма'
)
async def film_search(
    request: Request,
    model: FilmSearchRequest = Depends(),
) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=ASYNC_API_URL + '/film/search',
        params=request.query_params,
        headers=request.headers
    ) as resp:
        return ORJSONResponse(content=await resp.json())
