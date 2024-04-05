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
                f"No user found with id {str(self.user_id)}"
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
                f"No user found with id {str(self.user_id)}"
            )
        try:
            self.update()
            return ok(['Usuario eliminado exitosamente'])
        except Exception as e:
            return error(e.args[0])

    def validate_params(self):
        if '_id' in self.user_raw_data:
            del self.user_raw_data['_id']

        # validate requiere fields
        if 'email' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "El correo electrónico es obligatorio"
            )
        if 'name' not in self.user_raw_data or 'last_name' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "El nombre y los apellidos son obligatorios"
            )
        if 'phone' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "El télefono es obligatorio"
            )

        # validate email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex, self.user_raw_data['email']):
            raise exceptions.ValidationError(
                "El correo electrónico es incorrecto"
            )

    def update(self):
        return update_document(
            'users',
            {'_id': ObjectId(self.user_id)},
            self.user_raw_data
        )
