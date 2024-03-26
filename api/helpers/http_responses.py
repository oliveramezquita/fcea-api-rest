from django.http import JsonResponse
from rest_framework.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST
)


def ok(data):
    response = JsonResponse(data, safe=False)
    response.status_code = HTTP_200_OK
    return response


def bad_request(message, status_code=HTTP_400_BAD_REQUEST):
    response = JsonResponse([message], safe=False)
    response.status_code = status_code
    return response
