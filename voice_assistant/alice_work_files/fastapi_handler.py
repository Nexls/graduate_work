import typing

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from request import Request
from scenes import DEFAULT_SCENE, SCENES
from state import STATE_REQUEST_KEY

app = FastAPI()


class RequestModel(BaseModel):
    req1: typing.Any


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
    request = Request(event)
    current_scene_id = event.get('state', {}).get(STATE_REQUEST_KEY, {}).get('scene')

    if current_scene_id is None:
        return DEFAULT_SCENE().reply(request)

    current_scene = SCENES.get(current_scene_id, DEFAULT_SCENE)()
    next_scene = current_scene.move(request)

    if next_scene is not None:
        print(f'Moving from scene {current_scene.id()}, to {next_scene.id()}')
        return next_scene.reply(request)
    else:
        print(f'Failed to parse user request at scene {current_scene.id()}')
        return current_scene.fallback(request)


@app.post("/")
async def root(request: RequestModel):
    print(request.json)
    return handler(request.json, None)

if __name__ == '__main__':
    uvicorn.run(app, port=5001, host='0.0.0.0',)
