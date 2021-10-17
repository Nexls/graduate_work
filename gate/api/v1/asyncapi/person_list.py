from typing import List

from aiohttp import ClientSession
from core import context_logger
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from models.asyncapi.person_response import PersonResponse
from schemas.person_list import PersonSearchRequest
from settings import ASYNC_API_URL
from starlette.requests import Request

logger = context_logger.get(__name__)

router = APIRouter()


@router.get(
    '/person/search',
    response_model=List[PersonResponse],
    summary='Поиск по персонажам',
    description='Полнотекстовый поиск участников фильмов',
    response_description='ФИО персонажа, его роль и список фильмов'
)
async def person_details(
    request: Request,
    model: PersonSearchRequest = Depends(),
) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=ASYNC_API_URL + f'/person/search',
        params=request.query_params,
        headers=request.headers
    ) as resp:
        return ORJSONResponse(content=await resp.json())
