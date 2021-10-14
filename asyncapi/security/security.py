import inspect
from enum import Enum
from typing import Optional

import aiohttp
import jwt
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import InvalidSignatureError, ExpiredSignatureError
from pydantic import BaseModel
from settings import JWT_KEY_URL, JWT_PUBLIC_KEY
from starlette import status
from starlette.requests import Request

X_API_KEY = HTTPBearer(auto_error=False)


async def init_jwt_public_key() -> str:
    if JWT_PUBLIC_KEY is not None:
        return JWT_PUBLIC_KEY
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(JWT_KEY_URL) as r:
                    json_body = await r.json()
                    return json_body.get("public_key")
            except:
                ...


class Permissions(Enum):
    OTHER = 0
    USER = 1
    PAYING_USER = 2
    ADMIN = 3


def _get_permissions(jwt_public_key: str, credentials: Optional[HTTPAuthorizationCredentials]) -> int:
    if credentials is None:
        return Permissions.OTHER.value  # Если токена нет, то права 0
    else:
        try:
            payload = jwt.decode(
                jwt=credentials.credentials,
                key=jwt_public_key,
                algorithms=["RS256"]
            )
            return payload.get("permissions", 0)
        except (InvalidSignatureError, ExpiredSignatureError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key"
            )


def transform_obj_by_permissions(res, permissions):
    obj_permissions = getattr(res, '_permissions', 0)
    if obj_permissions != Permissions.OTHER.value and obj_permissions > permissions:
        res = {}
    return res


def jwt_permissions_required(optional=False, response_model=None):
    if response_model is None:
        response_model = BaseModel()

    def decorator(fn):
        async def wrapper(*args, credentials: HTTPAuthorizationCredentials = Depends(X_API_KEY), **kwargs):
            request: Request = kwargs.get('request')
            res = await fn(*args, **kwargs)
            if optional is False:
                permissions = _get_permissions(request.app.state.jwt_public_key, credentials)
                if isinstance(response_model, BaseModel):
                    res = transform_obj_by_permissions(res, permissions)
                elif issubclass(response_model.__origin__, list):
                    new_res = []
                    for obj in res:
                        obj = transform_obj_by_permissions(obj, permissions)
                        if obj:
                            new_res.append(obj)
                    res = new_res
            return res

        parameters = [*inspect.signature(fn).parameters.values()]
        if optional is False:
            parameters.append(inspect.Parameter(
                name='credentials',
                kind=inspect._ParameterKind.KEYWORD_ONLY,
                default=Depends(X_API_KEY),
                annotation=HTTPAuthorizationCredentials,
            ))
        wrapper.__signature__ = inspect.Signature(
            parameters=parameters,
            return_annotation=inspect.signature(fn).return_annotation,
        )
        wrapper.__name__ = fn.__name__

        return wrapper

    return decorator
