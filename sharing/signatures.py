from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

def sign_note(note_text, doctor_private_key):
    """Create a digital signature for a doctor's note."""

    if isinstance(doctor_private_key, RSA.RsaKey):
        private_key = doctor_private_key
    else:
        private_key = RSA.import_key(doctor_private_key)

    message_hash = SHA256.new(note_text.encode("utf-8"))

    signature = pss.new(private_key).sign(message_hash)

    return signature


def verify_signature(note_text, signature, doctor_public_key):
    """Verify the digital signature of a doctor's note."""

    if isinstance(doctor_public_key, RSA.RsaKey):
        public_key = doctor_public_key
    else:
        public_key = RSA.import_key(doctor_public_key)

    message_hash = SHA256.new(note_text.encode("utf-8"))

    verifier = pss.new(public_key)

    try:
        verifier.verify(message_hash, signature)
        return True
    except (ValueError, TypeError):
        return False