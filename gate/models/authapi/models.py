from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    login: str = Field(description='User\'s login', min_length=5, default='example')
    password: str = Field(description='User\'s password', min_length=8, default='passpass')


class UserSignIn(BaseModel):
    logined_by: datetime = Field(description='Auth datetime', default='2021-04-15T09:08:17')
    user_device_type: str = Field(description='Auth device type', default='mobile')
    user_agent: str = Field(
        description='Auth user-agent',
        default='Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/47.0.2526.83 Mobile Safari/537.36'
    )


class ChangeLogin(BaseModel):
    new_login: str = Field(description='User\'s login', min_length=5, default='example')


class ChangePassword(BaseModel):
    new_password: str = Field(description='User\'s password', min_length=8, default='passpass')


class Tokens(BaseModel):
    access_token: str = Field(description='Access token')
    refresh_token: str = Field(description='Refresh token')
