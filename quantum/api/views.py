import os
import uuid
from django.core.files.base import ContentFile


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Sae, UninitKey, Key, Kme
from .serializers import SaeSerializer, UninitKeySerializer, KeySerializer


class SaeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les entités SAE.
    Permet d'effectuer des opérations CRUD sur les SAE via l'API.
    """
    queryset = Sae.objects.all()  # Récupère tous les objets SAE
    serializer_class = SaeSerializer  # Spécifie le serializer à utiliser


class UninitKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les clés non initialisées.
    Permet d'effectuer des opérations CRUD sur les clés non initialisées.
    """
    queryset = UninitKey.objects.all()
    serializer_class = UninitKeySerializer


class KeyViewSet(viewsets.ModelViewSet):
    queryset = UninitKey.objects.all()
    serializer_class = UninitKeySerializer

    @action(detail=False, methods=['post'])
    def generate_key(self, request):
        """
        Générer une clé non initialisée et la stocker dans la base de données.
        """
        key_data = os.urandom(32)  # Générer une clé brute (256 bits)
        new_uninit_key = UninitKey(
            key_uuid=uuid.uuid4(),
            key=ContentFile(key_data),
            other_kme_id=request.data.get('other_kme_id')
        )
        new_uninit_key.save()

        serializer = self.get_serializer(new_uninit_key)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='status')
    def get_status(self, request, slave_sae_id=None):
        """
        Obtenir dynamiquement le statut des clés échangées entre le SAE maître et le SAE esclave.
        """
        try:
            # Récupérer le SAE esclave à partir de son ID
            slave_sae = Sae.objects.get(id=slave_sae_id)
        except Sae.DoesNotExist:
            return Response({"error": "SAE non trouvé"}, status=404)

        # Récupérer le KME source du SAE esclave et maitre
        source_kme = slave_sae.kme
        master_sae = slave_sae.master_sae

        # Si le SAE maître existe, récupérer le KME auquel il est connecté (target KME)
        if master_sae:
            target_kme = master_sae.kme
        else:
            return Response({"error": "SAE maître non trouvé"}, status=404)

        # Statut dynamique basé sur les KMEs et SAEs
        status_data = {
            "source_KME_ID": str(source_kme.id),
            "target_KME_ID": str(target_kme.id),
            "master_SAE_ID": str(master_sae.id),
            "slave_SAE_ID": slave_sae_id,
            "key_size": source_kme.key_size,
            "stored_key_count": source_kme.stored_key_count,
            "max_key_count": source_kme.max_key_count,
            "max_key_per_request": source_kme.max_key_per_request,
            "max_key_size": source_kme.max_key_size,
            "min_key_size": source_kme.min_key_size,
            "max_SAE_ID_count": source_kme.max_SAE_ID_count
        }
        return Response(status_data)
