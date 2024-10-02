import base64

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad


def key_reformat(bits):
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
    ct_bytes = cipher.encrypt(pad(bytes(key), AES.block_size))  # Chiffrement de la clé
    iv = base64.b64encode(cipher.iv).decode('utf-8')  # Initialisation vector (IV)
    ct = base64.b64encode(ct_bytes).decode('utf-8')  # Clé chiffrée
    return {"iv": iv, "ciphertext": ct}


def decrypt_key_aes(encrypted_key, aes_key, iv):
    """
    Déchiffre une clé AES en mode CBC.
    :param encrypted_key: La clé chiffrée en base64.
    :param aes_key: La clé AES symétrique utilisée pour le déchiffrement.
    :param iv: Le vecteur d'initialisation (IV) utilisé pour le chiffrement, encodé en base64.
    :return: La clé déchiffrée sous forme de texte.
    """
    # Décoder l'IV et le texte chiffré du format base64
    iv = base64.b64decode(iv)
    encrypted_key = base64.b64decode(encrypted_key)

    # Créer le cipher AES en mode CBC
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)

    # Déchiffrer et dépadder les données
    decrypted_key = unpad(cipher.decrypt(encrypted_key), AES.block_size)

    return decrypted_key
