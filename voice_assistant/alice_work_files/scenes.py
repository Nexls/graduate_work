import inspect
import sys
from abc import ABC, abstractmethod
from typing import Optional

import ujson
from aiohttp import ClientSession

from alice_work_files import intents
from alice_work_files.intents import FILM_INFO_INTENTS, PERSON_INFO_INTENTS, TOP_FILM_INTENTS
from alice_work_files.request import AliceRequest
from alice_work_files.response_helpers import button
from alice_work_files.state import STATE_RESPONSE_KEY


class Scene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    # генерация ответа сцены
    @abstractmethod
    async def reply(self, request):
        raise NotImplementedError()

    # проверка перехода к новой сцене
    def move(self, request: AliceRequest):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    async def handle_global_intents(self, request: AliceRequest):
        raise NotImplementedError()

    @abstractmethod
    async def handle_local_intents(self, request: AliceRequest) -> Optional[str]:
        raise NotImplementedError()

    async def fallback(self, request: AliceRequest):
        text = 'Не понимаю. Попробуй сформулировать иначе'

        # пока складываем нераспознанные выражения в обычный txt файл
        with open('/home/nexls/Documents/Cinema/alice_cinema_search/fallbacks.txt',
                  'a', encoding='utf-8') as file:
            file.write(request.original_utterance + '\n')

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


class SearchScene(Scene):
    def handle_global_intents(self, request: AliceRequest):
        if intents.HELP in request.intents:
            return Helper()
        if any(intent in request.intents for intent in TOP_FILM_INTENTS):
            return TopFilms()
        if any(intent in request.intents for intent in FILM_INFO_INTENTS):
            return FilmInfo()
        if any(intent in request.intents for intent in PERSON_INFO_INTENTS):
            return PersonInfo()


class Welcome(SearchScene):
    async def reply(self, request: AliceRequest):
        text = 'Привет! Cпроси меня о мире кино!'
        return await self.make_response(text, buttons=[
            button('Топ фильмов', hide=True),
            button('Что ты умеешь?', hide=True)
        ])

    def handle_local_intents(self, request: AliceRequest):
        return self.handle_global_intents(request)


class TopFilms(SearchScene):
    def __init__(self):
        self.local_intents = [
            intents.TOP_BY_TYPE,
            intents.TOP_BY_GENRE,
            intents.TOP_BY_RELEASE_DATE,
        ]

    async def reply(self, request: AliceRequest):
        if intents.TOP_BY_TYPE in request.intents:
            return await self.top_by_type(request)
        if intents.TOP_BY_GENRE in request.intents:
            return await self.top_by_genre(request)
        if intents.TOP_BY_RELEASE_DATE in request.intents:
            return await self.top_by_release_date(request)

    async def top_by_type(self, request: AliceRequest):
        filter_type = request.slots.get('MediaType', '')

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film?'
                         f'sort=-imdb_rating&page_size=3&filter_type={filter_type}')) as resp:
                resp_json = await resp.json()

        film_list = [film['title'] for film in resp_json]

        text = ujson.dumps('\n'.join(film_list))
        return await self.make_response(text)

    async def top_by_genre(self, request: AliceRequest):
        filter_genre = request.slots.get('GenreType', '')

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film?'
                         f'sort=-imdb_rating&page_size=3&filter_genre={filter_genre}')) as resp:
                resp_json = await resp.json()

        film_list = [film['title'] for film in resp_json]

        text = ujson.dumps('\n'.join(film_list))
        return await self.make_response(text)

    async def top_by_release_date(self, request: AliceRequest):
        text = 'Фильтрую по дате выхода'
        return await self.make_response(text)

    def handle_local_intents(self, request: AliceRequest):
        if any(intent in request.intents for intent in self.local_intents):
            return self


class Helper(SearchScene):
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


