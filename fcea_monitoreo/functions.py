import base64
import jwt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from decouple import config
from fcea_monitoreo.requests import get_elevation_request, get_geocode_request
from mail_templated import send_mail
from django.conf import settings

key = config('ENCRYPT_KEY')


def encrypt(raw):
    raw = pad(raw.encode(), 16)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(raw))


def decrypt(enc):
    enc = base64.b64decode(enc)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    return unpad(cipher.decrypt(enc), 16)


def get_altitude(lat, lng):
    response = get_elevation_request(lat, lng)
    data = response.json()['results'][0]
    return "{:.2f}".format(data['elevation'])


def get_geocode(lat, lng):
    response = get_geocode_request(lat, lng)
    data = response.json()['results'][0]['address_components']
    locality = next(
        (item for item in data if 'locality' in item['types']), None)
    administrative_area_level_1 = next(
        (item for item in data if 'administrative_area_level_1' in item['types']), None)
    return locality['long_name'], administrative_area_level_1['long_name']


def send_email(template, context):
    to = []
    to.append(context['email'])
    send_mail(
        template_name=template,
        context=context,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=to
    )


def encode_user(user):
    encoded_data = jwt.encode(payload=user,
                              key=config('AUTH_SECRET'),
                              algorithm="HS256")
    return encoded_data


def decode_user(token):
    decoded_data = jwt.decode(jwt=token,
                              key=config('AUTH_SECRET'),
                              algorithms=["HS256"])
    return decoded_data
