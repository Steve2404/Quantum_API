from rest_framework import serializers
from .models import KME, SAE, Key


class SAESerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'entité SAE.
    """
    class Meta:
        model = SAE
        fields = ['sae_id', 'name', 'is_master', 'sae_certificate_serial']


class KMESerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'entité KME avec les SAE inclus.
    """
    saes = SAESerializer(many=True, read_only=True)  # Inclure les SAE associés dans la réponse

    class Meta:
        model = KME
        fields = ['kme_id', 'name', 'hostname', 'stored_key_count', 'max_key_count',
                  'max_key_per_request', 'max_key_size', 'min_key_size', 'key_size', 'max_SAE_ID_count', 'saes']


class KeySerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'entité Key.
    """
    origin_sae = SAESerializer(read_only=True)  # Inclure les détails du SAE maître
    target_saes = SAESerializer(many=True, read_only=True)  # Inclure les détails des SAE esclaves

    class Meta:
        model = Key
        fields = ['key_id', 'key_data', 'size', 'origin_sae', 'target_saes', 'created_at']

class StatusSerializer(serializers.Serializer):
    """
    Sérialiseur personnalisé pour l'endpoint GET /status
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