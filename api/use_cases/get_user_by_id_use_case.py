from fcea_monitoreo.utils import get_collection
from api.helpers.http_responses import error, ok, not_found
from api.serializers.user_serializer import UserSerializer
from bson import ObjectId


class GetUserByIdUseCase:
    def __init__(self, request, user_id):
        self.user_id = user_id

    def execute(self):
        try:
            user = get_collection('users', {'_id': ObjectId(self.user_id)})
            if not user:
                return not_found(
                    f"Usuario no encontrado con el id: {str(self.user_id)}"
                )

            return ok(UserSerializer(user[0]).data)

        except Exception as e:
            return error(e.args[0])

    def not_registered(self):
        try:
            user = get_collection('users', {'_id': ObjectId(self.user_id)})
            if not user:
                return not_found(
                    f"Usuario no encontrado con el id: {str(self.user_id)}"
                )

            return ok(UserSerializer(user[0]).data)

        except Exception as e:
            return error(e.args[0])
