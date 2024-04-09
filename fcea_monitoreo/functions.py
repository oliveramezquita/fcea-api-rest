import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from decouple import config
from fcea_monitoreo.requests import google_request
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
    response = google_request(lat, lng)
    data = response.json()['results'][0]
    return "{:.2f}".format(data['elevation'])


def send_email(template, context):
    to = []
    to.append(context['email'])
    send_mail(
        template_name=template,
        context=context,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=to
    )
