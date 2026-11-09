from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP

def generate_key_pair():
    """
    Generate an RSA public and private key pair for a doctor.
    """

    key = RSA.generate(2048)

    private_key = key.export_key()
    public_key = key.publickey().export_key()

    return private_key, public_key

def encrypt_private_key(private_key, password):
    """
    Encrypt a doctor's private key using their password.
    """

    salt = get_random_bytes(16)

    encryption_key = PBKDF2(
        password.encode("utf-8"),
        salt,
        dkLen=32,
        count=600000,
        hmac_hash_module=SHA256
    )

    nonce = get_random_bytes(16)

    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=nonce)

    ciphertext, tag = cipher.encrypt_and_digest(private_key)

    return {
        "salt": salt,
        "nonce": nonce,
        "ciphertext": ciphertext,
        "tag": tag
    }

def decrypt_private_key(encrypted_data, password):
    """
    Decrypt a doctor's private key using their password.
    """

    encryption_key = PBKDF2(
        password.encode("utf-8"),
        encrypted_data["salt"],
        dkLen=32,
        count=600000,
        hmac_hash_module=SHA256
    )

    cipher = AES.new(
        encryption_key,
        AES.MODE_GCM,
        nonce=encrypted_data["nonce"]
    )

    private_key = cipher.decrypt_and_verify(
        encrypted_data["ciphertext"],
        encrypted_data["tag"]
    )

    return RSA.import_key(private_key)

def wrap_record_key(record_key, doctor_public_key):
    """
    Encrypt a record's AES key using the doctor's RSA public key.
    """

    public_key = RSA.import_key(doctor_public_key)

    cipher = PKCS1_OAEP.new(
        public_key,
        hashAlgo=SHA256
    )

    return cipher.encrypt(record_key)

def unwrap_record_key(wrapped_key, doctor_private_key):
    if isinstance(doctor_private_key, RSA.RsaKey):
        private_key = doctor_private_key
    else:
        private_key = RSA.import_key(doctor_private_key)

    cipher = PKCS1_OAEP.new(private_key, hashAlgo=SHA256)
    return cipher.decrypt(wrapped_key)