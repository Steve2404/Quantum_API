import uuid
from django.db import models
from django.utils.translation import gettext as _


class KME(models.Model):
    _(""" Modèle pour représenter une entité KME. """)
    kme_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)  # Nom d'hôte ou adresse IP
    certificate = models.BinaryField(null=True, blank=True)
    stored_key_count = models.IntegerField(default=0)  # Nombre de clés stockées
    max_key_count = models.IntegerField(default=100000)
    max_key_per_request = models.IntegerField(default=128)
    max_key_size = models.IntegerField(default=1024)
    min_key_size = models.IntegerField(default=64)
    key_size = models.IntegerField(default=352)
    max_SAE_ID_count = models.IntegerField(default=0)  # Maximum de SAEs supplémentaires dans une requête multicast

    def __str__(self):
        return f"KME- {self.name}: {self.kme_id}"


class SAE(models.Model):
    """
    Modèle pour les entités SAE (Subscriber Authentication Entity).
    Chaque SAE est associée à un KME et possède un certificat d'authentification.
    """
    sae_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    kme = models.ForeignKey(KME, related_name='saes', on_delete=models.CASCADE)  # Kme connecté à plusieurs SAE
    is_master = models.BooleanField(default=False)  # Indique si le SAE est maître
    sae_certificate_serial = models.BinaryField(null=True, blank=True)
    # Relation avec le SAE avec qui il communique
    communicates_with = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"SAE- {self.name}: {self.sae_id}"


class Key(models.Model):
    """
    Modèle pour les clés assignées entre SAE d'origine et SAE cible.
    """
    key_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    key_data = models.BinaryField()
    origin_sae = models.ForeignKey(SAE, related_name='origin_keys', on_delete=models.CASCADE)  # SAE maître
    target_saes = models.ManyToManyField(SAE, related_name='target_keys')  # SAEs esclaves
    created_at = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField(default=352)

    def __str__(self):
        return f"Key {self.key_id} (size: {self.size} bits)"


class KMEConnection(models.Model):
    source_kme = models.ForeignKey(KME, related_name='outgoing_connections', on_delete=models.CASCADE)
    target_kme = models.ForeignKey(KME, related_name='incoming_connections', on_delete=models.CASCADE)
    connection_certificate = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return f"Connection from {self.source_kme} to {self.target_kme}"


class KeyMaterial(models.Model):
    key_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    encrypted_key = models.TextField()  # La clé chiffrée (en base64)
    iv = models.TextField()  # Le vecteur d'initialisation AES
    consult_by = models.ManyToManyField(SAE, related_name='consulted_keys')
    created_at = models.DateTimeField(auto_now_add=True)


def update_sae_communication(master_sae, slave_sae):
    """
    Met à jour les relations de communication entre SAE maître et SAE esclave.
    """
    master_sae.communicates_with = slave_sae
    slave_sae.communicates_with = master_sae
    master_sae.save()
    slave_sae.save()




