from werkzeug.useragents import UserAgent
from redis import Redis
from .backoff import backoff
from db.storage import RedisStorage
import json
from datetime import datetime, date
import string
from secrets import choice


class JsonExtendEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)


def get_platform_by_user_agent(web_list: list, mob_list: list, user_agent: UserAgent):
    platform = user_agent.platform
    if platform in web_list:
        return 'web'
    elif platform in mob_list:
        return 'mobile'
    else:
        return 'smart'


def generate_random_email():
    alphabet = string.ascii_letters + string.digits
    return ''.join(choice(alphabet) for _ in range(8)) + '@random.com'


def generate_random_pass():
    alphabet = string.ascii_letters + string.digits
    return ''.join(choice(alphabet) for _ in range(16))


def delete_all_tokens_by_user_id(user_id: str, jwt_storage: RedisStorage):
    for key in jwt_storage.get_many_key_by_pattern(search_key=f'{user_id}_*'):
        jwt_storage.delete(key=key)


@backoff()
def wait_redis(redis: Redis):
    response = redis.ping()
    if not response:
        raise
