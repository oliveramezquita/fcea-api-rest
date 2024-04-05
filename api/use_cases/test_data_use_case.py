from rest_framework.status import (
    HTTP_200_OK,
)
from django.http import JsonResponse
from fcea_monitoreo.functions import encrypt
from urllib import parse


class TestDataUseCase:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def test_data(self):
        data = self.raw_data
        print(data)
        response = JsonResponse(data, safe=False)
        response.status_code = HTTP_200_OK

        return response

    def encrypt_test(self, raw_data):
        key = parse.quote_plus(encrypt(raw_data['id']))

        response = JsonResponse([key], safe=False)
        response.status_code = HTTP_200_OK

        return response
