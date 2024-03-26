from rest_framework import exceptions
from fcea_monitoreo.utils import update_document
from api.helpers.http_responses import ok
import bcrypt


class ResetPasswordUseCase:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def execute(self):
        self.validate_params()
        self.update()
        return ok(['La contraseña ha sido restablecida correctamente'])

    def validate_params(self):
        # validate requiere fields
        if 'email' not in self.raw_data:
            raise exceptions.ValidationError(
                "El correo electrónico es obligatorio"
            )
        if 'password' not in self.raw_data or 'confirm_password' not in self.raw_data:
            raise exceptions.ValidationError(
                "La contraseña y la confirmación de la contraseña son obligatorios"
            )

        # validate confirm password
        if self.raw_data['password'] != self.raw_data['confirm_password']:
            raise exceptions.ValidationError(
                "La contraseña y la confirmación de la contraseña no coinciden"
            )

    def update(self):
        self.encrypt_passwpord()
        return update_document(
            'users',
            {'email': self.raw_data['email']},
            {'password': self.raw_data['password']}
        )

    def encrypt_passwpord(self):
        self.raw_data['password'] = str(
            self.raw_data['password']).encode('utf-8')
        self.raw_data['password'] = bcrypt.hashpw(
            self.raw_data['password'], bcrypt.gensalt(10))
