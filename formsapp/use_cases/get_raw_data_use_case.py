from fcea_monitoreo.utils import get_collection
from django.http import HttpResponse
import json


class GetRawDataUseCase:
    def __init__(self, index):
        self.index = index

    def execute(self):
        raw_data = get_collection('formsapp_raw_data', {})
        if raw_data[self.index]:
            del raw_data[self.index]['_id']
            dump = json.dumps(raw_data[self.index])
            return HttpResponse(dump, content_type='application/json')
        return HttpResponse()
