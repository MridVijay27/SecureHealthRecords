import unittest

from sharing.key_manager import (
    generate_key_pair,
    encrypt_private_key,
    decrypt_private_key
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


if __name__ == "__main__":
    unittest.main()