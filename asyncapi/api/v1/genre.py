from http import HTTPStatus

from core import context_logger
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from models.genre import Genre
from services.genre import GenreService, get_genre_service
logger = context_logger.get(__name__)

router = APIRouter()


@router.get(
    '/genre/{genre_id}/',
    response_model=Genre,
    summary='Информация о жанре',
    response_description='Наименование жанра'
)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> ORJSONResponse:
    genre, cached = await genre_service.get_by_id(genre_id)
    if not genre:
        # Если пусто, отдаём 404 статус
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return ORJSONResponse(content=genre.dict(), headers={'X-Cached': cached})
