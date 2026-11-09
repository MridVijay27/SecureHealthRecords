# record_crypto.py
# Feature 2: encrypts and decrypts patient records with AES-256-GCM.
# The key is derived from the patient's password using PBKDF2-HMAC-SHA256.

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

# High iteration count makes password guessing slow (OWASP recommends 600,000 for PBKDF2-SHA256)
PBKDF2_ITERATIONS = 600000

# 32 bytes = 256-bit key, so AES runs as AES-256
KEY_LENGTH = 32

# Turns the patient's password into a 256-bit AES key.
# The same password + same salt always gives the same key, so the salt must be stored with the record. The salt is not secret.
def derive_key(password, salt):
    return PBKDF2(password, salt, dkLen=KEY_LENGTH,
                  count=PBKDF2_ITERATIONS, hmac_hash_module=SHA256)

# Encrypts data with AES-256-GCM.
# A new random 12-byte nonce is made every time, because reusing a nonce with the same key breaks GCM's security.
# Returns the nonce, the ciphertext and the 16-byte authentication tag.
def encrypt(key, plaintext):
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return nonce, ciphertext, tag

# Decrypts data with AES-256-GCM and checks the tag.
# Raises ValueError if the data was changed or the key is wrong.
def decrypt(key, nonce, ciphertext, tag):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)