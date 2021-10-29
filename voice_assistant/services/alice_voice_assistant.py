import logging
from functools import lru_cache
from typing import Any

from aiohttp import ClientSession
from starlette.requests import Request

from alice_work_files.request import AliceRequest
from alice_work_files.scenes import DEFAULT_SCENE, SCENES
from alice_work_files.state import STATE_REQUEST_KEY
from core import context_logger

logger = context_logger.get(__name__)
logging.getLogger('elasticsearch').propagate = False


class AliceVoiceAssistantService():
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    async def parse_alice_request_and_routing(self, request: Request) -> dict[str, Any]:
        """
        Entry-point for Serverless Function.
        :param event: request payload.
        :param context: information about current execution context.
        :return: response to be serialized as JSON.
        """
        event = await request.json()

        request = AliceRequest(event)
        current_scene_id = event.get('state', {}).get(STATE_REQUEST_KEY, {}).get('scene')

        if current_scene_id is None:
            return await DEFAULT_SCENE().reply(request)

        current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
        next_scene = current_scene.move(request)

        if next_scene is not None:
            return await next_scene.reply(request)
        else:
            return await current_scene.fallback(request)


@lru_cache()
def get_alice_voice_assistant_service(
) -> AliceVoiceAssistantService:
    return AliceVoiceAssistantService()
