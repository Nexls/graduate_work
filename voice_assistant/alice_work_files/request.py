class AliceRequest:
    def __init__(self, request_body):
        self.request_body = request_body

    def __getitem__(self, key):
        return self.request_body[key]

    @property
    def intents(self):
        return self.request_body['request'].get('nlu', {}).get('intents', {})

    @property
    def type(self):
        return self.request_body.get('request', {}).get('type')

    @property
    def slots(self):
        slots = {}
        request_intents = self.request_body['request']['nlu']['intents']

        # ебучие костыли из-за формата запроса яндекса (и моего аутизма)
        for intent in request_intents:
            try:
                slot_type = self.request_body['request']['nlu']['intents'][intent]['slots']['type']['type']
                slot_value = self.request_body['request']['nlu']['intents'][intent]['slots']['type']['value']
            except KeyError:
                slot_type = self.request_body['request']['nlu']['intents'][intent]['slots']['period']['type']
                slot_value = self.request_body['request']['nlu']['intents'][intent]['slots']['period']['value']
            finally:
                slots = {slot_type:slot_value}
        return slots

    @property
    def original_utterance(self):
        return self.request_body.get('request', {}).get('original_utterance')