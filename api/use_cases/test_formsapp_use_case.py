from rest_framework.status import (
    HTTP_200_OK,
)
from django.http import JsonResponse
from api.scripts.formsapp_parse import get_mapped_data
from fcea_monitoreo.functions import encrypt
from urllib import parse


class TestFormsappUseCase:

    def mapped_data(self):
        data = get_mapped_data()
        print(data)
        response = JsonResponse(data, safe=False)
        response.status_code = HTTP_200_OK

        return response

    def encrypt_test(self, raw_data):
        key = parse.quote_plus(encrypt(raw_data['id']))

        response = JsonResponse([key], safe=False)
        response.status_code = HTTP_200_OK

        return response
