import uuid
from django.db import models


class Kme(models.Model):
    """ Modèle pour représenter une entité KME. """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    key_size = models.IntegerField(default=256)  # Taille par défaut des clés
    stored_key_count = models.IntegerField(default=0)  # Nombre de clés stockées
    max_key_count = models.IntegerField(default=10000)  # Nombre maximum de clés
    max_key_per_request = models.IntegerField(default=1)  # Nombre max de clés par requête
    max_key_size = models.IntegerField(default=256)  # Taille maximale de clé
    min_key_size = models.IntegerField(default=128)  # Taille minimale de clé
    max_SAE_ID_count = models.IntegerField(default=0)  # Multicast max pour SAE

    def __str__(self):
        return f"KME- {self.name}: {self.id}"


class Sae(models.Model):
    """
    Modèle pour les entités SAE (Subscriber Authentication Entity).
    Chaque SAE est associée à un KME et possède un certificat d'authentification.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default='user', null=True)
    sae_certificate_serial = models.BinaryField(null=True, blank=True)  # Stockage du certificat du SAE en binaire
    kme = models.ForeignKey(Kme, on_delete=models.CASCADE, null=True, blank=True)
    master_sae = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"SAE- {self.name}: {self.id}"


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
    key_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    key_data = models.BinaryField()  # Stockage binaire de la clé
    origin_sae = models.ForeignKey('Sae', related_name='origin_keys', on_delete=models.CASCADE)
    target_sae = models.ForeignKey('Sae', related_name='target_keys', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Key {self.key_uuid}"
