from rest_framework import serializers
from api.models import Project
from api.scripts.json_encoder import JSONEncoder
from fcea_monitoreo.utils import get_collection


class ProjectSerializer(serializers.ModelSerializer):
    # reference_sites = serializers.SerializerMethodField(
    #     "get_reference_sites"
    # )

    # intereses_sites = serializers.SerializerMethodField(
    #     "get_intereses_sites"
    # )

    # def get_reference_sites(self, data):
    #     sites = get_collection(
    #         'sites', {'project': data['_id'], 'es_sitio_de_referencia': True})
    #     if not sites:
    #         return None
    #     return JSONEncoder().encode(sites)

    # def get_intereses_sites(self, data):
    #     sites = get_collection(
    #         'sites', {'project': data['_id'], 'es_sitio_de_referencia': False})
    #     if not sites:
    #         return None
    #     return JSONEncoder().encode(sites)

    class Meta:
        model = Project
        fields = '__all__'
