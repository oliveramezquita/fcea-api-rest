from rest_framework import exceptions
from fcea_monitoreo.utils import insert_document
from api.helpers.http_responses import ok, bad_request
from bson import ObjectId
import re


class CreateUserUseCase:
    def __init__(self, user_raw_data):
        self.user_raw_data = user_raw_data
        self.user_raw_data['activated'] = False
        self.user_raw_data['_deleted'] = False

    def execute(self):
        self.validate_params()
        if self.insert():
            # TODO: Enviar enlace para realizar el registro
            return ok(['El usuario ha sido creado correctamente'])
        return bad_request('El usuario ya existe')

    def validate_params(self):
        # validate requiere fields
        if 'email' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "El correo electrónico es obligatorio"
            )

        if 'role' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "El cargo del usuario es obligatorio"
            )

        # validate email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex, self.user_raw_data['email']):
            raise exceptions.ValidationError(
                "El correo electrónico es incorrecto"
            )

        # validate rol
        roles = ['ADMIN', 'BRIGADIER']
        if self.user_raw_data['role'] not in roles:
            raise exceptions.ValidationError(
                "El rol es incorrecto"
            )

    def insert(self):
        self.user_raw_data['_id'] = ObjectId()
        return insert_document('users', self.user_raw_data, {'email': self.user_raw_data['email']})
