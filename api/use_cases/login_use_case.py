from fcea_monitoreo.utils import get_collection
from fcea_monitoreo.functions import encode_user
from rest_framework import exceptions
from api.helpers.http_responses import bad_request
from rest_framework.status import HTTP_403_FORBIDDEN
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import re
import bcrypt
import json


class LoginUseCase:
    def __init__(self, login_raw_data):
        self.login_raw_data = login_raw_data
        self.user = get_collection('users', {
            'email': self.login_raw_data['email'],
            'activated': True,
            '_deleted': False,
        })

    def execute(self):
        self.validate_params()
        if self.authentication():
            auth_data = self.auth_data()
            dump = json.dumps(auth_data)
            print(f'dump: {dump}')
            return HttpResponse(dump, content_type='application/json')
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

    def auth_data(self):
        rules = {
            'SUPER_ADMIN': {
                'action': 'manage',
                'subject': 'all'
            },
            'ADMIN': {
                'action': 'manage',
                'subject': 'admin'
            },
            'BRIGADIER': {
                'action': 'read',
                'subject': 'brigadier'
            }
        }
        user_data = {
            '_id': str(self.user[0]['_id']),
            'fullName': f"{self.user[0]['name']} {self.user[0]['last_name']}",
            'username': self.get_short_name(),
            'avatar': None,
            'email': self.user[0]['email'],
            'role': self.user[0]['role'],
        }
        return {
            'userAbilityRules': [rules[self.user[0]['role']]],
            'accessToken': encode_user(user_data),
            'userData': user_data
        }

    def get_short_name(self):
        last_name = self.user[0]['last_name'].split()
        return f"{self.user[0]['name']} {last_name[0]}"
