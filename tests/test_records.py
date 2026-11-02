# test_records.py
# Unit tests for Feature 2 (encrypted records).

import unittest
from Crypto.Random import get_random_bytes
from records.record_crypto import derive_key, encrypt, decrypt


class TestRecordCrypto(unittest.TestCase):

    # Runs before every test: makes a fresh salt and key to test with
    def setUp(self):
        self.salt = get_random_bytes(16)
        self.key = derive_key("MyPass123!", self.salt)
        self.record = b"Blood test: normal"

    # Test 1: encrypting then decrypting gives back the original record
    def test_round_trip(self):
        nonce, ct, tag = encrypt(self.key, self.record)
        self.assertEqual(decrypt(self.key, nonce, ct, tag), self.record)

    # Test 2: encrypting the same record twice gives different ciphertext
    def test_same_record_different_ciphertext(self):
        nonce1, ct1, tag1 = encrypt(self.key, self.record)
        nonce2, ct2, tag2 = encrypt(self.key, self.record)
        self.assertNotEqual(ct1, ct2)
    # Test 3: changing one byte of the ciphertext is detected and rejected
    def test_tampered_ciphertext_rejected(self):
        nonce, ct, tag = encrypt(self.key, self.record)
        tampered = bytearray(ct)
        tampered[0] ^= 1
        with self.assertRaises(ValueError):
            decrypt(self.key, nonce, bytes(tampered), tag)

        # Test 4: decrypting with a key from the wrong password is rejected
    def test_wrong_key_rejected(self):
        nonce, ct, tag = encrypt(self.key, self.record)
        wrong_key = derive_key("____", self.salt)
        with self.assertRaises(ValueError):
            decrypt(wrong_key, nonce, ct, tag)

if __name__ == "__main__":
    unittest.main()

   