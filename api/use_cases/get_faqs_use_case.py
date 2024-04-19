from api.helpers.http_responses import ok
import json


class GetFaqsUseCase:
    def execute(self):
        with open('./api/assets/faqs.json') as f:
            faqs = json.load(f)
        return ok(faqs)
