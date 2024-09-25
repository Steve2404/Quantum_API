from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UninitKeyViewSet, KeyViewSet, SaeViewSet

# Créer un routeur pour enregistrer les ViewSets
router = DefaultRouter()

# Enregistrer les routes pour les ViewSets
router.register(r'uninitkeys', UninitKeyViewSet, basename='uninitkeys')  # Pour les clés non initialisées
router.register(r'Keys', KeyViewSet, basename='Keys')  # Pour les clés initialisées
router.register(r'saes', SaeViewSet, basename='saes')  # Pour les SAE

# Ajouter les routes dans les URLs principales de l'application
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/keys/', include([
        path('<str:slave_sae_id>/status/', KeyViewSet.as_view({'get': 'get_status'}), name='status')
    ]))
]