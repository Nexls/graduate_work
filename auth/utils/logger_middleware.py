from json import loads

from utils import context_logger
from werkzeug import Request

logger = context_logger.get(__name__)


class LoggerMiddleware:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        json_body_str = {}
        try:
            json_body = {}
        except (ValueError, AttributeError):
            json_body = {}

        query_string = request.query_string
        try:
            query_params = loads(query_string)
        except (ValueError, AttributeError):
            query_params = {}

        if hasattr(request, 'headers'):
            headers = {**request.headers}
        else:
            headers = {}

        if hasattr(request, 'args'):
            path_params = {**request.args}
        else:
            path_params = {}

        request_combined = {
            'headers': headers,
            'query': query_params,
            'json_body': json_body,
            'path_params': path_params,
        }
        context_logger.Context.set(request_combined)
        return self.app(environ, start_response)
