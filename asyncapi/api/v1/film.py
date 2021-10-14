from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from models.film import Film
from security.security import jwt_permissions_required
from services.film import FilmService, get_film_service

router = APIRouter()


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get(
    '/film/{film_id}/',
    response_model=Film,
    summary='Информация о фильме',
    description='Детальная информация о фильме',
    response_description='Название, рейтинг, описание фильма и список участников'
)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> ORJSONResponse:
    film, cached = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return ORJSONResponse(content=film.dict(), headers={'X-Cached': cached})


@router.get(
    '/security_films/',
    response_model=List[Film],
    summary='Иинформация о фильмах с доступами',
    description='Детальная информация о фильмах с доступом',
    response_description='Просмотреть список фильмов с различным доступом'
)
@jwt_permissions_required(response_model=List[Film])
async def security_films():
    res = [
        Film(**{
            "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": "Movie with permissions 0: other",
            "imdb_rating": 0,
            "description": "Фильм с общим доступом всем",
            "genre": [],
            "actors": [],
            "writers": [],
            "directors": []}),
        Film(**{
            "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
            "title": "Movie with permissions 1: user",
            "imdb_rating": 0,
            "description": "Фильм с общим доступом для авторизованных пользователей",
            "genre": [],
            "actors": [],
            "writers": [],
            "directors": [],
            "permissions": 1
        }),
        Film(**{
            "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
            "title": "Movie with permissions 2: paying user",
            "imdb_rating": 0,
            "description": "Фильм с общим доступом для авторизованных платящих пользователей",
            "genre": [],
            "actors": [],
            "writers": [],
            "directors": [],
            "permissions": 2
        }),
        Film(**{
            "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa9",
            "title": "Movie with permissions 3: admin",
            "imdb_rating": 0,
            "description": "Фильм с общим доступом для админов",
            "genre": [],
            "actors": [],
            "writers": [],
            "directors": [],
            "permissions": 3
        }),
    ]
    return res
