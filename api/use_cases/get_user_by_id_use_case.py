from fcea_monitoreo.utils import get_collection
from api.helpers.http_responses import error, ok, not_found
from api.serializers.user_serializer import UserSerializer
from bson import ObjectId


class GetUserByIdUseCase:
    def __init__(self, request, user_id):
        self.user_id = user_id

    def execute(self):
        try:
            users = get_collection('users', {
                '_deleted': False,
                '_id': ObjectId(self.user_id)
            })

            if not users:
                return not_found(
                    f"No user found with id {str(self.user_id)}"
                )

            return ok(UserSerializer(users[0]).data)

        except Exception as e:
            return error([e.args[0]])
