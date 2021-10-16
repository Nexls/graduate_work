from typing import List

from fastapi import APIRouter, Depends, Request
from models.enumerations import QueryType
from models.person_response import PersonResponse
from schemas.person_list import PersonSearchRequest
from services.person import PersonService, get_person_service

router = APIRouter()


@router.get(
    '/person/search',
    response_model=List[PersonResponse],
    summary='Поиск по персонажам',
    description='Полнотекстовый поиск участников фильмов',
    response_description='ФИО персонажа, его роль и список фильмов'
)
async def person_details(
    request: PersonSearchRequest = Depends(),
    person_list_service: PersonService = Depends(get_person_service)
) -> List[PersonResponse]:
    item_list = await person_list_service.get_by_query(
        body=dict(request.dict(exclude_none=True)),
        query_type=QueryType.SEARCH
    )
    if not item_list:
        # вернём пустой список
        return []

    return item_list
