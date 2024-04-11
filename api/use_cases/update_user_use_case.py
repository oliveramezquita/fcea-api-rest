from api.helpers.http_responses import ok, error, not_found
from rest_framework import exceptions
from fcea_monitoreo.utils import update_document, get_collection
from api.serializers.user_serializer import UserSerializer
from bson import ObjectId
import re


class UpdateUserUseCase:
    def __init__(self, user_raw_data, user_id):
        self.user_raw_data = user_raw_data
        self.user_id = user_id

    def execute(self):
        self.validate_params()
        user = get_collection('users', {
            '_deleted': False,
            '_id': ObjectId(self.user_id)
        })
        if not user:
            return not_found(
                f"Usuario no encontrado con el id: {str(self.user_id)}"
            )
        try:
            data = self.update()
            return ok(UserSerializer(data).data)
        except Exception as e:
            return error(e.args[0])

    def delete(self):
        user = get_collection('users', {
            '_deleted': False,
            '_id': ObjectId(self.user_id)
        })
        if not user:
            return not_found(
                f"Usuario no encontrado con el id: {str(self.user_id)}"
            )
        try:
            self.update()
            return ok(['Usuario eliminado exitosamente'])
        except Exception as e:
            return error(e.args[0])

    def validate_params(self):
        # validate email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if 'email' in self.user_raw_data and not re.fullmatch(regex, self.user_raw_data['email']):
            raise exceptions.ValidationError(
                "El correo electrónico es incorrecto"
            )

        # set default values
        if '_id' in self.user_raw_data:
            del self.user_raw_data['_id']
        if 'short_name' in self.user_raw_data:
            del self.user_raw_data['short_name']
        if 'full_name' in self.user_raw_data:
            del self.user_raw_data['full_name']

    def update(self):
        return update_document(
            'users',
            {'_id': ObjectId(self.user_id)},
            self.user_raw_data
        )
