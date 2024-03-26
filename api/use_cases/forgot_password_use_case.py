from api.helpers.http_responses import ok
from rest_framework import exceptions
import re


class ForgotPasswordUseCase:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def execute(self):
        self.validate_params()
        # TODO: Enviar enlace para restablecer la contraseña
        return ok([f"Se ha enviado el enlace para restablecer la contraseña al correo electrónico: {self.raw_data['email']}"])

    def validate_params(self):
        # validate requiere fields
        if 'email' not in self.raw_data:
            raise exceptions.ValidationError(
                "El correo electrónico es obligatorio"
            )

        # validate email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex, self.raw_data['email']):
            raise exceptions.ValidationError(
                "El correo electrónico es incorrecto"
            )
