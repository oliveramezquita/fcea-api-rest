from rest_framework.status import (
    HTTP_200_OK,
)
from django.http import JsonResponse
from fcea_monitoreo.functions import encrypt
from urllib import parse
from fcea_monitoreo.functions import send_email, get_geocode
from fcea_monitoreo.utils import get_collection
from bs4 import BeautifulSoup
import requests


class TestDataUseCase:
    def __init__(self, raw_data):
        self.raw_data = raw_data

    def test_data(self):
        data = self.raw_data
        print(data)
        response = JsonResponse(data, safe=False)
        response.status_code = HTTP_200_OK

        return response

    def encrypt_test(self):
        key = parse.quote_plus(encrypt(self.raw_data['id']))

        response = JsonResponse([key], safe=False)
        response.status_code = HTTP_200_OK

        return response

    def test_email_register(self):
        reponse_email = send_email(
            template="mail_templated/register.html",
            context={
                'subject': 'Invitación para el registro del monitoreo de la calidad del agua',
                'email': self.raw_data['email'],
                'link_href': 'http://localhost:5173/register',
            },
        )

        response = JsonResponse([reponse_email], safe=False)
        response.status_code = HTTP_200_OK

        return response

    def test_email_form(self):
        reponse_email = send_email(
            template="mail_templated/form.html",
            context={
                'subject': f"Formato de campo digital cuenca: {self.raw_data['project']}",
                'email': self.raw_data['email'],
                'user_name': self.raw_data['user_name'],
                'project': self.raw_data['project'],
                'link_href': 'http://localhost:5173/'
            },
        )

        response = JsonResponse([reponse_email], safe=False)
        response.status_code = HTTP_200_OK

        return response

    def test_email_reset_password(self):
        reponse_email = send_email(
            template="mail_templated/reset-password.html",
            context={
                'subject': 'Solicitud de cambio de contraseña',
                'email': self.raw_data['email'],
                'link_href': 'http://localhost:5173/reset-password',
            },
        )

        response = JsonResponse([reponse_email], safe=False)
        response.status_code = HTTP_200_OK

        return response

    def test_locations(self):
        city, state = get_geocode(self.raw_data['lat'], self.raw_data['lng'])

        response = JsonResponse([city, state], safe=False)
        response.status_code = HTTP_200_OK

        return response

    def test_scrape_url_images(self):
        url = "https://forms.app/recordimage/6612f856d861385a599f264b/bde0eaac-f516-11ee-aae9-0242ac120004?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbnN3ZXJJZCI6IjY2MTJmODU2ZDg2MTM4NWE1OTlmMjY0YiIsImZvcm1JZCI6IjY2MGY3OGVkMDkxNjYxZDIzODg1MjQ2YiIsImlhdCI6MTcxMjUxOTI1NCwiZXhwIjoxNzQzNjIzMjU0fQ.OlsaBOamcavezZJioqk4-bFXl2rhrKycjXzdVOHoI4Y"
        # Execute GET request
        response = requests.get(url)
        # Parse the HTML document from the source code using BeautifulSoup
        html = BeautifulSoup(response.text, 'html.parser')
        print(html)

        response = JsonResponse([], safe=False)
        response.status_code = HTTP_200_OK
        return response
