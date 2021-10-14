from typing import List

from fastapi import APIRouter, Depends, Request
from models.enumerations import QueryType
from models.film_response import FilmResponse
from services.film import FilmService, get_film_service

router = APIRouter()


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get(
    '/film',
    response_model=List[FilmResponse],
    summary='Список фильмов',
    description='Список фильмов, отсортированный по указанному полю, с фильтром по жанрам (если фильтр задан)',
    response_description='Название и рейтинг фильма'
)
async def film_list_with_filter(
    request: Request,
    film_list_service: FilmService = Depends(get_film_service)
) -> List[FilmResponse]:
    film_list = await film_list_service.get_by_query(
        body=dict(request.query_params),
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
    request: Request,
    film_list_service: FilmService = Depends(get_film_service)
) -> List[FilmResponse]:
    film_list = await film_list_service.get_by_query(
        body=dict(request.query_params),
        query_type=QueryType.SEARCH
    )
    if not film_list:
        # вернем пустой список
        return []

    return film_list
