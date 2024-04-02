from api.helpers.http_responses import ok_paginated, error
from fcea_monitoreo.utils import get_collection
from api.serializers.user_serializer import UserSerializer
from urllib.parse import parse_qs
from django.core.paginator import Paginator
from api.constants import DEFAULT_PAGE_SIZE


class GetUsersUseCase:
    def __init__(self, request):
        params = parse_qs(request.META['QUERY_STRING'])

        self.page = params['page'][0] if 'page' in params else 1

        self.page_size = params['itemsPerPage'][0] \
            if 'itemsPerPage' in params else DEFAULT_PAGE_SIZE

        self.q = params['q'][0] if 'q' in params else None

        self.activated = params['activated'][0] if 'activated' in params else None

        self.institution = params['institution'][0] if 'institution' in params else None

        self.role = params['role'][0] if 'role' in params else None

        self.order_by = params['orderBy'][0] if 'orderBy' in params else None

        self.sort_list = {
            'user': 'name',
            'role': 'role',
            'institution': 'institution',
            'status': 'activated',
        }

        self.sort_by = None
        if 'sortBy' in params:
            self.sort_by = self.sort_list[params['sortBy'][0]]

    def execute(self):
        try:
            filters = {'_deleted': False}

            if self.q:
                filters['$or'] = [
                    {'name': {'$regex': self.q}},
                    {'last_name': {'$regex': self.q}},
                    {'email': {'$regex': self.q}},
                ]

            if self.role:
                filters['role'] = self.role

            if self.institution:
                filters['institution'] = self.institution

            if self.activated == 'true':
                filters['activated'] = True

            if self.activated == 'false':
                filters['activated'] = False

            if self.sort_by and self.order_by:
                data = get_collection(
                    'users', filters, self.sort_by, self.order_by)
            else:
                data = get_collection('users', filters)
            paginator = Paginator(data, per_page=self.page_size)
            page = paginator.get_page(self.page)

            return ok_paginated(
                paginator,
                page,
                UserSerializer(data, many=True).data
            )

        except Exception as e:
            return error(e.args[0])
