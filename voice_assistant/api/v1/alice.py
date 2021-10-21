from core import context_logger
from core.logger_route import LoggerRoute
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from services.alice_voice_assistant import get_alice_voice_assistant_service, AliceVoiceAssistantService
from starlette.requests import Request

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
    alice_service: AliceVoiceAssistantService = Depends(get_alice_voice_assistant_service)
) -> ORJSONResponse:
    res = await alice_service.parse_alice_request_and_routing(request=request)

    return ORJSONResponse(content=res)
