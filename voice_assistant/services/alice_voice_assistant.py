import logging
from functools import lru_cache
from typing import Any

from core import context_logger
from services.voice_assistant_base import VoiceAssistantServiceBase
from starlette.requests import Request

logger = context_logger.get(__name__)
logging.getLogger('elasticsearch').propagate = False


class AliceVoiceAssistantService(VoiceAssistantServiceBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    async def parse_alice_request_and_routing(self, request: Request) -> dict[str, Any]:
        # some logics
        # ...
        return await self.get_top_films(request)

    async def get_top_films(self, request: Request) -> dict[str, Any]:
        ...


@lru_cache()
def get_alice_voice_assistant_service(
) -> AliceVoiceAssistantService:
    return AliceVoiceAssistantService()
