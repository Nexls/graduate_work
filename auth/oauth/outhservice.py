from typing import Dict

from flask import redirect, request, render_template
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restplus import abort
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.orm import Session

import settings
from db.db import session
from db.storage import jwt_storage
from models.user import SocialAccount, User, UserSignIn, Roles, Permissions
from settings import VK_CLIENT_ID, VK_CLIENT_SECRET, FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET, WEB_list, MOB_list
from utils.utils import generate_random_pass, get_platform_by_user_agent
from .provider import BaseProvider, VkProvider, FacebookProvider


class OAuthService:
    def __init__(self, session: Session, url_pattern: str = "http://localhost:5000/social_auth/"):
        self.session = session
        self.url_pattern = url_pattern.rstrip("/")
        self.providers: Dict[str, BaseProvider] = {}

    def add_providers(self, *args):
        for provider in args:
            if not isinstance(provider, BaseProvider):
                raise ValueError(f"args {provider} must be instance of BaseProvider")
            provider.update_url_pattern(self.url_pattern)
            self.providers[provider.name] = provider

    @property
    def providers_list(self):
        return [{'name': name, 'url': f'{self.url_pattern}/login/{name}'} for name in self.providers.keys()]

    def oauth_resolver(self, method: str, provider_name: str):
        if method not in ['login', 'callback'] or provider_name not in self.providers:
            abort(404)
        if method == 'login':
            return redirect(self.providers[provider_name].auth_url)
        else:
            code = request.args.get('code')
            if code is None:
                abort(400)
            return self.oauth_authorization(self.providers[provider_name], code)

    def oauth_authorization(self, provider: BaseProvider, request_code: str):
        platform = get_platform_by_user_agent(web_list=WEB_list, mob_list=MOB_list, user_agent=request.user_agent)
        user_social = provider.get_user(code=request_code)
        user_db: User = User.query.filter_by(email=user_social.email).one_or_none()
        social_account_db = SocialAccount.query.filter_by(social_id=user_social.social_id).one_or_none()
        if user_db:
            return render_template('login.html', account=user_db.email)
        if not social_account_db:
            # TODO: replace password to generate_random_password()
            user_db = User(login=user_social.social_id, password=pbkdf2_sha256.hash("passpass"),
                           email=user_social.email)
            session.add(user_db)
            session.flush()
            session.refresh(user_db)
            social_account_db = SocialAccount(user_id=user_db.id, social_id=user_social.social_id,
                                              social_name=provider.name)
            user_permissions = Roles(user_id=user_db.id, permissions=Permissions.PAYING_USER)
            session.add(social_account_db)
            session.add(user_permissions)
        else:
            # Если аккаунт соц сети найден, вытаскиваем соотвествюущего user
            user_db = social_account_db.user
        user_sing_in = UserSignIn(user_id=user_db.id, user_agent=request.user_agent.string,
                                  user_device_type=platform)
        session.add(user_sing_in)
        session.commit()
        access_token = create_access_token(identity=user_db.login,
                                           additional_claims={'permissions': Permissions.USER.value})
        refresh_token = create_refresh_token(identity=user_db.login,
                                             additional_claims={'platform': platform})
        jwt_storage.set(key=f"{user_db.login}_{platform}_refresh", value=refresh_token,
                        expire=settings.refresh_token_expires)
        return {'access_token': access_token, 'refresh_token': refresh_token}


oauth_service = OAuthService(session)
oauth_service.add_providers(VkProvider(client_id=VK_CLIENT_ID, client_secret=VK_CLIENT_SECRET),
                            FacebookProvider(client_id=FACEBOOK_CLIENT_ID, client_secret=FACEBOOK_CLIENT_SECRET))
