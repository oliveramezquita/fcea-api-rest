from api.helpers.http_responses import ok_paginated, bad_request
from fcea_monitoreo.utils import get_collection
from api.serializers.user_serializer import UserSerializer
from urllib.parse import parse_qs
from django.core.paginator import Paginator
from api.constants import DEFAULT_PAGE_SIZE


class GetUsersUseCase:
    def __init__(self, request):
        params = parse_qs(request.META['QUERY_STRING'])

        self.page = params['page'][0] if 'page' in params else 1

        self.page_size = params['page_size'][0] \
            if 'page_size' in params else DEFAULT_PAGE_SIZE

    def execute(self):
        try:
            data = get_collection('users', {'_deleted': False})
            paginator = Paginator(data, per_page=self.page_size)
            page = paginator.get_page(self.page)

            return ok_paginated(
                paginator,
                page,
                UserSerializer(data, many=True).data
            )

        except Exception as e:
            return bad_request([e.args])
