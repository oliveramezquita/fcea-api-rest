from fcea_monitoreo.utils import get_collection
from rest_framework import exceptions
from api.helpers.http_responses import ok, bad_request
from api.serializers.user_serializer import UserSerializer
from rest_framework.status import HTTP_403_FORBIDDEN
import re
import bcrypt


class LoginUseCase:
    def __init__(self, login_raw_data):
        self.login_raw_data = login_raw_data
        self.user = get_collection(
            'users', {'email': self.login_raw_data['email']})

    def execute(self):
        self.validate_params()
        if self.authentication():
            return ok(UserSerializer(self.user[0]).data)
        return bad_request('Acceso incorrecto', HTTP_403_FORBIDDEN)

    def validate_params(self):

        # validate requiere fields
        if 'email' not in self.login_raw_data:
            raise exceptions.ValidationError(
                "El correo electrónico es obligatorio"
            )
        if 'password' not in self.login_raw_data:
            raise exceptions.ValidationError(
                "La contraseña es obligatorio"
            )

        # validate email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex, self.login_raw_data['email']):
            raise exceptions.ValidationError(
                "El correo electrónico es incorrecto"
            )

        # validate if the user exists
        if not self.user:
            raise exceptions.ValidationError(
                "El correo electrónico no ha sido registrado"
            )

        # validate activated
        if not self.user[0]['activated']:
            raise exceptions.ValidationError(
                "Revisa en tu correo electrónico el enlace para registrarte"
            )

    def authentication(self):
        # validate authentication
        password = str(self.login_raw_data['password']).encode('utf-8')
        if bcrypt.checkpw(password, self.user[0]['password']):
            return True
