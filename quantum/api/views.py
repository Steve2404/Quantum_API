import base64

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, TokenObtainPairSerializer

from Crypto.Random import get_random_bytes
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import SAE, KME, update_sae_communication, KeyMaterial
from .serializers import StatusSerializer
from .bb84 import generate_bb84_keys
from .encryptor import decrypt_key_aes
from .service import store_generated_keys, update_kme_key_count, get_additional_slave


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class KMEViewSet(viewsets.ViewSet):
    """
   ViewSet to handle requests related to KME.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='status')
    def get_status(self, request, pk=None):

        """
        Endpoint to retrieve the key status for a slave SAE.
        https://{KME_hostname}/api/v1/keys/{
        slave_SAE_ID}/status
            
        """

        # Retrieve the slave SAE via its ID (pk).
        try:
            slave_sae = SAE.objects.get(sae_id=pk)
        except SAE.DoesNotExist:
            return Response({"error": "SAE not found"}, status=404)

        # Retrieve the KME associated with the slave SAE.
        source_kme = slave_sae.kme

        # Check with which master SAE the slave is communicating.
        master_sae = slave_sae.communicates_with

        if not master_sae:
            return Response({"error": "No master SAE found for this KME"}, status=404)

        # Retrieve the KME of the master SAE.
        target_kme = master_sae.kme

        # Create the response dictionary according to the ETSI specification.
        status_data = {
            "source_KME_ID": source_kme.kme_id,  # Le KME du SAE esclave
            "target_KME_ID": target_kme.kme_id,  # KME of the slave SAE
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

        # Return the JSON data directly.
        serializer = StatusSerializer(status_data)
        return Response(serializer.data, status=200)

    @action(detail=True, methods=['post', 'get'], url_path='enc_keys')
    def get_key(self, request, pk=None):
        """
        Endpoint to generate or retrieve keys (enc_keys).
        POST : Generate keys (used by the master SAE).
        GET : Retrieve the generated keys (used by the slave SAE).
        https://{KME_hostname}/api/v1/keys/{slave_SAE_ID}/enc_keys
        """

        # Retrieve the slave SAE.
        try:
            slave_sae = SAE.objects.get(sae_id=pk)
            kme_slave = KME.objects.get(kme_id=slave_sae.kme_id)
        except (SAE.DoesNotExist, KME.DoesNotExist):
            return Response({"error": "Slave SAE or KME not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            # POST: The master SAE generates the keys.

            # Retrieve the master SAE ID from the request.
            master_sae_id = request.data.get('master_sae_id', None)
            if not master_sae_id:
                return Response({"error": "Master SAE ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the master SAE.
            try:
                master_sae = SAE.objects.get(sae_id=master_sae_id, is_master=True)
            except SAE.DoesNotExist:
                return Response({"error": "Master SAE not found"}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve the KME connected to the master SAE.
            try:
                kme_master = KME.objects.get(kme_id=master_sae.kme_id)
            except KME.DoesNotExist:
                return Response({"error": "KME not found for the Master SAE"}, status=status.HTTP_404_NOT_FOUND)

            # Connection on the same KME
            if kme_slave.kme_id == kme_master.kme_id:
                kme = kme_master
                # Update the communication relationships between the master and the slave.
                update_sae_communication(master_sae, slave_sae)

                # Manage key generation parameters (size and number of keys).
                number_of_keys = request.data.get('number', 1)
                num_bits_per_key = request.data.get('size', 16)

                kme.key_size = num_bits_per_key
                kme.save(update_fields=['key_size'])

                # Generate the BB84 keys.
                bb84_keys = generate_bb84_keys(num_keys=number_of_keys, num_bits_per_key=num_bits_per_key)

                # Hash the AES key for encryption.
                aes_key = get_random_bytes(16)

                # Add other slave SAEs if necessary.
                add_slave_saes = get_additional_slave(request, add_slave_id='add_slave_id')
                all_sae = [slave_sae] + add_slave_saes

                # Encrypt and store each key in the database.
                stored_keys = store_generated_keys(bb84_keys, aes_key, master_sae, all_sae)

                # Update the number of stored keys in the KME.
                try:
                    update_kme_key_count(kme, number_of_keys)
                except ValueError as value:
                    return Response({"error": str(value)}, status=status.HTTP_400_BAD_REQUEST)

                # Return the response with the generated keys.
                return Response({"keys": stored_keys}, status=status.HTTP_200_OK)

        elif request.method == 'GET':
            # GET: slave SAE retrieves the generated keys

            # Retrieve the encrypted keys associated with this slave SAE.
            keys = KeyMaterial.objects.filter(consult_by=slave_sae)

            if not keys.exists():
                return Response({"error": "No keys found for this Slave SAE"}, status=status.HTTP_404_NOT_FOUND)

            # Prepare the response with the encrypted keys.
            key_data = [{"key_ID": str(key.key_id), "key": key.encrypted_key} for key in keys]

            return Response({"keys": key_data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'], url_path='dec_keys')
    def get_keys_by_ids(self, request, pk=None):
        """
        Endpoint to retrieve specific keys with their key_IDs for a slave SAE.
        https://{KME_hostname}/api/v1/keys/{master_SAE_ID}/dec_keys?key_ID=bc490419-7d60-487f-adc1-4ddcc177c139
        """
        # Retrieve the master SAE via the ID passed in the URL.
        try:
            master_sae = SAE.objects.get(sae_id=pk, is_master=True)
            print(f"master id: {master_sae}")
        except SAE.DoesNotExist:
            return Response({"error": "Master SAE not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the key_IDs from the GET request parameters.
        key_ids = request.query_params.get('key_ID')

        if not key_ids:
            return Response({"error": "No key IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the keys associated with the provided key_IDs.
        keys = KeyMaterial.objects.filter(key_id=key_ids)

        if not keys.exists():
            return Response({"error": "No keys found for the provided key IDs"}, status=status.HTTP_404_NOT_FOUND)

        # Prepare the response with the decrypted keys.
        keys_data = []
        for key_material in keys:
            aes_key = base64.b64decode(key_material.aes_key)
            decrypted_key = decrypt_key_aes(key_material.encrypted_key, aes_key)
            keys_data.append({
                "key_ID": str(key_material.key_id),
                "decrpyted_key": decrypted_key,
            })

        return Response({"keys": keys_data}, status=status.HTTP_200_OK)
