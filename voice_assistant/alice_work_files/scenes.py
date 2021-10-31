import inspect
import sys
from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable, Optional

import ujson

from alice_work_files import intents
from alice_work_files.intents import FILM_INFO_INTENTS, PERSON_INFO_INTENTS, TOP_FILM_INTENTS
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
        if intents.HELP in request.intents:
            return Helper()
        if set(request.intents) & set(TOP_FILM_INTENTS):
            return TopFilms()
        if set(request.intents) & set(FILM_INFO_INTENTS):
            return FilmInfo()
        if set(request.intents) & set(PERSON_INFO_INTENTS):
            return PersonInfo()

    @abstractmethod
    async def handle_local_intents(self, request: AliceRequest) -> Optional[str]:
        ...

    async def fallback(self, request: AliceRequest):
        text = 'Не понимаю. Попробуй сформулировать иначе'

        logger.error(f'incomprehensible intent: {request.original_utterance}')

        return await self.make_response(text, buttons=[
            button('Что ты умеешь?', hide=True)
        ])

    async def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None):
        if tts is None:
            tts = text.replace('\n', ' ')

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


class Welcome(Scene):
    async def reply(self, request: AliceRequest):
        text = 'Привет! Cпроси меня о мире кино!'
        return await self.make_response(text, buttons=[
            button('Топ фильмов', hide=True),
            button('Что ты умеешь?', hide=True)
        ])

    def handle_local_intents(self, request: AliceRequest):
        return self.handle_global_intents(request)


class TopFilms(Scene):

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        intents_dict = {
            intents.TOP_BY_TYPE: self.top_by_type,
            intents.TOP_BY_GENRE: self.top_by_genre,
            intents.TOP_BY_RELEASE_DATE: self.top_by_release_date,
        }
        return intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]  # TODO: filtering most relevant intent
        handler = self.intents_handler[intent]
        return await handler(request)

    async def top_by_type(self, request: AliceRequest):
        filter_type = request.slots.get('MediaType', '')

        async with request.session.get(
                url=(f'{ASYNC_API_URL}/film?'
                     f'sort=-imdb_rating&page_size=3&filter_type={filter_type}')
        ) as resp:
            resp_json = await resp.json()

        film_list = [film['title'] for film in resp_json]

        text = ujson.dumps('\n'.join(film_list))
        return await self.make_response(text)

    async def top_by_genre(self, request: AliceRequest):
        filter_genre = request.slots.get('GenreType', '')

        async with request.session.get(
                url=(f'{ASYNC_API_URL}/film?'
                     f'sort=-imdb_rating&page_size=3&filter_genre={filter_genre}')
        ) as resp:
            resp_json = await resp.json()

        film_list = [film['title'] for film in resp_json]

        text = ujson.dumps('\n'.join(film_list))
        return await self.make_response(text)

    async def top_by_release_date(self, request: AliceRequest):
        filter_release_date = request.slots.get('ReleaseDate', '')

        async with request.session.get(
                url=(f'{ASYNC_API_URL}/film?'
                     f'sort=-imdb_rating&page_size=3&filter_release_date={filter_release_date}')
        ) as resp:
            resp_json = await resp.json()

        film_list = [film['title'] for film in resp_json]

        text = ujson.dumps('\n'.join(film_list))
        return await self.make_response(text)

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(TOP_FILM_INTENTS):
            return self


class Helper(Scene):
    async def reply(self, request):
        text = ('Я могу показать лучшие фильмы этой недели.\n'
                'Или, например, сказать кто снял фильм.\n'
                'А еще могу посоветовать фильмы с твоим любимым актером.')
        return await self.make_response(text, buttons=[
            button('Покажи топ фильмов', hide=True),
            button('Покажи лучшие комедии', hide=True),
            button('Кто автор фильма Дюна?', hide=True),
            button('В каких фильмах снимался Джейсон Стэтхем?', hide=True),
            button('Что ты умеешь?', hide=True)
        ])

    def handle_local_intents(self, request: AliceRequest):
        pass


