from typing import List

from aiohttp import ClientSession
from core import context_logger
from core.logger_route import LoggerRoute
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from models.authapi.models import Tokens, User, UserSignIn, ChangeLogin, ChangePassword
from settings import AUTH_API_URL
from starlette.requests import Request

logger = context_logger.get(__name__)

router = APIRouter(route_class=LoggerRoute)


@router.post(
    '/signup',
    response_model=Tokens,
    description='Метод для регистрации пользователя',
    responses={401: {'description': 'User exist'}}
)
async def sign_up(request: Request, user: User) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.post(
        url=AUTH_API_URL + '/signup',
        json=user.dict(),
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.post(
    '/signin',
    response_model=Tokens,
    description='Метод для авторизации пользователя',
    responses={401: {'description': 'Wrong login or password'}},
)
async def sign_in(request: Request, user: User) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.post(
        url=AUTH_API_URL + f'/signin',
        data=user.dict(),
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.get(
    '/signin_history',
    response_model=List[UserSignIn],
    description='Метод для получения истории авторизаций',
    responses={401: {'description': 'Unauthorized'}},
)
async def sign_in_history(request: Request) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=AUTH_API_URL + f'/signin_history',
        params=request.query_params,
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.post(
    '/protected',
    description='Метод для тестирования access токена',
)
async def protected(request: Request, ) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.post(
        url=AUTH_API_URL + f'/protected',
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.post(
    '/refresh',
    description='Метод для обновления access и refresh токенов'
)
async def refresh(request: Request) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.post(
        url=AUTH_API_URL + f'/refresh',
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.delete(
    '/logout',
    description='Метод для разлогирования с текущего устройства'
)
async def logout(request: Request) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.delete(
        url=AUTH_API_URL + f'/logout',
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.delete(
    '/logout_all',
    description='Метод для разлогирования со всех устройств пользователя'
)
async def logout_all(request: Request) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.delete(
        url=AUTH_API_URL + f'/logout_all',
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.post(
    '/change_login',
    description='Метод для смены логина'
)
async def change_login(request: Request, new_data: ChangeLogin) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.post(
        url=AUTH_API_URL + f'/change_login',
        data=new_data.dict(),
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.post(
    '/change_pass',
    description='Метод для смены пароля'
)
async def change_pass(request: Request, new_data: ChangePassword) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.post(
        url=AUTH_API_URL + f'/change_pass',
        data=new_data.dict(),
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())


@router.get(
    '/public_key',
    description='Метод получения public key для сторонних сервсисов для проверки сигнатуры ключей'
)
async def public_key(request: Request) -> ORJSONResponse:
    session: ClientSession = request.app.state.session
    async with session.get(
        url=AUTH_API_URL + f'/public_key',
        headers={
            'X-REQUEST-ID': request.headers.get('x-request-id'),
            'USER-AGENT': request.headers.get('user-agent'),
        },
    ) as resp:
        return ORJSONResponse(content=await resp.json())
