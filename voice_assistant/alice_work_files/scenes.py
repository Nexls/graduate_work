import inspect
import sys
from typing import Any, Awaitable, Callable

import json

from alice_work_files import intents
from alice_work_files.base_scene import Scene
from alice_work_files.intents import FILM_INFO_INTENTS, PERSON_INFO_INTENTS, TOP_FILM_INTENTS
from alice_work_files.request import AliceRequest
from alice_work_files.response_helpers import button
from core import context_logger

logger = context_logger.get(__name__)


# подкласс, чтобы избежать circular import
class GlobalScene(Scene):
    def handle_global_intents(self, request: AliceRequest):
        intents_set = set(request.intents)
        if intents.HELP in request.intents:
            return Helper()
        if intents_set & set(TOP_FILM_INTENTS):
            return TopFilms()
        if intents_set & set(FILM_INFO_INTENTS):
            return FilmInfo()
        if intents_set & set(PERSON_INFO_INTENTS):
            return PersonInfo()


class Welcome(GlobalScene):
    async def reply(self, request: AliceRequest):
        text = 'Привет! Cпроси меня о мире кино!'
        return await self.make_response(text, buttons=[
            button('Топ фильмов', hide=True),
            button('Что ты умеешь?', hide=True)
        ])

    def handle_local_intents(self, request: AliceRequest):
        return self.handle_global_intents(request)


class TopFilms(GlobalScene):
    def __init__(self):
        self.intents_dict = {
            intents.TOP_BY_TYPE: self.top_by_type,
            intents.TOP_BY_GENRE: self.top_by_genre,
            intents.TOP_BY_RELEASE_DATE: self.top_by_release_date,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]  # TODO: filtering most relevant intent
        handler = self.intents_handler[intent]
        return await handler(request)

    async def top_by_type(self, request: AliceRequest):
        filter_type = request.slots.get('type', '')

        resp_json = await self.get_request(
            request,
            path='film',
            filter_type=filter_type,
            sort='-imdb_rating'
        )

        film_list = (film['title'] for film in resp_json)

        text = '\n'.join(film_list)
        return await self.make_response(text)

    async def top_by_genre(self, request: AliceRequest):
        filter_type = request.slots.get('type', '')

        resp_json = await self.get_request(
            request,
            path='film',
            filter_type=filter_type,
            sort='-imdb_rating'
        )

        film_list = (film['title'] for film in resp_json)

        text = '\n'.join(film_list)
        return await self.make_response(text)

    async def top_by_release_date(self, request: AliceRequest):
        filter_type = request.slots.get('period', '')

        resp_json = await self.get_request(
            request,
            path='film',
            filter_type=filter_type,
            sort='-imdb_rating'
        )

        film_list = (film['title'] for film in resp_json)

        text = '\n'.join(film_list)
        return await self.make_response(text)

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(TOP_FILM_INTENTS):
            return self


class Helper(GlobalScene):
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


class FilmInfo(GlobalScene):
    def __init__(self):
        self.intents_dict = {
            intents.FILM_ACTORS: self.film_actors,
            intents.FILM_AUTHOR: self.film_author,
            intents.FILM_GENRE: self.film_genre,
            intents.FILM_RATING: self.film_rating,
            intents.FILM_DURATION: self.film_duration,
            intents.FILM_RELEASE_DATE: self.film_release_date,
            intents.FILM_DESCRIPTION: self.film_description,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]   # TODO: filtering most relevant intent
        handler = self.intents_handler[intent]
        return await handler(request)

    async def _get_film_id(self, request: AliceRequest):
        film_name = request.slots.get('film_name', '')

        resp_json = await self.get_request(request, path='film/search', query=film_name)

        return resp_json[0]['uuid']

    async def film_author(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        resp_json = await self.get_request(request, path=f'film/{film_id}')

        film_writers = (writer['full_name'] for writer in resp_json['writers'])

        text = '\n'.join(film_writers)
        return await self.make_response(text)

    async def film_actors(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        resp_json = await self.get_request(request, path=f'film/{film_id}')

        film_actors = (actor['full_name'] for actor in resp_json['actors'])

        text = '\n'.join(film_actors)
        return await self.make_response(text)

    async def film_description(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        resp_json = await self.get_request(request, path=f'film/{film_id}')

        film_description = resp_json[0]['description']
        return await self.make_response(film_description)

    async def film_duration(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        resp_json = await self.get_request(request, path=f'film/{film_id}')

        # film_duration = resp_json[0]['duration']
        return await self.make_response(f'Пока нет информации о длительности фильма')

    async def film_genre(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        resp_json = await self.get_request(request, path=f'film/{film_id}')

        film_genres = (genre['name'] for genre in resp_json['genre'])

        text = '\n'.join(film_genres)
        return await self.make_response(text)

    async def film_rating(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        resp_json = await self.get_request(request, path=f'film/{film_id}')

        film_rating = resp_json[0]['imdb_rating']
        return await self.make_response(f'Рейтинг фильма - {film_rating}')

    async def film_release_date(self, request: AliceRequest):
        film_id = await self._get_film_id(request)

        resp_json = await self.get_request(request, path=f'film/{film_id}')

        film_release_date = resp_json[0]['release_date']
        return await self.make_response(f'Дата выхода фильма - {film_release_date}')

    def handle_local_intents(self, request: AliceRequest):
        if set(request.intents) & set(FILM_INFO_INTENTS):
            return self


class PersonInfo(GlobalScene):
    def __init__(self):
        self.intents_dict = {
            intents.PERSON_AGE: self.person_age,
            intents.PERSON_FILMS: self.person_films,
            intents.PERSON_BIOGRAPHY: self.person_biography,
        }

    @property
    def intents_handler(self) -> dict[str, Callable[[AliceRequest], Awaitable]]:
        return self.intents_dict

    async def reply(self, request: AliceRequest) -> dict[str, Any]:
        intent = list(request.intents.keys())[0]  # TODO: filtering most relevant intent
        handler = self.intents_handler[intent]
        return await handler(request)

    async def _get_person_id(self, request: AliceRequest):
        person_name = request.slots.get('film_name', '')

        resp_json = await self.get_request(request, path='person/search', query=person_name)

        return resp_json[0]['uuid']

    async def person_age(self, request: AliceRequest):
        person_id = self._get_person_id(request)

        resp_json = await self.get_request(request, path=f'person/{person_id}')

        person_birth_date = resp_json[0]['birth_date']
        return await self.make_response(person_birth_date)

    async def person_films(self, request: AliceRequest):
        person_id = self._get_person_id(request)

        resp_json = await self.get_request(request, path=f'person/{person_id}')

        person_film_ids = (film['uuid'] for film in resp_json['filmworks'])

        text = '\n'.join(person_film_ids)
        return await self.make_response(text)

    async def person_biography(self, request: AliceRequest):
        person_id = self._get_person_id(request)

        resp_json = await self.get_request(request, path=f'person/{person_id}')

        person_biography = resp_json[0]['biography']
        return await self.make_response(f'Вот что я нашла - {person_biography}')

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
