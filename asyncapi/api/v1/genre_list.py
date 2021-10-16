from typing import List

from fastapi import APIRouter, Depends, Request
from models.genre import Genre
from services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get(
    '/genre/',
    response_model=List[Genre],
    summary='Список жанров',
    response_description='Id и наименование жанра'
)
async def genre_list(
    request: Request,
    genre_list_service: GenreService = Depends(get_genre_service)
) -> List[Genre]:
    item_list = await genre_list_service.get_by_query(
        body=dict(request.query_params)
    )
    if not item_list:
        # вернем пустой список
        return []

    return item_list
