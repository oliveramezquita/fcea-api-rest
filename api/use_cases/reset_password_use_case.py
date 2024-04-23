from rest_framework import exceptions
from fcea_monitoreo.utils import update_document, get_collection
from api.helpers.http_responses import ok, not_found, bad_request
from rest_framework.status import HTTP_403_FORBIDDEN
from bson import ObjectId
import bcrypt


class ResetPasswordUseCase:
    def __init__(self, raw_data):
        self.raw_data = raw_data
        if '_id' in self.raw_data:
            self.user = get_collection(
                'users', {'_id': ObjectId(self.raw_data['_id'])})

    def validate_params(self):
        # validate requiere fields
        if '_id' not in self.raw_data:
            raise exceptions.ValidationError(
                "El id del usuario es obligatorio"
            )

        if 'newPassword' not in self.raw_data or 'confirmPassword' not in self.raw_data:
            raise exceptions.ValidationError(
                "La nueva contraseña y la confirmación de la contraseña son obligatorios"
            )

        # validate confirm password
        if self.raw_data['newPassword'] != self.raw_data['confirmPassword']:
            raise exceptions.ValidationError(
                "La nueva contraseña y la confirmación de la contraseña no coinciden"
            )

    def reset_password_inside(self):
        self.validate_params()
        if not self.user:
            return not_found(
                f"Usuario no encontrado con el id: {str(self.raw_data['_id'])}"
            )
        if 'currentPassword' not in self.raw_data:
            raise exceptions.ValidationError(
                "La contraseña actual es obligatoria para restablecer una nueva"
            )
        if self.raw_data['currentPassword'] == self.raw_data['newPassword']:
            raise exceptions.ValidationError(
                "La nueva contraseña no puede ser igual a la actual"
            )
        if self.authentication():
            self.encrypt_passwpord()
            update_document(
                'users',
                {'_id': ObjectId(self.raw_data['_id'])},
                {'password': self.raw_data['password']},
            )
            return ok(["La nueva contraseña se ha restablecido exitosamente"])
        return bad_request('Acceso incorrecto', HTTP_403_FORBIDDEN)

    def reset_password_outside(self):
        self.validate_params()
        if not self.user:
            return not_found(
                f"Usuario no encontrado con el id: {str(self.raw_data['_id'])}"
            )
        self.encrypt_passwpord()
        update_document(
            'users',
            {'_id': ObjectId(self.raw_data['_id'])},
            {'password': self.raw_data['password']},
        )
        return ok(["La nueva contraseña se ha restablecido exitosamente"])

    def authentication(self):
        # validate authentication
        password = str(self.raw_data['currentPassword']).encode('utf-8')
        if bcrypt.checkpw(password, self.user[0]['password']):
            return True

    def encrypt_passwpord(self):
        self.raw_data['password'] = str(
            self.raw_data['newPassword']).encode('utf-8')
        self.raw_data['password'] = bcrypt.hashpw(
            self.raw_data['password'], bcrypt.gensalt(10))
