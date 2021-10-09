from abc import abstractmethod, ABC
from dataclasses import dataclass

from requests import get

from utils.utils import generate_random_email


@dataclass
class SocialUser:
    email: str
    social_id: str

    def to_json(self):
        return {"email": self.email, "social_id": self.social_id}


class BaseProvider(ABC):
    def __init__(self, name: str, client_id: str, client_secret: str,
                 url_pattern: str = "http://localhost:5000/social_auth/"):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.url_pattern = url_pattern.rstrip("/")

    @property
    @abstractmethod
    def auth_url(self):
        pass

    @property
    def redirect_uri(self):
        return f"{self.url_pattern}/callback/{self.name}"

    def update_url_pattern(self, new_url_pattern: str):
        self.url_pattern = new_url_pattern.rstrip("/")

    @abstractmethod
    def get_access_token(self, code: str) -> str:
        pass

    @abstractmethod
    def get_user(self, code: str) -> SocialUser:
        pass


class VkProvider(BaseProvider):
    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 url_pattern: str = "http://localhost:5000/social_auth/"):
        super().__init__(name="vk", client_id=client_id, client_secret=client_secret, url_pattern=url_pattern)

    @property
    def auth_url(self):
        return f"https://oauth.vk.com/authorize?display=page" \
               f"&scope=4194304" \
               f"&response_type=code" \
               f"&client_id={self.client_id}" \
               f"&redirect_uri={self.redirect_uri}"

    def get_access_token(self, code: str) -> str:
        params = {"client_id": self.client_id, "client_secret": self.client_secret,
                  "redirect_uri": self.redirect_uri,
                  "code": code}
        res = get(url="https://oauth.vk.com/access_token", params=params).json()
        return res["access_token"]

    def get_user(self, code: str) -> SocialUser:
        params = {"client_id": self.client_id,
                  "client_secret": self.client_secret,
                  "redirect_uri": self.redirect_uri,
                  "code": code}
        res = get(url="https://oauth.vk.com/access_token", params=params, verify=False).json()
        email = res.get("email", generate_random_email())
        social_id = str(res["user_id"])
        return SocialUser(email=email, social_id=social_id)


class FacebookProvider(BaseProvider):
    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 url_pattern: str = "http://localhost:5000/social_auth/"):
        super().__init__(name="facebook", client_id=client_id, client_secret=client_secret, url_pattern=url_pattern)

    @property
    def auth_url(self):
        return f"https://www.facebook.com/v10.0/dialog/oauth?" \
               f"&scope=email" \
               f"&client_id={self.client_id}" \
               f"&redirect_uri={self.redirect_uri}"

    def get_access_token(self, code: str) -> str:
        params = {"client_id": self.client_id,
                  "client_secret": self.client_secret,
                  "redirect_uri": self.redirect_uri,
                  "code": code}
        res = get(url="https://graph.facebook.com/v10.0/oauth/access_token", params=params, verify=False).json()
        return res["access_token"]

    def get_user(self, code: str) -> SocialUser:
        access_token = self.get_access_token(code)
        params = {"fields": "id,email", "access_token": access_token}
        res = get(url="https://graph.facebook.com/v10.0/me", params=params).json()
        email = res.get("email", generate_random_email())
        social_id = str(res["id"])
        return SocialUser(email=email, social_id=social_id)
