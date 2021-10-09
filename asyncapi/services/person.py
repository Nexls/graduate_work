from functools import lru_cache
from typing import Optional, List, Tuple

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException
from http import HTTPStatus

from db.db_client import get_elastic, BaseDatabaseClient
from db.storage import get_redis, BaseStorage
from models.film_response import FilmResponse
from models.person import Person
from models.person_response import PersonResponse
from services.query_constructor import QueryConstructor
from models.enumerations import QueryType
from core.config import REDIS_CACHE_EXPIRE_IN_SECONDS, ELASTIC_INDEX_PERSON, ELASTIC_INDEX_FILM


class PersonService:
    def __init__(self, storage: BaseStorage, db_client: BaseDatabaseClient):
        self.storage = storage
        self.db_client = db_client

    async def _search_query_db(self, body: dict, query_type: QueryType) -> Optional[List[Person]]:
        '''Возвращает список персон из индекса, с ограничениями и поиском, если задано в запросе'''

        query_constructor = QueryConstructor(body).add_sort().add_limits().add_single_field_search('full_name')
        payload = query_constructor.get_payload()

        results = await self.db_client.search(index=ELASTIC_INDEX_PERSON, body=payload)
        return [Person(**doc) for doc in results]

    async def get_by_query(self, body: dict, query_type: QueryType) -> Optional[List[PersonResponse]]:
        '''Получает список персон из эластика и преобразовывает в нужный формат ответа API'''

        person_list = await self._search_query_db(body, query_type)

        result = []
        for person in person_list:
            film_roles = {'actor': [], 'writer': [], 'director': []}
            [film_roles[film.role].append(film.uuid) for film in person.filmworks]
            for role, films in film_roles.items():
                if not films:
                    continue

                result.append(PersonResponse(
                    uuid=person.uuid,
                    full_name=person.full_name,
                    role=role,
                    film_ids=films
                ))

        return result

    # get_by_id возвращает объект персонажа. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, id: str) -> Tuple[Optional[PersonResponse], str]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        person_response = await self._get_from_cache(id)
        cached = "1"
        if not person_response:
            # Если персоны нет в кеше, то ищем его в Elasticsearch
            person = await self._get_from_elastic(id)
            cached = "0"
            if not person:
                return None, cached

            person_response = await self._convert_person(person)

            await self._put_to_cache(person_response)

        return person_response, cached

    async def _convert_person(self, person: Person) -> PersonResponse:
        film_roles = {'actor': [], 'writer': [], 'director': []}
        roles = []
        film_ids = []

        [film_roles[film.role].append(film.uuid) for film in person.filmworks]
        for role, films in film_roles.items():
            if not films:
                continue
            roles.append(role)
            film_ids += films

        return PersonResponse(
            uuid=person.uuid,
            full_name=person.full_name,
            role=','.join(roles),
            film_ids=film_ids
        )

    async def _get_from_elastic(self, id: str) -> Optional[Person]:
        # Если не найдено по id, то эластик кидает исключение. Оборачиваем в попытку и ругаемся правильно
        try:
            doc = await self.db_client.get(ELASTIC_INDEX_PERSON, id)
        except Exception:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
        return Person(**doc)

    async def _get_from_cache(self, id: str) -> Optional[PersonResponse]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.storage.get(id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        item = PersonResponse.parse_raw(data)
        return item

    async def _put_to_cache(self, item: PersonResponse):

        await self.storage.set(str(item.uuid), item.json(), expire=REDIS_CACHE_EXPIRE_IN_SECONDS)

    async def get_films_by_person_id(self, id: str) -> Optional[List[FilmResponse]]:
        person, cached = await self.get_by_id(id)
        if not person:
            return None

        # строим свой запрос в эластик
        try:
            docs = await self.db_client.mget(
                body={'ids': person.film_ids},
                index=ELASTIC_INDEX_FILM
                )
        except Exception:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

        return [FilmResponse(**doc) for doc in docs]


@lru_cache()
def get_person_service(
        storage: BaseStorage = Depends(get_redis),
        db_client: BaseDatabaseClient = Depends(get_elastic),
) -> PersonService:
    return PersonService(storage, db_client)
