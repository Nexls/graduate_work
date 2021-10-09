from flask_restplus import fields
from .api import api

user = api.model('User', {
    'login': fields.String(description='User\'s login', min_length=5, required=True, example='example'),
    'password': fields.String(description='User\'s password', required=True, min_length=8, example='passpass'),
})

user_sign_in = api.model('UserSignIn', {
    'logined_by': fields.DateTime(description='Auth datetime', example='2021-04-15 09:08:17.532807'),
    'user_device_type': fields.String(description='Auth device type', example='mobile'),
    'user_agent': fields.String(description='Auth user-agent', example='Mozilla/5.0 '
                                                                       '(Linux; Android 6.0.1; Nexus 6P Build/MMB29P) '
                                                                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                                       'Chrome/47.0.2526.83 Mobile Safari/537.36'),
})

change_login = api.model('ChangeEmail', {
    'new_login': fields.String(description='User\'s login', required=True, min_length=5, example='example'),
})
change_pass = api.model('ChangePass', {
    'new_password': fields.String(description='User\'s password', required=True, min_length=8, example='passpass'),
})

tokens = api.model('Tokens', {
    'access_token': fields.String(description='Access token'),
    'refresh_token': fields.String(description='Refresh token')
})
