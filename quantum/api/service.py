import base64
import uuid
import requests

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from .models import KeyMaterial, Key, KMEConnection, KME, SAE
from .encryptor import encrypt_key_aes, hash_key


def store_generated_keys(keys, aes_key, origin_sae, target_saes):
    """
    Stores the generated keys after encryption in the database via KeyMaterial.
    """

    stored_keys = []
    with transaction.atomic():  # Ensure transactional integrity.
        for key in keys:
            key_str = ''.join(map(str, key))
            encrypted_data = encrypt_key_aes(key_str, aes_key)
            aes_key_encoded = base64.b64encode(aes_key).decode('utf-8')

            key_id = uuid.uuid4()
            key_material = KeyMaterial.objects.create(
                key_id=key_id,
                encrypted_key=encrypted_data['ciphertext'],
                aes_key=aes_key_encoded,
                iv=encrypted_data['iv']
            )
            key_material.consult_by.set(target_saes)
            key_material.save()

            key_instance = Key.objects.create(
                key_id=key_id,
                key_data=base64.b64decode(encrypted_data['ciphertext']),  # Unencrypted version, if needed.
                origin_sae=origin_sae,
                size=len(key)  # Size in bits
            )
            key_instance.target_saes.set(target_saes)
            key_instance.save()

            # Adding key information to the list of stored keys for the response.
            stored_keys.append({
                "key_ID": str(key_id),
                "encrypted_key": encrypted_data['ciphertext']
            })
    return stored_keys


def create_kme_connection(source_kme, target_kme, connection_certificate):
    """
    Creates or updates the connection between two KMEs.
    """
    connection, created = KMEConnection.objects.get_or_create(
        source_kme=source_kme,
        target_kme=target_kme,
        defaults={'connection_certificate': connection_certificate}
    )
    if not created:
        connection.connection_certificate = connection_certificate
        connection.save()


def create_connection_between_kmes(request):
    """
    Creates a connection between two KMEs.
    """
    source_kme_id = request.data.get('source_kme_id')
    target_kme_id = request.data.get('target_kme_id')
    certificate = request.data.get('certificate')

    # Retrieve the KMEs.
    try:
        source_kme = KME.objects.get(kme_id=source_kme_id)
        target_kme = KME.objects.get(kme_id=target_kme_id)
    except KME.DoesNotExist:
        return Response({"error": "KME not found"}, status=status.HTTP_404_NOT_FOUND)

    # Create or update the connection.
    create_kme_connection(source_kme, target_kme, certificate)

    return Response({"message": "Connection created or updated successfully."}, status=status.HTTP_200_OK)


def update_kme_key_count(kme, new_keys_count):
    """
    Updates the number of stored keys in a KME after key generation or exchange.
    """
    kme.stored_key_count += new_keys_count
    if kme.stored_key_count > kme.max_key_count:
        raise ValueError("The maximum key storage capacity of the KME has been reached.")
    kme.save()


def get_additional_slave(request, add_slave_id):
    add_slave_sae_ids = request.data.get(add_slave_id, [])

    # If add_slave_sae_ids is a string, convert it to a list.
    if isinstance(add_slave_sae_ids, str):
        add_slave_sae_ids = [add_slave_sae_ids]

    if not add_slave_sae_ids:
        return []
    # Retrieve the SAE instances corresponding to the provided IDs.
    slave_saes = SAE.objects.filter(sae_id__in=add_slave_sae_ids)

    # Check if any SAEs were not found.
    if not slave_saes.exists():
        return Response({"error": "One or more slave SAE IDs not found"}, status=status.HTTP_404_NOT_FOUND)
    return slave_saes


def get_kme_certificate(kme):
    """
    Function to retrieve the certificate of a KME from its model.

    """
    if not kme.certificate:
        raise ValueError(f"Le KME {kme.name} has no certificate.")
    return kme.certificate


def validate_certificate(cert1, cert2):
    """
    Validate that two certificates are compatible/equal.

    """
    # A simple example of direct comparison of certificates.
    return cert1 == cert2


def validate_certificates(kme_master, kme_slave):
    """
    Validate the certificates between the master KME and the slave KME.

    """
    try:
        cert_master = get_kme_certificate(kme_master)
        cert_slave = get_kme_certificate(kme_slave)

        # Call a function that validates the certificates against each other.
        return validate_certificate(cert_master, cert_slave)
    except ValueError as e:
        # Error handling if one of the KMEs does not have a certificate.
        return False


def send_keys_to_kme2(kme_slave, sae_slave, stored_keys, aes_key):

    data = {
        "sae_slave_id": str(sae_slave.sae_id),
        "keys": stored_keys,
        "aes_key": base64.b64encode(aes_key).decode('utf-8')
    }
    response = requests.post(f"{kme_slave.hostname}/api/v1/keys/enc_keys/", json=data)
    return response



