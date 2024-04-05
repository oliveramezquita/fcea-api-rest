from api.helpers.http_responses import ok, error, not_found
from fcea_monitoreo.utils import update_document, get_collection
from rest_framework import exceptions
from api.serializers.catalog_serializer import CatalogSerializer
from bson import ObjectId


class UpdateCatalogUseCase:
    def __init__(self, catalog_raw_data, catalog_id):
        self.catalog_raw_data = catalog_raw_data
        self.catalog_id = catalog_id

    def execute(self):
        self.validate_params()
        catalog = get_collection('catalogs', {
            '_id': ObjectId(self.catalog_id)
        })
        if not catalog:
            return not_found(
                f"No catalog found with id {str(self.catalog_id)}"
            )
        try:
            data = self.update()
            return ok(CatalogSerializer(data).data)
        except Exception as e:
            return error(e.args[0])

    def validate_params(self):
        if '_id' in self.catalog_raw_data:
            del self.catalog_raw_data['_id']

        if 'values' not in self.catalog_raw_data:
            raise exceptions.ValidationError(
                "Debes agregar al menos un valor al catálogo"
            )

    def update(self):
        return update_document(
            'catalogs',
            {'_id': ObjectId(self.catalog_id)},
            self.catalog_raw_data
        )
