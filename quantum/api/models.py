import uuid

from Crypto.Random import get_random_bytes
from django.db import models
from django.contrib.auth.models import User


class KME(models.Model):
    """ Model to represent a KME entity """
    kme_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    hostname = models.CharField(max_length=255)  # Hostname or IP address.
    certificate = models.BinaryField(null=True, blank=True)
    stored_key_count = models.IntegerField(default=0)  # Number of stored keys.
    max_key_count = models.IntegerField(default=100000)
    max_key_per_request = models.IntegerField(default=128)
    max_key_size = models.IntegerField(default=1024)
    min_key_size = models.IntegerField(default=64)
    key_size = models.IntegerField(default=352)
    max_SAE_ID_count = models.IntegerField(default=0)  # Maximum additional SAEs in a multicast request.

    def __str__(self):
        return f"KME- {self.name}: {self.kme_id}"


class SAE(models.Model):
    """
    Model for Subscriber Authentication Entities (SAE). Each SAE is associated with a KME and has an authentication certificate.
    """
    sae_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    kme = models.ForeignKey(KME, related_name='saes', on_delete=models.CASCADE)  # KME connected to multiple SAEs.
    is_master = models.BooleanField(default=False)  # Indicates if the SAE is master
    sae_certificate_serial = models.BinaryField(null=True, blank=True)
    # Relationship with the SAE it communicates with.
    communicates_with = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"SAE- {self.name}: {self.sae_id}"


class Key(models.Model):
    """
    Model for keys assigned between source SAE and target SAE.
    """
    key_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    key_data = models.BinaryField()
    origin_sae = models.ForeignKey(SAE, related_name='origin_keys', on_delete=models.CASCADE)  # Master SAE.
    target_saes = models.ManyToManyField(SAE, related_name='target_keys')  # Slave SAEs.
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
    encrypted_key = models.TextField()  # The encrypted key (in base64)
    aes_key = models.TextField(default=get_random_bytes(16))
    iv = models.TextField()  # The AES initialization vector.
    consult_by = models.ManyToManyField(SAE, related_name='consulted_keys')
    created_at = models.DateTimeField(auto_now_add=True)


def update_sae_communication(master_sae, slave_sae):
    """
    Updates the communication relationships between master SAE and slave SAE.
    """
    master_sae.communicates_with = slave_sae
    slave_sae.communicates_with = master_sae
    master_sae.save()
    slave_sae.save()




