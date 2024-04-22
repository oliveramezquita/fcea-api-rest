from api.helpers.http_responses import ok, error, not_found
from rest_framework import exceptions
from fcea_monitoreo.utils import update_document, get_collection
from api.serializers.user_serializer import UserSerializer
from bson import ObjectId
# from django.contrib.auth.models import User
# from rest_framework.authtoken.models import Token
import re
import bcrypt


class RegisterUserUseCase:
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

    def validate_params(self):
        # validate requiere fields
        if 'email' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "El correo electrónico es obligatorio"
            )
        if 'password' not in self.user_raw_data or 'confirm_password' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "La contraseña y la confirmación de la contraseña son obligatorios"
            )
        if 'name' not in self.user_raw_data or 'last_name' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "El nombre y los apellidos son obligatorios"
            )
        if 'phone' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "El télefono es obligatorio"
            )
        if 'institution' not in self.user_raw_data:
            raise exceptions.ValidationError(
                "La institución goburnamental o educativa es obligatoria"
            )
        else:
            self.user_raw_data['institution'] = self.user_raw_data['institution'].strip(
            )

        # validate email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex, self.user_raw_data['email']):
            raise exceptions.ValidationError(
                "El correo electrónico es incorrecto"
            )

        # validate confirm password
        if self.user_raw_data['password'] != self.user_raw_data['confirm_password']:
            raise exceptions.ValidationError(
                "La contraseña y la confirmación de la contraseña no coinciden"
            )

        # set default values
        self.encrypt_passwpord()
        self.user_raw_data['activated'] = True
        del self.user_raw_data['confirm_password']

    def update(self):
        # user = User.objects.create_user(
        #     username=self.user_raw_data['email'],
        #     password=self.user_raw_data['password']
        # )
        # Token.objects.create(user=user)
        return update_document(
            'users',
            {'_id': ObjectId(self.user_id)},
            self.user_raw_data
        )

    def encrypt_passwpord(self):
        self.user_raw_data['password'] = str(
            self.user_raw_data['password']).encode('utf-8')
        self.user_raw_data['password'] = bcrypt.hashpw(
            self.user_raw_data['password'], bcrypt.gensalt(10))
