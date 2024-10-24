import base64
import uuid

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

from .models import KeyMaterial, Key, KMEConnection, KME, SAE
from .encryptor import encrypt_key_aes, hash_key


def store_generated_keys(keys, aes_key, origin_sae, target_saes):
    """
    Stocke les clés générées après leur chiffrement dans la base de données via KeyMaterial.
    """

    stored_keys = []
    with transaction.atomic():  # Assurer l'intégrité transactionnelle
        for key in keys:
            # print(key)
            key_str = ''.join(map(str, key))
            # key = normalize_key(key)
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
                key_data=base64.b64decode(encrypted_data['ciphertext']),  # Version non chiffrée, si nécessaire
                origin_sae=origin_sae,
                size=len(key)  # Taille en bits
            )
            key_instance.target_saes.set(target_saes)
            key_instance.save()

            # Ajout des informations sur la clé à la liste des clés stockées pour la réponse
            stored_keys.append({
                "key_ID": str(key_id),
                "encrypted_key": encrypted_data['ciphertext']
            })
    return stored_keys


def create_kme_connection(source_kme, target_kme, connection_certificate):
    """
    Crée ou met à jour la connexion entre deux KMEs.
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
    Crée une connexion entre deux KMEs.
    """
    source_kme_id = request.data.get('source_kme_id')
    target_kme_id = request.data.get('target_kme_id')
    certificate = request.data.get('certificate')

    # Récupérer les KMEs
    try:
        source_kme = KME.objects.get(kme_id=source_kme_id)
        target_kme = KME.objects.get(kme_id=target_kme_id)
    except KME.DoesNotExist:
        return Response({"error": "KME not found"}, status=status.HTTP_404_NOT_FOUND)

    # Créer ou mettre à jour la connexion
    create_kme_connection(source_kme, target_kme, certificate)

    return Response({"message": "Connection created or updated successfully."}, status=status.HTTP_200_OK)


def update_kme_key_count(kme, new_keys_count):
    """
    Met à jour le nombre de clés stockées dans un KME après génération ou échange de clés.
    """
    kme.stored_key_count += new_keys_count
    if kme.stored_key_count > kme.max_key_count:
        raise ValueError("La capacité maximale de stockage de clés du KME a été atteinte.")
    kme.save()


def get_additional_slave(request, add_slave_id):
    add_slave_sae_ids = request.data.get(add_slave_id, [])

    # Si add_slave_sae_ids est une chaîne, convertis-le en liste
    if isinstance(add_slave_sae_ids, str):
        add_slave_sae_ids = [add_slave_sae_ids]

    if not add_slave_sae_ids:
        return []
    # Récupérer les instances SAE correspondantes aux IDs fournis
    slave_saes = SAE.objects.filter(sae_id__in=add_slave_sae_ids)

    # Vérifier si des SAE n'ont pas été trouvés
    if not slave_saes.exists():
        return Response({"error": "One or more slave SAE IDs not found"}, status=status.HTTP_404_NOT_FOUND)
    return slave_saes

