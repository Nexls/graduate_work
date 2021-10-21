import asyncio

import aiohttp
import pytest
import settings
from app import app
from asgi_lifespan import LifespanManager
from httpx import AsyncClient


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
async def test_client() -> AsyncClient:
    async with LifespanManager(app, startup_timeout=60, shutdown_timeout=60):
        async with AsyncClient(app=app, base_url=settings.SERVICE_URL) as client:
            yield client
