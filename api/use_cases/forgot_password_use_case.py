from api.helpers.http_responses import ok, not_found
from rest_framework import exceptions
from fcea_monitoreo.utils import get_collection
from fcea_monitoreo.functions import send_email, encrypt
from fcea_monitoreo.settings import ADMIN_URL
from urllib import parse
import re


class ForgotPasswordUseCase:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def execute(self):
        self.validate_params()
        user = get_collection('users', {
            'email': self.raw_data['email'],
            'activated': True,
            '_deleted': False
        })
        if not user:
            return not_found(
                f"Usuario no encontrado con el email: {self.raw_data['email']}"
            )
        self.send_link(user[0])
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

    def send_link(self, user):
        key = parse.quote_plus(encrypt(str(user['_id'])))
        link = f"{ADMIN_URL}reset-password?rt={key}"
        send_email(
            template="mail_templated/reset-password.html",
            context={
                'subject': 'Solicitud de cambio de contraseña',
                'email': self.raw_data['email'],
                'link_href': link,
            },
        )
