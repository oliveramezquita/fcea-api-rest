from rest_framework import exceptions
from fcea_monitoreo.utils import insert_document
from api.helpers.http_responses import created, bad_request, error
from bson import ObjectId
from urllib import parse
from fcea_monitoreo.settings import ADMIN_URL
from fcea_monitoreo.functions import encrypt, send_email
import re


class CreateUserUseCase:
    def __init__(self, user_raw_data):
        self.user_raw_data = user_raw_data
        self.user_raw_data['activated'] = False
        self.user_raw_data['_deleted'] = False

    def execute(self):
        self.validate_params()
        if self.insert():
            try:
                self.send_link()
                return created(['El usuario ha sido creado correctamente'])
            except Exception as e:
                return error(e.args[0])
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
        roles = ['SUPER_ADMIN', 'ADMIN', 'BRIGADIER']
        if self.user_raw_data['role'] not in roles:
            raise exceptions.ValidationError(
                "El rol es incorrecto"
            )

    def insert(self):
        self.user_raw_data['_id'] = ObjectId()
        return insert_document(
            'users',
            self.user_raw_data,
            {
                'email': self.user_raw_data['email'],
                '_deleted': False,
            })

    def send_link(self):
        key = parse.quote_plus(encrypt(str(self.user_raw_data['_id'])))
        link = f"{ADMIN_URL}register?rt={key}"
        send_email(
            template="mail_templated/register.html",
            context={
                'subject': 'Invitación para el registro del monitoreo de la calidad del agua',
                'email': self.user_raw_data['email'],
                'link_href': link,
            },
        )
