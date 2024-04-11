from rest_framework import serializers
from api.models import User


class UserSerializer(serializers.ModelSerializer):
    short_name = serializers.SerializerMethodField(
        "get_short_name"
    )
    full_name = serializers.SerializerMethodField(
        "get_full_name"
    )

    def get_short_name(self, data):
        if 'name' not in data:
            return f"{data['email'][0]} {data['email'][1]}"

        if 'last_name' in data and data['last_name'] != '':
            last_name = data['last_name'].split()
            return f"{data['name']} {last_name[0]}"
        return None

    def get_full_name(self, data):
        if 'name' not in data:
            return f"{data['email'][0]} {data['email'][1]}"

        if 'last_name' in data and data['last_name'] != '':
            return f"{data['name']} {data['last_name']}"
        return None

    class Meta:
        model = User
        fields = '__all__'
