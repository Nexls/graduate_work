import logging
import sys
from logging import config

import settings
from api.routes import api
from app import app
from db.db import init_db, session
from db.storage import jwt_storage
from flask_jwt_extended import JWTManager
from utils import context_logger
from utils.utils import wait_redis

api.init_app(app)
jwt = JWTManager(app)
init_db()
wait_redis(jwt_storage.redis_adapter)
logger = context_logger.get(__name__)
config.dictConfig(settings.LOGGING)
logger.logger.addHandler(logging.StreamHandler(sys.stdout))


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    user_id = jwt_payload['sub']
    token_type = jwt_payload['type']
    if token_type == 'access':
        return False
    platform = jwt_payload['platform']
    token_in_redis = jwt_storage.get(f'{user_id}_{platform}_refresh')
    return token_in_redis is None


@app.teardown_appcontext
def shutdown_session(exception=None):
    if session is not None:
        session.close()


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.access')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8002,
    )
