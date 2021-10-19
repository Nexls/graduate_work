import json
from functools import wraps

from db.db import session
from db.storage import jwt_storage
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, \
    create_refresh_token, unset_jwt_cookies, get_jwt
from flask_restplus import Resource, reqparse
from models.user import User, UserSignIn, Roles, Permissions
from passlib.hash import pbkdf2_sha256
from schemas import user, api, tokens, change_login, change_pass, user_sign_in
from settings import WEB_list, MOB_list
from settings import public_key, refresh_token_expires
from sqlalchemy import or_
from utils import context_logger
from utils.utils import get_platform_by_user_agent, delete_all_tokens_by_user_id, JsonExtendEncoder, \
    generate_random_email

logger = context_logger.get(__name__)


def response_decorator():
    def _response_decorator(f):
        @wraps(f)
        def __response_decorator(*args, **kwargs):
            body = api.payload

            request_context = context_logger.Context.get()
            request_context['json_body'] = body
            context_logger.Context.set(request_context)
            logger.info(f'receive request for {f.__name__}')
            result = f(*args, **kwargs)
            return result

        return __response_decorator

    return _response_decorator


@api.route('/signup', doc={'description': 'Метод для регистрации пользователя'})
class Signup(Resource):
    @api.expect(user, validate=True)
    @api.response(200, 'Success', tokens)
    @api.response(401, 'User exist')
    @response_decorator()
    def post(self):
        logger.info('Api SignUp')
        platform = get_platform_by_user_agent(web_list=WEB_list, mob_list=MOB_list, user_agent=request.user_agent)
        data = api.payload
        user = User.query.filter(or_(User.login == data['login'], User.email == data['login'])).one_or_none()
        if user:
            return 'User exist', 401
        hass_pass = pbkdf2_sha256.hash(data['password'])
        user_db = User(login=data['login'], password=hass_pass, email=data.get('email', generate_random_email()))
        session.add(user_db)
        session.flush()
        session.refresh(user_db)
        user_sing_in = UserSignIn(user_id=user_db.id, user_agent=request.user_agent.string,
                                  user_device_type=platform)
        user_permissions = Roles(user_id=user_db.id, permissions=Permissions.USER)
        session.add(user_sing_in)
        session.add(user_permissions)
        session.commit()
        access_token = create_access_token(identity=data['login'],
                                           additional_claims={'permissions': Permissions.USER.value})
        refresh_token = create_refresh_token(identity=data['login'], additional_claims={'platform': platform})
        jwt_storage.set(key=f"{data['login']}_{platform}_refresh", value=refresh_token, expire=refresh_token_expires)
        return {'access_token': access_token, 'refresh_token': refresh_token}


@api.route('/signin', doc={'description': 'Метод для авторизации пользователя'})
class Signin(Resource):
    @api.expect(user, validate=True)
    @api.response(200, 'Success', tokens)
    @api.response(401, 'Wrong login or password')
    def post(self):
        platform = get_platform_by_user_agent(web_list=WEB_list, mob_list=MOB_list, user_agent=request.user_agent)
        data = api.payload
        user = User.query.filter(or_(User.login == data['login'], User.email == data['login'])).one_or_none()
        if not user or not pbkdf2_sha256.verify(data['password'], user.password):
            return 'Wrong login or password', 401
        user_sing_in = UserSignIn(user_id=user.id, user_agent=request.user_agent.string,
                                  user_device_type=platform)
        session.add(user_sing_in)
        session.commit()
        user_permissions: Roles = Roles.query.filter_by(user_id=user.id).first()
        access_token = create_access_token(identity=user.login,
                                           additional_claims={'permissions': user_permissions.permissions.value})
        refresh_token = create_refresh_token(identity=user.login, additional_claims={'platform': platform})
        jwt_storage.set(key=f'{user.login}_{platform}_refresh', value=refresh_token, expire=refresh_token_expires)
        return {'access_token': access_token, 'refresh_token': refresh_token}


def get_parser(key_type: str):
    parser = reqparse.RequestParser()
    parser.add_argument('Authorization', location='headers',
                        help=f'Authorization: Bearer <{key_type}_token>')
    return parser


@api.route('/signin_history', doc={'description': 'Метод для получения истории авторизаций'})
class SigninHistory(Resource):
    @api.doc(security='apikey')
    @jwt_required(locations=['headers'])
    @api.response(200, 'Success', [user_sign_in])
    @api.response(401, 'Unauthorized')
    def get(self):
        user_id = get_jwt()['sub']
        user_db = User.query.filter_by(login=user_id).one_or_none()
        sign_in_history = UserSignIn.query.with_entities(UserSignIn.logined_by, UserSignIn.user_agent,
                                                         UserSignIn.user_device_type).filter_by(
            user_id=user_db.id).all()
        history_list = []
        for store in sign_in_history:
            dict_store = dict(**store)
            history_list.append(dict_store)
        return json.dumps(history_list, cls=JsonExtendEncoder)


