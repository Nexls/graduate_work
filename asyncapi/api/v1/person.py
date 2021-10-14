from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from models.film_response import FilmResponse
from models.person_response import PersonResponse
from services.person import PersonService, get_person_service

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
    person_service: PersonService = Depends(get_person_service)
) -> ORJSONResponse:
    person, cached = await person_service.get_by_id(person_id)
    if not person:
        # Если пусто, отдаём 404 статус
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return ORJSONResponse(content=person.dict(), headers={'X-Cached': cached})


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
    person_service: PersonService = Depends(get_person_service)
) -> List[FilmResponse]:
    film_list = await person_service.get_films_by_person_id(person_id)
    if not film_list:
        # Если пусто, отдаём 404 статус
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='nothing found')

    return film_list
