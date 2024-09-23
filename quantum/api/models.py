import uuid
from django.db import models


class Sae(models.Model):
    """
    Modèle pour les entités SAE (Subscriber Authentication Entity).
    Chaque SAE est associée à un KME et possède un certificat d'authentification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID pour identifier chaque SAE
    sae_certificate_serial = models.BinaryField(null=True, blank=True)  # Stockage du certificat du SAE en binaire
    kme_id = models.IntegerField()  # Référence à un KME via son ID

    def __str__(self):
        return f"SAE {self.id}"


class UninitKey(models.Model):
    """
    Modèle pour les clés non initialisées.
    Elles sont stockées avant d'être assignées à des SAE.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID pour chaque clé non initialisée
    key_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Identifiant unique de la clé
    key = models.BinaryField()  # Clé elle-même, stockée sous forme binaire
    other_kme_id = models.IntegerField()  # Référence à un autre KME si la clé est partagée

    def __str__(self):
        return f"UninitKey {self.key_uuid}"


class Key(models.Model):
    """
    Modèle pour les clés assignées entre SAE d'origine et SAE cible.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    key = models.BinaryField()  # Clé attribuée
    origin_sae = models.ForeignKey(Sae, related_name='origin_keys', on_delete=models.CASCADE)  # SAE d'origine
    target_sae = models.ForeignKey(Sae, related_name='target_keys', on_delete=models.CASCADE)  # SAE cible

    def __str__(self):
        return f"Key {self.key_uuid}"
