from functools import lru_cache

from aiohttp import ClientSession


@lru_cache()
async def get_session() -> ClientSession:
    return ClientSession()
