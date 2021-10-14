from functools import lru_cache
from typing import Optional, List, Tuple

from fastapi import Depends, HTTPException
from http import HTTPStatus

from db.db_client import get_elastic, BaseDatabaseClient
from db.storage import get_redis, BaseStorage
from models.genre import Genre
import settings


class GenreService:
    def __init__(self, storage: BaseStorage, db_client: BaseDatabaseClient):
        self.storage = storage
        self.db_client = db_client

    async def get_by_query(self, body: dict) -> Optional[List[Genre]]:
        '''Возвращает список жанров из индекса, без ограничений, всё, что есть'''

        # если не задать size, то он по дефолту 10. Передаем максимум, чтобы вернул всё, что есть
        results = await self.db_client.search(index=settings.ELASTIC_INDEX_GENRE, size=10000)
        return [Genre(**doc) for doc in results]

    async def get_by_id(self, id: str) -> Tuple[Optional[Genre], str]:
        genre = await self._get_from_cache(id)
        cached = "1"
        if not genre:
            genre = await self._get_from_db(id)
            cached = "0"
            if not genre:
                return None, cached

            await self._put_to_cache(genre)

        return genre, cached

    async def _get_from_db(self, id: str) -> Optional[Genre]:
        try:
            doc = await self.db_client.get(settings.ELASTIC_INDEX_GENRE, id)
        except Exception:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')
        return Genre(**doc)

    async def _get_from_cache(self, id: str) -> Optional[Genre]:
        data = await self.storage.get(id)
        if not data:
            return None

        item = Genre.parse_raw(data)
        return item

    async def _put_to_cache(self, item: Genre):

        await self.storage.set(str(item.uuid), item.json(), expire=settings.REDIS_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        storage: BaseStorage = Depends(get_redis),
        db_client: BaseDatabaseClient = Depends(get_elastic),
) -> GenreService:
    return GenreService(storage, db_client)