class FilmInfo(SearchScene):
    async def reply(self, request):
        if intents.TOP_BY_TYPE in request.intents:
            return await self.film_author(request)
        if intents.FILM_ACTORS in request.intents:
            return await self.film_actors(request)
        if intents.FILM_GENRE in request.intents:
            return await self.film_genre(request)
        if intents.FILM_RATING in request.intents:
            return await self.film_rating(request)
        if intents.FILM_DURATION in request.intents:
            return await self.film_duration(request)
        if intents.FILM_RELEASE_DATE in request.intents:
            return await self.film_release_date(request)
        if intents.FILM_DESCRIPTION in request.intents:
            return await self.film_description(request)

    # эта функция должна сократить код отдельных функций в 2 раза
    async def get_film_id(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # film_name_rus = request.slots.get('YANDEX.STRING', '')
        # film_name_eng = transliterate(film_name_rus)

        # для теста
        film_name_eng = 'dune'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film/search?'
                         f'sort=-imdb_rating&page_size=1&query={film_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        film_id = resp_json[0]['uuid']

        return await film_id

    async def film_author(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # film_name_rus = request.slots.get('YANDEX.STRING', '')
        # film_name_eng = transliterate(film_name_rus)

        # для теста
        film_name_eng = 'dune'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film/search?'
                         f'sort=-imdb_rating&page_size=1&query={film_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        # film_id = await self.get_film_id(request)

        film_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/film/{film_id}')) as resp:
                resp_json = await resp.json()

        film_writers = [writer['full_name'] for writer in resp_json['writers']]

        text = ujson.dumps('\n'.join(film_writers))
        return await self.make_response(text)

    async def film_actors(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # film_name_rus = request.slots.get('YANDEX.STRING', '')
        # film_name_eng = transliterate(film_name_rus)

        # для теста
        film_name_eng = 'dune'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film/search?'
                         f'sort=-imdb_rating&page_size=1&query={film_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        # film_id = await self.get_film_id(request)

        film_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/film/{film_id}')) as resp:
                resp_json = await resp.json()

        film_actors = [actor['full_name'] for actor in resp_json['actors']]

        text = ujson.dumps('\n'.join(film_actors))
        return await self.make_response(text)

    async def film_description(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # film_name_rus = request.slots.get('YANDEX.STRING', '')
        # film_name_eng = transliterate(film_name_rus)

        # для теста
        film_name_eng = 'dune'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film/search?'
                         f'sort=-imdb_rating&page_size=1&query={film_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        film_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/film/{film_id}')) as resp:
                resp_json = await resp.json()

        film_description = resp_json[0]['description']
        return await self.make_response(film_description)

    async def film_duration(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # film_name_rus = request.slots.get('YANDEX.STRING', '')
        # film_name_eng = transliterate(film_name_rus)

        # для теста
        film_name_rus = 'дюна'
        film_name_eng = 'dune'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film/search?'
                         f'sort=-imdb_rating&page_size=1&query={film_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        film_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/film/{film_id}')) as resp:
                resp_json = await resp.json()

        # film_duration = resp_json[0]['duration']
        return await self.make_response(f'Пока нет информации о длительности фильма {film_name_rus}')

    async def film_genre(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # film_name_rus = request.slots.get('YANDEX.STRING', '')
        # film_name_eng = transliterate(film_name_rus)

        # для теста
        film_name_eng = 'dune'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film/search?'
                         f'sort=-imdb_rating&page_size=1&query={film_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        film_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/film/{film_id}')) as resp:
                resp_json = await resp.json()

        film_genres = [genre['name'] for genre in resp_json['genre']]

        text = ujson.dumps('\n'.join(film_genres))
        return await self.make_response(text)

    async def film_rating(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # film_name_rus = request.slots.get('YANDEX.STRING', '')
        # film_name_eng = transliterate(film_name_rus)

        # для теста
        film_name_rus = 'дюна'
        film_name_eng = 'dune'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film/search?'
                         f'sort=-imdb_rating&page_size=1&query={film_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        film_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/film/{film_id}')) as resp:
                resp_json = await resp.json()

        film_rating = resp_json[0]['imdb_rating']
        return await self.make_response(f'Рейтинг фильма {film_name_rus} - {film_rating}')

    async def film_release_date(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # film_name_rus = request.slots.get('YANDEX.STRING', '')
        # film_name_eng = transliterate(film_name_rus)

        # для теста
        film_name_rus = 'дюна'
        film_name_eng = 'dune'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/film/search?'
                         f'sort=-imdb_rating&page_size=1&query={film_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        film_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/film/{film_id}')) as resp:
                resp_json = await resp.json()

        # film_release_date = resp_json[0]['release_date']
        return await self.make_response(f'Пока нет информации о дате выхода фильма {film_name_rus}')

    def handle_local_intents(self, request: AliceRequest):
        if any(intent in request.intents for intent in FILM_INFO_INTENTS):
            return self


