import uuid
from collections import Callable

from core import context_logger
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import Response
import orjson

logger = context_logger.get(__name__)


class LoggerRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        original_handler_name = self.dependant.cache_key[0]

        async def custom_route_handler(request: Request) -> Response:
            request_text = await request.body()
            try:
                json_body = orjson.loads(request_text)
            except (ValueError, AttributeError):
                json_body = {}

            headers = {**request.headers}
            if 'X-REQUEST-ID' not in headers:
                headers['X-REQUEST-ID'] = str(uuid.uuid4())
                request._headers = Headers(headers=headers)

            request_combined = {
                'headers': {**request.headers},
                'query': {**request.query_params},
                'json_body': json_body,
                'path_params': {**request.path_params},
            }
            context_logger.Context.set(request_combined)
            logger.info(f'receive request for {original_handler_name.__name__}')

            try:
                response = await original_route_handler(request)
            except Exception as e:
                logger.exception(f'during {original_handler_name.__name__} an error occurred: {str(e)}')
                return ORJSONResponse(
                    {
                        'result_code': 'error',
                        'description': str(e)
                    },
                    status_code=500,
                )
            if hasattr(response, 'body'):
                logger.info(f'response {original_handler_name.__name__} with {response.body = }')
            return response

        return custom_route_handler
