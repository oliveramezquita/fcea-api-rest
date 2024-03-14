from rest_framework.status import (
    HTTP_200_OK,
)
from django.http import JsonResponse
from api.scripts.formulas import *
from fcea_monitoreo.utils import insert_document


class SaveAnswersUseCase:
    def __init__(self, answers_raw_data):
        self.answers_raw_data = answers_raw_data

    def execute(self):
        self.save_answers_data()
        response = JsonResponse(
            {'message': 'Las respuestas fueron guardadas'}, safe=False)
        response.status_code = HTTP_200_OK

        return response

    def save_answers_data(self):
        data = {}
        for item in self.answers_raw_data:
            data['_id'] = int(generate_objectid(item.get('Nombre del sitio')))
            data['email'] = item.get('Dirección de correo electrónico')
            data['nombre_brigadistas'] = item.get(
                'Nombre de las y los brigadistas')
            data['nombre_sitio'] = item.get('Nombre del sitio')
            data['clave_sitio'] = item.get('Clave del sitio')
            data['es_sitio_referecia'] = get_es_sitio_de_referencia(
                item.get('¿Es sitio de referencia?'))
            data['sitio_referecia'] = item.get('Sitio de referencia', '')
            data['ubicacion'] = f'{item.get("Latitud")}, {item.get("Longitud")}'
            data['tipo_cuerpo_agua'] = item.get(
                'Selecciona el tipo de cuerpo de agua')
            data['fecha'] = item.get('Fecha del monitoreo')
            data['hora'] = item.get('Hora de inicio', '')
            data['temporada'] = item.get('Temporada')
            data['notas'] = item.get('Notas', '')
            insert_document('answers', data, {'_id': data['_id']})

    def test_data(self):
        data = self.answers_raw_data
        print(data)
        response = JsonResponse(data, safe=False)
        response.status_code = HTTP_200_OK

        return response
