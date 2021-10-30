from aiohttp import ClientSession
from security.limiter import RateLimiter

from core import context_logger
from core.logger_route import LoggerRoute
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from settings import VOICE_ASSISTANT_URL
from starlette.requests import Request

logger = context_logger.get(__name__)

router = APIRouter(route_class=LoggerRoute)


@router.post(
    '/alice',
    summary='Webhook для Алисы',
    description='Обрабатывает запросы от Алисы',
    dependencies=[Depends(RateLimiter(times=1000, seconds=60 * 60))]
)
async def alice(request: Request) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.post(
        url=VOICE_ASSISTANT_URL + '/alice',
        params=request.query_params,
        headers=request.headers
    ) as resp:

        return ORJSONResponse(content=await resp.json())
