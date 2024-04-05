from api.helpers.http_responses import created, bad_request, error
from fcea_monitoreo.utils import insert_document
from rest_framework import exceptions
from bson import ObjectId


class CreateCatalogUseCase:
    def __init__(self, catalog_raw_data):
        self.catalog_raw_data = catalog_raw_data

    def execute(self):
        self.validate_params()

        if self.insert():
            try:
                return created(['El catálogo ha sido creado correctamente'])
            except Exception as e:
                return error(e.args[0])
        return bad_request('El catálogo ya existe')

    def validate_params(self):
        # validate requiere fields
        if 'name' not in self.catalog_raw_data:
            raise exceptions.ValidationError(
                "El correo electrónico es obligatorio"
            )

        if 'values' not in self.catalog_raw_data:
            raise exceptions.ValidationError(
                "Debes agregar al menos un valor al catálogo"
            )

    def insert(self):
        self.catalog_raw_data['_id'] = ObjectId()
        return insert_document(
            'catalogs',
            self.catalog_raw_data,
            {
                'name': self.catalog_raw_data['name'],
            }
        )
