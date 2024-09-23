from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter


from api.views import SaeViewSet, UninitKeyViewSet, KeyViewSet

# Configuration du routeur
router = DefaultRouter()
router.register(r'saes', SaeViewSet)  # Route pour les SAE
router.register(r'uninitkeys', UninitKeyViewSet)  # Route pour les clés non initialisées
router.register(r'keys', KeyViewSet)  # Route pour les clés attribuées

# Inclusion des routes dans le fichier urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),  # Insertion des routes générées par le routeur
]
