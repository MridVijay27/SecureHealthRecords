# Handles secure password hashing and verification using PBKDF2.

import hmac
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

# OWASP recommends 600,000 iterations for PBKDF2-HMAC-SHA256 to slow down password guessing.
SALT_LENGTH = 16
KEY_LENGTH = 32
ITERATIONS = 600000


def hash_password(password):
    # A random salt ensures identical passwords produce different hashes.
    salt = get_random_bytes(SALT_LENGTH)

    password_hash = PBKDF2(
        password.encode("utf-8"),
        salt,
        dkLen=KEY_LENGTH,
        count=ITERATIONS,
        hmac_hash_module=SHA256
    )

    return salt.hex(), password_hash.hex()


def verify_password(password, stored_salt, stored_hash):
    # Recreate the hash using the stored salt and compare it with the original.
    try:
        salt = bytes.fromhex(stored_salt)
        original_hash = bytes.fromhex(stored_hash)
    except (ValueError, TypeError):
        return False

    new_hash = PBKDF2(
        password.encode("utf-8"),
        salt,
        dkLen=KEY_LENGTH,
        count=ITERATIONS,
        hmac_hash_module=SHA256
    )

    # Constant-time comparison reduces timing-based information leaks.
    return hmac.compare_digest(new_hash, original_hash)
