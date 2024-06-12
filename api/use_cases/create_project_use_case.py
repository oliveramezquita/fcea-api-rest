from rest_framework import exceptions
from fcea_monitoreo.utils import insert_document
from api.helpers.http_responses import created, bad_request, error
from bson import ObjectId


class CreateProjectUseCase:
    def __init__(self, project_raw_data):
        self.project_raw_data = project_raw_data
        self.project_raw_data['activated'] = True
        self.project_raw_data['rfs_data'] = {}
        self.project_raw_data['its_data'] = {}
        self.project_raw_data['_deleted'] = False

    def execute(self):
        self.validate_params()
        if self.insert():
            try:
                return created(['El monitoreo ha sido creado correctamente'])
            except Exception as e:
                return error(e.args[0])
        return bad_request('El monitoreo ya existe')

    def validate_params(self):
        # validate requiere fields
        if 'name' not in self.project_raw_data:
            raise exceptions.ValidationError(
                "El nombre del proyecto es obligatorio"
            )

        if 'season' not in self.project_raw_data:
            raise exceptions.ValidationError(
                "La temporada es obligatoria"
            )

        if 'year' not in self.project_raw_data:
            raise exceptions.ValidationError(
                "El año es obligatorio"
            )

        if 'month' not in self.project_raw_data:
            raise exceptions.ValidationError(
                "El mes es obligatorio"
            )

        if 'admin_users' not in self.project_raw_data:
            self.project_raw_data['admin_users'] = []

        # validate rol
        seasons = ['Secas', 'Lluvias']
        if self.project_raw_data['season'] not in seasons:
            raise exceptions.ValidationError(
                "La temporada es incorrecta"
            )

    def insert(self):
        self.project_raw_data['_id'] = ObjectId()
        try:
            return insert_document(
                'projects',
                self.project_raw_data,
                {
                    'name': self.project_raw_data['name'],
                    'season': self.project_raw_data['season'],
                    'year': int(self.project_raw_data['year']),
                    'month': self.project_raw_data['month'],
                    '_deleted': False,
                })
        except Exception as e:
            return error(e.args[0])