class PersonInfo(SearchScene):
    async def reply(self, request: AliceRequest):
        if intents.PERSON_AGE in request.intents:
            return await self.person_age(request)
        if intents.PERSON_FILMS in request.intents:
            return await self.person_films(request)
        if intents.PERSON_BIOGRAPHY in request.intents:
            return await self.person_biography(request)

    async def person_age(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # person_name_rus = request.slots.get('YANDEX.STRING', '')
        # person_name_eng = transliterate(film_name_rus)

        # для теста
        person_name_rus = 'алиса'
        person_name_eng = 'alice'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/person/search?'
                         f'page_size=1&query={person_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        person_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/person/{person_id}')) as resp:
                resp_json = await resp.json()

        person_birth_date = resp_json[0]['birth_date']
        return await self.make_response(person_birth_date)

    async def person_films(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # person_name_rus = request.slots.get('YANDEX.STRING', '')
        # person_name_eng = transliterate(film_name_rus)

        # для теста
        person_name_rus = 'алиса'
        person_name_eng = 'alice'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/person/search?'
                         f'page_size=1&query={person_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        person_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/person/{person_id}')) as resp:
                resp_json = await resp.json()

        # тут либо возвращать из es сразу названия фильмов
        # либо для каждого фильма отдельно доставать название по id
        person_film_ids = [film['uuid'] for film in resp_json['filmworks']]

        text = ujson.dumps('\n'.join(person_film_ids))
        return await self.make_response(text)

    async def person_biography(self, request: AliceRequest):
        # переводим с русского на латиницу чтобы можно было вставлять в запрос

        # person_name_rus = request.slots.get('YANDEX.STRING', '')
        # person_name_eng = transliterate(film_name_rus)

        # для теста
        person_name_rus = 'алиса'
        person_name_eng = 'alice'

        async with ClientSession() as session:
            async with session.get(
                    url=('http://localhost:8001/api/v1/person/search?'
                         f'page_size=1&query={person_name_eng}')) as resp:
                resp_json = await resp.json()

        # по-хорошему сохранить как переменную класса, чтобы потом использовать в локальных интентах
        person_id = resp_json[0]['uuid']

        async with ClientSession() as session:
            async with session.get(
                    url=(f'http://localhost:8001/api/v1/person/{person_id}')) as resp:
                resp_json = await resp.json()

        # person_biography = resp_json[0]['biography']
        return await self.make_response('Пока нет информации о биографии этого человека')

    def handle_local_intents(self, request: AliceRequest):
        if any(intent in request.intents for intent in PERSON_INFO_INTENTS):
            return PersonInfo()


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


# первая попавшаяся функция транслитерации
def transliterate(name):
    # Словарь с заменами
    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
              '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '',
              ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
              '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
              'Є': 'e', '—': ''}

    # Циклически заменяем все буквы в строке
    for key in slovar:
        name = name.replace(key, slovar[key])
    return name