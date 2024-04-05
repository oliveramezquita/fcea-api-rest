from api.helpers.http_responses import ok, not_found, error
from fcea_monitoreo.utils import get_collection
from api.serializers.catalog_serializer import CatalogSerializer
from bson import ObjectId


class GetCatalogByIdUseCase:
    def __init__(self, request, catalog_id):
        self.catalog_id = catalog_id

    def execute(self):
        try:
            catalog = get_collection('catalogs', {
                '_id': ObjectId(self.catalog_id)
            })

            if not catalog:
                return not_found(
                    f"No user found with id {str(self.catalog_id)}"
                )

            return ok(CatalogSerializer(catalog[0]).data)

        except Exception as e:
            return error(e.args[0])
