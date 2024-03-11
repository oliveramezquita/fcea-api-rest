from rest_framework import serializers


class ProjectsSerializer(serializers.Serializer):
    name = serializers.CharField()
    uid = serializers.CharField()
    last_update = serializers.DateTimeField()


class SubmissionSerializer(serializers.Serializer):
    _id = serializers.IntegerField()
    name = serializers.CharField(source='nombre_sitio')
    form_id = serializers.CharField(source='id_formulario')
    water_body = serializers.CharField(source='tipo_de_cuerpo')
