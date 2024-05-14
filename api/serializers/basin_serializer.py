from rest_framework import serializers
from api.models import Basin


class BasinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basin
        fields = '__all__'
