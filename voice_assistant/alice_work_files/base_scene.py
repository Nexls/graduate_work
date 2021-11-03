from abc import ABC, abstractmethod
from typing import Optional

from alice_work_files.request import AliceRequest
from alice_work_files.response_helpers import button
from alice_work_files.state import STATE_RESPONSE_KEY
from core import context_logger
from settings import ASYNC_API_URL

logger = context_logger.get(__name__)


class Scene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    # генерация ответа сцены
    @abstractmethod
    async def reply(self, request):
        ...

    # проверка перехода к новой сцене
    def move(self, request: AliceRequest):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    def handle_global_intents(self, request: AliceRequest):
        ...

    async def handle_local_intents(self, request: AliceRequest) -> Optional[str]:
        ...

    async def fallback(self, request: AliceRequest):
        text = 'Не понимаю. Попробуй сформулировать иначе'

        logger.error(f'incomprehensible intent: {request.original_utterance}')

        return await self.make_response(text, buttons=[
            button('Что ты умеешь?', hide=True)
        ])

    async def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None):
        if not text:
            text = ('К сожалению, по твоему запросу ничего не нашлось. '
                    'Попробуй спросить что-нибудь еще!')
        elif len(text) > 1024:
            text = text[:1024]
        if tts is None:
            tts = text.replace('\n', ', ')

        response = {
            'text': text,
            'tts': tts,
        }

        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        if directives is not None:
            response['directives'] = directives

        webhook_response = {
            'response': response,
            'version': '1.0',
            STATE_RESPONSE_KEY: {
                'scene': self.id(),
            },
        }
        if state is not None:
            webhook_response[STATE_RESPONSE_KEY].update(state)
        return webhook_response

    async def get_request(
            self,
            request: AliceRequest,
            path: str,
            filter_type: str = None,
            filter_genre: str = None,
            query: str = None,
            sort: str = None,
            page_size: int = 3
    ):

        url = f'{ASYNC_API_URL}/{path}'

        if filter_type:
            url += f'?filter_type={filter_type}&page_size={page_size}'
        if filter_genre:
            url += f'?filter_genre={filter_genre}&page_size={page_size}'
        if query:
            url += f'?query={query}&page_size={page_size}'
        if sort:
            url += f'&sort={sort}'

        async with request.session.get(url=url) as resp:
            return await resp.json()
