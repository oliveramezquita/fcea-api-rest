from rest_framework import serializers
from api.models import Project
from api.scripts.json_encoder import JSONEncoder
from fcea_monitoreo.utils import get_collection


class ProjectSerializer(serializers.ModelSerializer):
    reference_sites_data = serializers.SerializerMethodField(
        "get_reference_sites"
    )

    interest_sites_data = serializers.SerializerMethodField(
        "get_interest_sites"
    )

    def get_reference_sites(self, data):
        sites = get_collection(
            'sites', {'project_id': data['_id'], 'es_sitio_referencia': True})
        if sites:
            data['rfs_data']['answers'] = sites
        return JSONEncoder().encode(data['rfs_data'])

    def get_interest_sites(self, data):
        sites = get_collection(
            'sites', {'project_id': data['_id'], 'es_sitio_referencia': False})
        if sites:
            data['its_data']['answers'] = sites
        return JSONEncoder().encode(data['its_data'])

    class Meta:
        model = Project
        fields = '__all__'
