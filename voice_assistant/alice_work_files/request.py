from typing import Any, Optional

from aiohttp import ClientSession


class AliceRequest:
    def __init__(
        self,
        request_body: dict[str, Any],
        session: ClientSession
    ) -> None:
        self.request_body = request_body
        self.session = session

    def __getitem__(self, key):
        return self.request_body[key]

    @property
    def intents(self):
        # TODO: return the most relevant intent
        return self.request_body['request'].get('nlu', {}).get('intents', {})

    @property
    def type(self):
        return self.request_body.get('request', {}).get('type')

    @property
    def slots(self):
        slots = {}
        request_intents = self.request_body['request']['nlu']['intents']
        intent = list(request_intents.keys())[0]

        slots = self.request_body['request']['nlu']['intents'][intent]['slots']

        try:
            slot_type = slots['type']['type']
            slot_value = slots['type']['value']
        except KeyError:
            slot_type = slots['period']['type']
            slot_value = slots['period']['value']

        return {slot_type: slot_value}

    @property
    def original_utterance(self):
        return self.request_body.get('request', {}).get('original_utterance')
