from fastapi import APIRouter, Depends, Request
from typing import List

from services.person import PersonService, get_person_service
from models.person_response import PersonResponse
from models.enumerations import QueryType

router = APIRouter()


@router.get('/person/search',
            response_model=List[PersonResponse],
            summary='Поиск по персонажам',
            description='Полнотекстовый поиск участников фильмов',
            response_description='ФИО персонажа, его роль и список фильмов'
            )
async def person_details(request: Request, person_list_service: PersonService = Depends(get_person_service)) -> List[PersonResponse]:

    item_list = await person_list_service.get_by_query(
        body=dict(request.query_params),
        query_type=QueryType.SEARCH
    )
    if not item_list:
        # вернём пустой список
        return []

    return item_list
