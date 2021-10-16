from functools import lru_cache
from typing import Optional, List, Tuple

from fastapi import Depends, HTTPException
from http import HTTPStatus

from db.db_client import get_elastic, BaseDatabaseClient
from db.storage import get_redis, BaseStorage
from models.film import Film
from models.film_response import FilmResponse
from models.enumerations import QueryType
from services.query_constructor import QueryConstructor
import settings


class FilmService:
    def __init__(self, storage: BaseStorage, db_client: BaseDatabaseClient):
        self.storage = storage
        self.db_client = db_client

    async def _search_query_db(self, body: dict, query_type: QueryType) -> Optional[List[Film]]:

        query_constructor = QueryConstructor(body).add_sort().add_limits()
        if query_type == QueryType.SEARCH:
            query_constructor = query_constructor.add_multi_field_search([
                'title',
                'description',
                'genre.name',
                'actors.full_name',
                'writers.full_name',
                'directors.full_name'
            ])
        if query_type == QueryType.FILTER:
            query_constructor = query_constructor.add_filter('genre.name.keyword', 'filter_genre')

        payload = query_constructor.get_payload()

        results = await self.db_client.search(index=settings.ELASTIC_INDEX_FILM, body=payload)
        return [Film(**doc) for doc in results]

    async def get_by_query(self, body: dict, query_type: QueryType) -> List[FilmResponse]:
        """Получает список фильмов из эластика и преобразовывает в нужный формат ответа API"""
        film_list = await self._search_query_db(body, query_type)
        return [FilmResponse(
            uuid=film.uuid,
            title=film.title,
            imdb_rating=film.imdb_rating
        ) for film in film_list]

    # get_by_id возвращает объект фильма и флаг если объект из кэша.
    # Объект опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Tuple[Optional[Film], str]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        cached = '1'
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_db(film_id)
            cached = '0'
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None, cached
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film, cached

    async def _get_film_from_db(self, film_id: str) -> Optional[Film]:
        # Если не найдено по id, то эластик кидает исключение. Оборачиваем в попытку и ругаемся правильно
        try:
            doc = await self.db_client.get(settings.ELASTIC_INDEX_FILM, film_id)
        except Exception:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
        return Film(**doc)

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.storage.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.storage.set(str(film.uuid), film.json(), expire=settings.REDIS_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        storage: BaseStorage = Depends(get_redis),
        db_client: BaseDatabaseClient = Depends(get_elastic),
) -> FilmService:
    return FilmService(storage, db_client)
