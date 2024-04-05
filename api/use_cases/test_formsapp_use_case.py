from rest_framework.status import (
    HTTP_200_OK,
)
from django.http import JsonResponse
from fcea_monitoreo.functions import encrypt
from urllib import parse


class TestFormsappUseCase:

    def encrypt_test(self, raw_data):
        key = parse.quote_plus(encrypt(raw_data['id']))

        response = JsonResponse([key], safe=False)
        response.status_code = HTTP_200_OK

        return response
