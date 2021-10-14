from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from settings import PROJECT_NAME

app = FastAPI(
    title=PROJECT_NAME,
    docs_url='/api/docs/',
    openapi_url='/api/docs.json',
    default_response_class=ORJSONResponse,
    version='1.0.0',
)
