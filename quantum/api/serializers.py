from rest_framework import serializers
from .models import Sae, UninitKey, Key


class SaeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sae
        fields = ['id', 'sae_certificate_serial', 'kme']


class UninitKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = UninitKey
        fields = ['id', 'key_uuid', 'key', 'other_kme_id']


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ['id', 'key_uuid', 'key', 'origin_sae', 'target_sae']
