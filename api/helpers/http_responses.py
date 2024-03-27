from django.http import JsonResponse
from rest_framework.status import (
    HTTP_200_OK, HTTP_400_BAD_REQUEST
)


def build_response_with_pagination(paginator, page, data):
    payload = {
        "total_pages": paginator.num_pages,
        "total_elements": paginator.count,
        "last": not page.has_next(),
        "page_size": len(page),
        "page": page.number,
        "data": data
    }
    return JsonResponse(payload, safe=False)


def ok(data):
    response = JsonResponse(data, safe=False)
    response.status_code = HTTP_200_OK
    return response


def ok_paginated(paginator, page, data):
    response = build_response_with_pagination(paginator, page, data)
    response.status_code = HTTP_200_OK
    return response


def bad_request(message, status_code=HTTP_400_BAD_REQUEST):
    response = JsonResponse([message], safe=False)
    response.status_code = status_code
    return response
