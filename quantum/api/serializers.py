from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import KME, SAE, Key


class UserSerializer(serializers.ModelSerializer):
    """
        Serializer for SAE Authentication
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class SAESerializer(serializers.ModelSerializer):
    """
    Serializer for the SAE entity.
    """

    class Meta:
        model = SAE
        fields = ['sae_id', 'name', 'is_master', 'sae_certificate_serial']


class KMESerializer(serializers.ModelSerializer):
    """
    Serializer for the KME entity with the included SAEs.
    """
    saes = SAESerializer(many=True, read_only=True)  # Include the associated SAEs in the response.

    class Meta:
        model = KME
        fields = ['kme_id', 'name', 'hostname', 'stored_key_count', 'max_key_count',
                  'max_key_per_request', 'max_key_size', 'min_key_size', 'key_size', 'max_SAE_ID_count', 'saes']


class KeySerializer(serializers.ModelSerializer):
    """
    Serializer for the Key entity.
    """
    origin_sae = SAESerializer(read_only=True)  # Include the details of the master SAE.
    target_saes = SAESerializer(many=True, read_only=True)  # Include the details of the slave SAEs.

    class Meta:
        model = Key
        fields = ['key_id', 'key_data', 'size', 'origin_sae', 'target_saes', 'created_at']


class StatusSerializer(serializers.Serializer):
    """
    Custom serializer for the GET /status endpoint.
    """
    source_KME_ID = serializers.CharField()
    target_KME_ID = serializers.CharField()
    master_SAE_ID = serializers.CharField()
    slave_SAE_ID = serializers.CharField()
    key_size = serializers.IntegerField()
    stored_key_count = serializers.IntegerField()
    max_key_count = serializers.IntegerField()
    max_key_per_request = serializers.IntegerField()
    max_key_size = serializers.IntegerField()
    min_key_size = serializers.IntegerField()
    max_SAE_ID_count = serializers.IntegerField()
