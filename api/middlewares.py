from rest_framework import exceptions
from json.decoder import JSONDecodeError
from fcea_monitoreo.functions import decode_user
from fcea_monitoreo.utils import get_collection
from rest_framework import authentication


class InvalidAccessTokenError(Exception):
    pass


class FceaAuthenticationMiddleware(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("authorization", None)
        try:
            if not token:
                raise exceptions.AuthenticationFailed(
                    'Token de acceso no válido')

            token = token.split(" ")[1]
            user = self.get_user_from_token(token)
            return (user, None)

        except InvalidAccessTokenError as e:
            raise exceptions.NotFound(
                "No puedo obtener información con el token actual")

    def get_user_from_token(self, token: str):
        payload = decode_user(token)
        user_data = get_collection('users', {
            '_id': payload['_id'],
            'email': payload['email'],
            'role': payload['role']
        })

        if user_data is None:
            raise InvalidAccessTokenError

        return user_data
