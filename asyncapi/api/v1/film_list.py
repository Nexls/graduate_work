from typing import List

from fastapi import APIRouter, Depends

from core import context_logger
from core.logger_route import LoggerRoute
from models.enumerations import QueryType
from models.film_response import FilmResponse
from schemas.film_list import FilmFilterRequest, FilmSearchRequest
from services.film import FilmService, get_film_service

logger = context_logger.get(__name__)

router = APIRouter(route_class=LoggerRoute)


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get(
    '/film',
    response_model=List[FilmResponse],
    summary='Список фильмов',
    description='Список фильмов, отсортированный по указанному полю, с фильтром по жанрам (если фильтр задан)',
    response_description='Название и рейтинг фильма'
)
async def film_list_with_filter(
    request: FilmFilterRequest = Depends(),
    film_list_service: FilmService = Depends(get_film_service)
) -> List[FilmResponse]:
    film_list = await film_list_service.get_by_query(
        body=dict(request.dict(exclude_none=True)),
        query_type=QueryType.FILTER
    )
    if not film_list:
        # вернем пустой список
        return []

    return film_list


@router.get(
    '/film/search',
    response_model=List[FilmResponse],
    summary='Поиск фильмов',
    description='Полнотекстовый поиск фильмов',
    response_description='Название и рейтинг фильма'
)
async def film_search(
    request: FilmSearchRequest = Depends(),
    film_list_service: FilmService = Depends(get_film_service)
) -> List[FilmResponse]:
    film_list = await film_list_service.get_by_query(
        body=dict(request.dict(exclude_none=True)),
        query_type=QueryType.SEARCH
    )
    if not film_list:
        # вернем пустой список
        return []

    return film_list
