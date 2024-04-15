from api.helpers.http_responses import ok
from fcea_monitoreo.utils import get_collection
from api.serializers.catalog_serializer import CatalogSerializer


class GetCatalogsUseCase:
    def execute(self):
        data = get_collection('catalogs', {'_deleted': False})
        return ok(CatalogSerializer(data, many=True).data)
