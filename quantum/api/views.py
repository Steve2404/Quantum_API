import os
import uuid
from django.core.files.base import ContentFile


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Sae, UninitKey, Key
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