@api.route('/protected', doc={'description': 'Метод для тестирования access токена'})
class Protected(Resource):
    @api.doc(security='apikey')
    @jwt_required(locations=['headers'])
    def post(self):
        return 'You are authenticated!', 200


@api.route('/refresh', doc={'description': 'Метод для обновления access и refresh токенов'})
class Refresh(Resource):
    @api.expect(get_parser('refresh'))
    @jwt_required(locations=['headers'], refresh=True)
    def post(self):
        platform = get_platform_by_user_agent(web_list=WEB_list, mob_list=MOB_list, user_agent=request.user_agent)
        identity = get_jwt_identity()
        user_id = get_jwt()['sub']
        user_permissions: Roles = Roles.query.join(User).filter(User.login == user_id).first()
        access_token = create_access_token(identity=identity,
                                           additional_claims={'permissions': user_permissions.permissions.value})
        refresh_token = create_refresh_token(identity=identity, additional_claims={'platform': platform})
        jwt_storage.set(key=f'{user_id}_{platform}_refresh', value=refresh_token, expire=refresh_token_expires)
        return {'access_token': access_token, 'refresh_token': refresh_token}


@api.route('/logout', doc={'description': 'Метод для разлогирования с текущего устройства'})
class Logout(Resource):
    @api.doc(security='apikey')
    @jwt_required(locations=['headers'])
    def delete(self):
        platform = get_platform_by_user_agent(web_list=WEB_list, mob_list=MOB_list, user_agent=request.user_agent)
        response = jsonify({'msg': 'logout successful'})
        unset_jwt_cookies(response)
        user_id = get_jwt()['sub']
        jwt_storage.delete(key=f'{user_id}_{platform}_refresh')
        return response


@api.route('/logout_all', doc={'description': 'Метод для разлогирования со всех устройств пользователя'})
class LogoutAll(Resource):
    @api.doc(security='apikey')
    @jwt_required(locations=['headers'])
    def delete(self):
        response = jsonify({'msg': 'logout all successful'})
        unset_jwt_cookies(response)
        user_id = get_jwt()['sub']
        delete_all_tokens_by_user_id(user_id, jwt_storage)
        return response


@api.route('/change_login', doc={'description': 'Метод для смены логина'})
class ChangeInfo(Resource):
    @api.expect(change_login, validate=True)
    @api.doc(security='apikey')
    @jwt_required(locations=['headers'])
    def post(self):
        platform = get_platform_by_user_agent(web_list=WEB_list, mob_list=MOB_list, user_agent=request.user_agent)
        user_id = get_jwt()['sub']
        data = api.payload
        session.query(User).filter(User.login == user_id).update({'login': data['new_login']})
        session.commit()
        delete_all_tokens_by_user_id(user_id, jwt_storage)
        user_permissions: Roles = Roles.query.join(User).filter(User.login == data['new_login']).first()
        access_token = create_access_token(identity=data['new_login'],
                                           additional_claims={'permissions': user_permissions.permissions.value})
        refresh_token = create_refresh_token(identity=data['new_login'], additional_claims={'platform': platform})
        jwt_storage.set(key=f'{data["new_login"]}_{platform}_refresh', value=refresh_token,
                        expire=refresh_token_expires)
        return {'access_token': access_token, 'refresh_token': refresh_token}


@api.route('/change_pass', doc={'description': 'Метод для смены пароля'})
class ChangeInfo(Resource):
    @api.expect(change_pass, validate=True)
    @api.doc(security='apikey')
    @jwt_required(locations=['headers'])
    def post(self):
        platform = get_platform_by_user_agent(web_list=WEB_list, mob_list=MOB_list, user_agent=request.user_agent)
        user_id = get_jwt()['sub']
        data = api.payload
        session.query(User).filter(User.login == user_id).update({'password': data['new_password']})
        session.commit()
        delete_all_tokens_by_user_id(user_id, jwt_storage)
        user_permissions: Roles = Roles.query.join(User).filter(User.login == user_id).first()
        access_token = create_access_token(identity=user_id,
                                           additional_claims={'permissions': user_permissions.permissions.value})
        refresh_token = create_refresh_token(identity=user_id, additional_claims={'platform': platform})
        jwt_storage.set(key=f'{user_id}_{platform}_refresh', value=refresh_token,
                        expire=refresh_token_expires)
        return {'access_token': access_token, 'refresh_token': refresh_token}


@api.route('/public_key', doc={'description': 'Метод получения public key для сторонних сервсисов '
                                              'для проверки сигнатуры ключей'})
class PublicKey(Resource):
    def get(self):
        return {'public_key': public_key.decode()}
