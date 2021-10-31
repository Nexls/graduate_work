import collections

from core import context_logger
from core.logger_route import LoggerRoute
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from services.alice_voice_assistant import get_alice_voice_assistant_service, AliceVoiceAssistantService
from starlette.requests import Request
from typing import Awaitable

logger = context_logger.get(__name__)

router = APIRouter(route_class=LoggerRoute)


# Внедряем FilmService с помощью Depends(get_film_service)
@router.post(
    '/alice',
    summary='Webhook для Алисы',
    description='Обрабатывает запросы от Алисы',
)
async def film_details(
    request: Request,
    alice_service: Awaitable[AliceVoiceAssistantService] = Depends(get_alice_voice_assistant_service)
) -> ORJSONResponse:
    if isinstance(alice_service, collections.Awaitable):
        alice_service = await alice_service
    res = await alice_service.parse_request_and_routing(request=request)

    return ORJSONResponse(content=res)
