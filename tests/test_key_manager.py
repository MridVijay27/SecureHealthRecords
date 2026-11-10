import unittest
from Crypto.Random import get_random_bytes

from sharing.key_manager import (
    generate_key_pair,
    encrypt_private_key,
    decrypt_private_key,
    wrap_record_key,
    unwrap_record_key
)


class TestKeyManager(unittest.TestCase):

    def test_key_generation(self):
        private_key, public_key = generate_key_pair()

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)

    def test_encrypt_and_decrypt_private_key(self):
        private_key, public_key = generate_key_pair()

        encrypted = encrypt_private_key(
            private_key,
            "DoctorPassword123"
        )

        decrypted = decrypt_private_key(
            encrypted,
            "DoctorPassword123"
        )

        self.assertEqual(
            decrypted.export_key(),
            private_key
        )

    def test_wrong_password_is_rejected(self):
        private_key, public_key = generate_key_pair()

        encrypted = encrypt_private_key(
            private_key,
            "DoctorPassword123"
        )

        with self.assertRaises(ValueError):
            decrypt_private_key(
                encrypted,
                "WrongPassword123"
            )   
             
    def test_wrap_and_unwrap_record_key(self):
        private_key, public_key = generate_key_pair()

        record_key = get_random_bytes(32)

        wrapped_key = wrap_record_key(record_key, public_key)

        unwrapped_key = unwrap_record_key(
            wrapped_key,
            private_key
        )

        self.assertEqual(record_key, unwrapped_key)

    def test_wrong_doctor_cannot_unwrap_record_key(self):
        doctor1_private, doctor1_public = generate_key_pair()
        doctor2_private, doctor2_public = generate_key_pair()

        record_key = get_random_bytes(32)

        wrapped_key = wrap_record_key(record_key, doctor1_public)

        with self.assertRaises(ValueError):
            unwrap_record_key(wrapped_key, doctor2_private)

if __name__ == "__main__":
    unittest.main()