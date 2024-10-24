import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad


def hash_key(bits):
    """Convert a list of bits into a key usable for AES encryption."""
    bit_str = ''.join(str(bit) for bit in bits)
    key_raw = int(bit_str, 2).to_bytes((len(bit_str) + 7) // 8, 'big')
    hash_code = SHA256.new(key_raw)
    hash_code.update(key_raw)
    return hash_code.digest()[:16]


def encrypt_key_aes(key, aes_key):
    """
    Chiffrer la clé binaire BB84 avec AES.
    :param key: La clé à chiffrer (générée par BB84).
    :param aes_key: La clé symétrique AES utilisée pour le chiffrement.
    :return: La clé chiffrée en base64.
    """

    cipher = AES.new(aes_key, AES.MODE_CBC)  # Utilisation d'AES en mode CBC
    iv = cipher.iv
    ct_bytes = cipher.encrypt(pad(key.encode(), AES.block_size))  # Chiffrement de la clé
    # iv = base64.b64encode(cipher.iv).decode('utf-8')  # Initialisation vector (IV)
    ciphertext = base64.b64encode(iv + ct_bytes).decode('utf-8')  # Clé chiffrée
    return {"iv": iv, "ciphertext": ciphertext}


def decrypt_key_aes(encrypted_key, aes_key):
    """
    Déchiffre une clé AES en mode CBC.
    :param encrypted_key: La clé chiffrée en base64.
    :param aes_key: La clé AES symétrique utilisée pour le déchiffrement.
    :return: La clé déchiffrée sous forme de texte.
    """

    # Décoder l'IV et le texte chiffré du format base64
    encrypted_key_decode = base64.b64decode(encrypted_key)
    iv = encrypted_key_decode[:AES.block_size]

    # Créer le cipher AES en mode CBC
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)

    # Déchiffrer et dépadder les données
    decrypted_key_block = cipher.decrypt(encrypted_key_decode[AES.block_size:])
    decrypted_key = unpad(decrypted_key_block, AES.block_size)
    decrypted_key_list = [int(char) for char in decrypted_key.decode()]

    return decrypted_key_list
