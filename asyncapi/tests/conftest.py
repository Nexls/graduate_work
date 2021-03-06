import asyncio
import json
from dataclasses import dataclass

import aiohttp
import aioredis
import pytest
import settings
from app import app
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from multidict import CIMultiDictProxy
from tests.functional.settings import BASE_DIR

from elasticsearch import AsyncElasticsearch, helpers


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='function', autouse=True)
def patch_indexes(monkeypatch):
    monkeypatch.setattr(settings, 'ELASTIC_INDEX_FILM', f'test_{settings.ELASTIC_INDEX_FILM}')
    monkeypatch.setattr(settings, 'ELASTIC_INDEX_GENRE', f'test_{settings.ELASTIC_INDEX_GENRE}')
    monkeypatch.setattr(settings, 'ELASTIC_INDEX_PERSON', f'test_{settings.ELASTIC_INDEX_PERSON}')


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}'])
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = settings.SERVICE_URL + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


@pytest.fixture
async def test_client() -> AsyncClient:
    async with LifespanManager(app, startup_timeout=60, shutdown_timeout=60):
        async with AsyncClient(app=app, base_url=settings.SERVICE_URL) as client:
            yield client


@pytest.fixture(scope='session')
def load_data(session, es_client):
    async def inner(index_name: str, file_name: str) -> bool:
        """
        ?????????????????? ???????????? ?? ??????????????. ???????????????????? True, ???????? ?????? ???????????? ??????????????
        """
        def gendata(body: list):
            for item in body:
                yield {
                    '_index': index_name,
                    '_id': item['uuid'],
                    '_source': item,
                }

        with open(BASE_DIR / 'testdata' / file_name, 'r') as f:
            data = json.load(f)

        # ???????????????? refresh ??????????????, ?????? ???????? ?????????? ?????????? ???????????????? ?????????????? ?????????????? ????????????????????
        _, errs = await helpers.async_bulk(es_client, gendata(data), chunk_size=500, refresh=True)

        # ?? ?????????????? errs ???????????? ?????????????????????? ????????????, ???????? ????????
        if len(errs) > 0:
            return False
        return True
    return inner


# ?????????????? ?????? ???????????????? ?? ?????????? ????????????, ??.??. ???????? ????????, ?????????????? ?????????????? ?????????? 2 ??????????????.
# ?? ???????? ?????????????? ?????????????? ?????????? ??????????, ???? ???????????????? ???????????? ????????, ?????????????? ???????????? ?????? ????????????????????
@pytest.fixture(scope='session', autouse=True)
async def storage_clear():
    redis = aioredis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASS if settings.REDIS_PASS else None,
        ssl=settings.REDIS_USE_SSL,
        ssl_cert_reqs='none',
    )
    await redis.flushall(asynchronous=True)


@pytest.fixture(scope='session', autouse=True)
async def load_films(load_data, es_client):
    """???????????????????? ???????????? ?????? ??????????"""
    rez = await load_data(f'test_{settings.ELASTIC_INDEX_FILM}', 'movies.json')
    yield rez
    await es_client.indices.delete(f'test_{settings.ELASTIC_INDEX_FILM}')


@pytest.fixture(scope='session', autouse=True)
async def load_persons(load_data, es_client):
    """???????????????????? ???????????? ?????? ??????????"""
    rez = await load_data(f'test_{settings.ELASTIC_INDEX_PERSON}', 'persons.json')
    yield rez
    await es_client.indices.delete(f'test_{settings.ELASTIC_INDEX_PERSON}')


@pytest.fixture(scope='session', autouse=True)
async def load_genres(load_data, es_client):
    """???????????????????? ???????????? ?????? ??????????"""
    rez = await load_data(f'test_{settings.ELASTIC_INDEX_GENRE}', 'genres.json')
    yield rez
    await es_client.indices.delete(f'test_{settings.ELASTIC_INDEX_GENRE}')
