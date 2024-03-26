from api.helpers.http_responses import ok, bad_request
from fcea_monitoreo.utils import get_collection
from api.serializers.user_serializer import UserSerializer


class GetUsersUseCase:
    def execute(self):
        try:
            data = get_collection('users', {})
            return ok(UserSerializer(data, many=True).data)

        except Exception as e:
            return bad_request([e.args])
