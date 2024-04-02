from fcea_monitoreo.utils import distinct_collection
from api.helpers.http_responses import ok


class GetInfoFromUsersUseCase:

    def institutions_list(self):
        data = distinct_collection('users', 'institution')
        return ok(data)
