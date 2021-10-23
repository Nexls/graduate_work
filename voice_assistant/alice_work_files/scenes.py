import inspect
import sys
from abc import ABC, abstractmethod
from typing import Optional

import intents
from intents import FILM_INFO_INTENTS, PERSON_INFO_INTENTS, TOP_FILM_INTENTS
from request import Request
from response_helpers import button
from state import STATE_RESPONSE_KEY


class Scene(ABC):

    @classmethod
    def id(cls):
        return cls.__name__

    # генерация ответа сцены
    @abstractmethod
    def reply(self, request):
        raise NotImplementedError()

    # проверка перехода к новой сцене
    def move(self, request: Request):
        next_scene = self.handle_local_intents(request)
        if next_scene is None:
            next_scene = self.handle_global_intents(request)
        return next_scene

    @abstractmethod
    def handle_global_intents(self, request: Request):
        raise NotImplementedError()

    @abstractmethod
    def handle_local_intents(self, request: Request) -> Optional[str]:
        raise NotImplementedError()

    def fallback(self, request: Request):
        text = 'Спроси нормально.'

        with open('/home/nexls/Documents/Cinema/GRADUATE/alice_cinema_search/fallbacks.txt',
                  'a', encoding='utf-8') as file:
            file.write(request.original_utterance + '\n')

        return self.make_response(text, buttons=[
            button('Что ты умеешь?', hide=True)
        ])

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None):
        response = {
            'text': text,
            'tts': tts if tts is not None else text,
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
    def handle_global_intents(self, request: Request):
        if intents.HELP in request.intents:
            return Helper()
        if any(intent in request.intents for intent in TOP_FILM_INTENTS):
            return TopFilms()
        if any(intent in request.intents for intent in FILM_INFO_INTENTS):
            return FilmInfo()
        if any(intent in request.intents for intent in PERSON_INFO_INTENTS):
            return PersonInfo()


class Welcome(SearchScene):
    def reply(self, request: Request):
        text = 'Привет! Cпроси меня о мире кино!'
        return self.make_response(text, buttons=[
            button('Топ фильмов', hide=True),
            button('Что ты умеешь?', hide=True)
        ])

    def handle_local_intents(self, request: Request):
        pass


class TopFilms(SearchScene):
    def __init__(self):
        self.local_intents = [
            intents.TOP_BY_TYPE,
            intents.TOP_BY_GENRE,
            intents.TOP_BY_RELEASE_DATE,
        ]

    def reply(self, request: Request):
        if intents.TOP_BY_TYPE in request.intents:
            return self.top_by_type(request)
        if intents.TOP_BY_GENRE in request.intents:
            return self.top_by_genre(request)
        if intents.TOP_BY_RELEASE_DATE in request.intents:
            return self.top_by_release_date(request)

    def top_by_type(self, request: Request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Фильтрую по типу'
        return self.make_response(text)

    def top_by_genre(self, request: Request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Фильтрую по жанру'
        return self.make_response(text)

    def top_by_release_date(self, request: Request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Фильтрую по дате выхода'
        return self.make_response(text)

    def handle_local_intents(self, request: Request):
        if any(intent in request.intents for intent in self.local_intents):
            return TopFilms()


class Helper(SearchScene):
    def reply(self, request):
        text = ('Я могу показать лучшие фильмы этой недели.\n'
                'Или, например, сказать кто снял фильм.\n'
                'А еще могу посоветовать фильмы с твоим любимым актером.')
        return self.make_response(text, buttons=[
            button('Покажи топ фильмов', hide=True),
            button('Покажи лучшие комедии', hide=True),
            button('Кто автор фильма Дюна?', hide=True),
            button('В каких фильмах снимался Джейсон Стэтхем?', hide=True),
            button('Что ты умеешь?', hide=True)
        ])

    def handle_local_intents(self, request: Request):
        pass


class FilmInfo(SearchScene):
    def reply(self, request):
        if intents.TOP_BY_TYPE in request.intents:
            return self.film_author(request)
        if intents.FILM_ACTORS in request.intents:
            return self.film_actors(request)
        if intents.FILM_GENRE in request.intents:
            return self.film_genre(request)
        if intents.FILM_RATING in request.intents:
            return self.film_rating(request)
        if intents.FILM_DURATION in request.intents:
            return self.film_duration(request)
        if intents.FILM_RELEASE_DATE in request.intents:
            return self.film_release_date(request)
        if intents.FILM_DESCRIPTION in request.intents:
            return self.film_description(request)

    def film_author(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Автор фильма'
        return self.make_response(text)

    def film_actors(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Актеры фильма'
        return self.make_response(text)

    def film_description(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Описание фильма'
        return self.make_response(text)

    def film_duration(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Длительность фильма'
        return self.make_response(text)

    def film_genre(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Жанр фильма'
        return self.make_response(text)

    def film_rating(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Рейтинг фильма'
        return self.make_response(text)

    def film_release_date(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Дата выхода фильма'
        return self.make_response(text)

    def handle_local_intents(self, request: Request):
        if any(intent in request.intents for intent in FILM_INFO_INTENTS):
            return TopFilms()


class PersonInfo(SearchScene):
    def reply(self, request):
        if intents.PERSON_AGE in request.intents:
            return self.person_age(request)
        if intents.PERSON_FILMS in request.intents:
            return self.person_films(request)
        if intents.PERSON_BIOGRAPHY in request.intents:
            return self.person_biography(request)

    def person_age(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Возраст человека'
        return self.make_response(text)

    def person_films(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Фильмы с участием человека'
        return self.make_response(text)

    def person_biography(self, request):
        # запрос к бд, можно из запроса передавать параметры в функцию
        text = 'Биография человека'
        return self.make_response(text)

    def handle_local_intents(self, request: Request):
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
