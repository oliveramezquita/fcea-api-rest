from rest_framework.status import (
    HTTP_200_OK,
)
from django.http import JsonResponse
from api.scripts.formsapp_parse import get_mapped_data


class TestFormsappUseCase:

    def mapped_data(self):
        data = get_mapped_data()
        print(data)
        response = JsonResponse(data, safe=False)
        response.status_code = HTTP_200_OK

        return response
