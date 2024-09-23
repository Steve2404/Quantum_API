from rest_framework import viewsets
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
    """
    ViewSet pour gérer les clés attribuées.
    Permet d'effectuer des opérations CRUD sur les clés déjà assignées.
    """
    queryset = Key.objects.all()
    serializer_class = KeySerializer