class FilmInfo(Scene):
    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        intents_dict = {
            intents.FILM_ACTORS: self.film_actors,
            intents.FILM_AUTHOR: self.film_author,
            intents.FILM_GENRE: self.film_genre,
            intents.FILM_RATING: self.film_rating,
            intents.FILM_DURATION: self.film_duration,
            intents.FILM_RELEASE_DATE: self.film_release_date,
            intents.FILM_DESCRIPTION: self.film_description,
        }
        return intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]   # TODO: filtering most relevant intent
        handler = self.intents_handler[intent]
        return await handler(request)

    async def _get_film_id(self, request: AliceRequest):
        # film_name = request.slots.get('YANDEX.STRING', '')

        # для теста
        film_name = 'дюна'

        async with request.session.get(
                url=(f'{ASYNC_API_URL}/film/search?'
                     f'sort=-imdb_rating&page_size=1&query={film_name}')
        ) as resp:
            resp_json = await resp.json()

        film_id = resp_json[0]['uuid']

        return film_id

    async def film_author(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/film/{film_id}'
        ) as resp:
            resp_json = await resp.json()

        film_writers = [writer['full_name'] for writer in resp_json['writers']]

        text = ujson.dumps('\n'.join(film_writers))
        return await self.make_response(text)

    async def film_actors(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/film/{film_id}'
        ) as resp:
            resp_json = await resp.json()

        film_actors = [actor['full_name'] for actor in resp_json['actors']]

        text = ujson.dumps('\n'.join(film_actors))
        return await self.make_response(text)

    async def film_description(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/film/{film_id}') as resp:
            resp_json = await resp.json()

        film_description = resp_json[0]['description']
        return await self.make_response(film_description)

    async def film_duration(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/film/{film_id}'
        ) as resp:
            resp_json = await resp.json()

        # film_duration = resp_json[0]['duration']
        return await self.make_response(f'Пока нет информации о длительности фильма')

    async def film_genre(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/film/{film_id}'
        ) as resp:
            resp_json = await resp.json()

        film_genres = [genre['name'] for genre in resp_json['genre']]

        text = ujson.dumps('\n'.join(film_genres))
        return await self.make_response(text)

    async def film_rating(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/film/{film_id}'
        ) as resp:
            resp_json = await resp.json()

        film_rating = resp_json[0]['imdb_rating']
        return await self.make_response(f'Рейтинг фильма - {film_rating}')

    async def film_release_date(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/film/{film_id}') as resp:
            resp_json = await resp.json()

        # film_release_date = resp_json[0]['release_date']
        return await self.make_response(f'Пока нет информации о дате выхода фильма')

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(FILM_INFO_INTENTS):
            return self


class PersonInfo(Scene):
    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        intents_dict = {
            intents.PERSON_AGE: self.person_age,
            intents.PERSON_FILMS: self.person_films,
            intents.PERSON_BIOGRAPHY: self.person_biography,
        }
        return intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]  # TODO: filtering most relevant intent
        handler = self.intents_handler[intent]
        return await handler(request)

    async def _get_person_id(self, request: AliceRequest):
        # person_name = request.slots.get('YANDEX.STRING', '')

        # для теста
        person_name = 'алиса'

        async with request.session.get(
                url=(f'{ASYNC_API_URL}/film/search?'
                     f'sort=-imdb_rating&page_size=1&query={person_name}')
        ) as resp:
            resp_json = await resp.json()

        person_id = resp_json[0]['uuid']

        return person_id

    async def person_age(self, request: AliceRequest):
        person_id = self._get_person_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/person/{person_id}'
        ) as resp:
            resp_json = await resp.json()

        person_birth_date = resp_json[0]['birth_date']
        return await self.make_response(person_birth_date)

    async def person_films(self, request: AliceRequest):
        person_id = self._get_person_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/person/{person_id}'
        ) as resp:
            resp_json = await resp.json()

        person_film_ids = [film['uuid'] for film in resp_json['filmworks']]

        text = ujson.dumps('\n'.join(person_film_ids))
        return await self.make_response(text)

    async def person_biography(self, request: AliceRequest):
        person_id = self._get_person_id(request)

        async with request.session.get(
                url=f'{ASYNC_API_URL}/person/{person_id}'
        ) as resp:
            resp_json = await resp.json()

        # person_biography = resp_json[0]['biography']
        return await self.make_response('Пока нет информации о биографии этого человека')

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(PERSON_INFO_INTENTS):
            return self


def _list_scenes():
    current_module = sys.modules[__name__]
    scenes = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scene):
            scenes.append(obj)
    return scenes


SCENES = {
    scene.id(): scene for scene in _list_scenes()
}
DEFAULT_SCENE = Welcome
