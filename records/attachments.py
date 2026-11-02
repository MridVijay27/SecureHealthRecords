# attachments.py
# Feature 2: encrypts and decrypts file attachments (e.g. a scan or PDF) with AES-256-GCM.
# Reuses encrypt() and decrypt() from record_crypto, so files get the same protection as text records.

import os
from records.record_crypto import encrypt, decrypt

# Limit attachment size so a very large file cannot fill up the database (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Reads a file from disk and encrypts its contents with AES-256-GCM.
# Returns the original file name plus the nonce, ciphertext and tag to store in the database.
def encrypt_file(key, file_path):
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        raise ValueError("File is too large (maximum 10 MB)")
    with open(file_path, "rb") as f:
        data = f.read()
    nonce, ciphertext, tag = encrypt(key, data)
    return os.path.basename(file_path), nonce, ciphertext, tag

# Decrypts an attachment and writes the original file to output_path.
# Raises ValueError if the attachment was tampered with or the key is wrong,
# so a changed file is never written to disk.
def decrypt_file(key, nonce, ciphertext, tag, output_path):
    data = decrypt(key, nonce, ciphertext, tag)
    with open(output_path, "wb") as f:
        f.write(data)