from Crypto.Random import get_random_bytes
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import SAE, KME, update_sae_communication, KeyMaterial
from .serializers import StatusSerializer
from .bb84 import generate_bb84_keys
from .service import store_generated_keys, update_kme_key_count, create_kme_connection, get_additional_slave


class KMEViewSet(viewsets.ViewSet):
    """
    ViewSet pour gérer les requêtes liées au KME.
    """

    @action(detail=True, methods=['get'], url_path='status')
    def get_status(self, request, pk=None):
        """
        Endpoint pour récupérer le statut des clés pour un SAE esclave.
        https://{KME_hostname}/api/v1/keys/{slave_SAE_ID}/status
        """
        # Récupérer le SAE esclave via son ID (pk)
        try:
            slave_sae = SAE.objects.get(sae_id=pk)
        except SAE.DoesNotExist:
            return Response({"error": "SAE not found"}, status=404)

        # Récupérer le KME associé au SAE esclave
        source_kme = slave_sae.kme

        # Vérifier avec quel SAE maître l'esclave communique
        master_sae = slave_sae.communicates_with

        if not master_sae:
            return Response({"error": "No master SAE found for this KME"}, status=404)

        # Récupérer le KME du SAE maître
        target_kme = master_sae.kme

        # Créer le dictionnaire de réponse conformément à la spécification ETSI
        status_data = {
            "source_KME_ID": source_kme.kme_id,  # Le KME du SAE esclave
            "target_KME_ID": target_kme.kme_id,  # Le KME du SAE maître
            "master_SAE_ID": master_sae.sae_id,
            "slave_SAE_ID": slave_sae.sae_id,
            "key_size": target_kme.key_size,
            "stored_key_count": target_kme.stored_key_count,
            "max_key_count": target_kme.max_key_count,
            "max_key_per_request": target_kme.max_key_per_request,
            "max_key_size": target_kme.max_key_size,
            "min_key_size": target_kme.min_key_size,
            "max_SAE_ID_count": target_kme.max_SAE_ID_count
        }

        # Retourner les données JSON directement
        serializer = StatusSerializer(status_data)
        return Response(serializer.data, status=200)

    @action(detail=True, methods=['post', 'get'], url_path='enc_keys')
    def get_key(self, request, pk=None):
        """
        Endpoint pour générer ou récupérer les clés (enc_keys).
        POST : Générer des clés (utilisé par le SAE maître).
        GET : Récupérer les clés générées (utilisé par le SAE esclave).
        https://{KME_hostname}/api/v1/keys/{slave_SAE_ID}/enc_keys
        """

        # Récupérer le SAE esclave
        try:
            slave_sae = SAE.objects.get(sae_id=pk)
            kme_slave = KME.objects.get(kme_id=slave_sae.kme_id)
        except (SAE.DoesNotExist, KME.DoesNotExist):
            return Response({"error": "Slave SAE or KME not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            # --- POST: Le SAE maître génère les clés ---

            # Ici, on suppose que le SAE maître est l'utilisateur qui effectue la requête
            # master_sae = request.user
            # print(f"nom user: {master_sae}")
            # if not master_sae.is_master:
            #     return Response({"error": "Only master SAE can generate keys"},
            #     status=status.HTTP_403_FORBIDDEN)

            # Récupérer l'ID du SAE maître à partir de la requête
            master_sae_id = request.data.get('master_sae_id', None)
            if not master_sae_id:
                return Response({"error": "Master SAE ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Récupérer le SAE maître
            try:
                master_sae = SAE.objects.get(sae_id=master_sae_id, is_master=True)
            except SAE.DoesNotExist:
                return Response({"error": "Master SAE not found"}, status=status.HTTP_404_NOT_FOUND)

            # Récupérer le KME connecté au SAE maître
            try:
                kme_master = KME.objects.get(kme_id=master_sae.kme_id)
            except KME.DoesNotExist:
                return Response({"error": "KME not found for the Master SAE"}, status=status.HTTP_404_NOT_FOUND)

            # connection sur le meme KME
            if kme_slave.kme_id == kme_master.kme_id:
                kme = kme_master
                # Mettre à jour les relations de communication entre le maître et l'esclave
                update_sae_communication(master_sae, slave_sae)

                # Gérer les paramètres de génération de clé (taille et nombre de clés)
                number_of_keys = request.data.get('number', 1)
                num_bits_per_key = request.data.get('size', 16)

                kme.key_size = num_bits_per_key
                kme.save(update_fields=['key_size'])

                # Générer les clés BB84
                bb84_keys = generate_bb84_keys(num_keys=number_of_keys, num_bits_per_key=num_bits_per_key)

                # Générer une clé AES pour le chiffrement
                aes_key = get_random_bytes(16)

                # Ajouter d'autres SAEs esclaves si nécessaire
                add_slave_saes = get_additional_slave(request, add_slave_id='add_slave_id')
                all_sae = [slave_sae] + add_slave_saes

                # Chiffrer et stocker chaque clé dans la base de données
                stored_keys = store_generated_keys(bb84_keys, aes_key, master_sae, all_sae)

                # Mettre à jour le nombre de clés stockées dans le KME
                try:
                    update_kme_key_count(kme, number_of_keys)
                except ValueError as value:
                    return Response({"error": str(value)}, status=status.HTTP_400_BAD_REQUEST)

                # Retourner la réponse avec les clés générées
                return Response({"keys": stored_keys}, status=status.HTTP_200_OK)
            else:
                # connection sur des KME different
                create_kme_connection(kme_master, kme_slave, connection_certificate="123")

        elif request.method == 'GET':
            # --- GET: Le SAE esclave récupère les clés générées ---

            # Récupérer les clés chiffrées associées à cet SAE esclave
            keys = KeyMaterial.objects.filter(consult_by=slave_sae)

            if not keys.exists():
                return Response({"error": "No keys found for this Slave SAE"}, status=status.HTTP_404_NOT_FOUND)

            # Préparer la réponse avec les clés chiffrées
            key_data = [{"key_ID": str(key.key_id), "key": key.encrypted_key} for key in keys]

            return Response({"keys": key_data}, status=status.HTTP_200_OK)
