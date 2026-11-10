import unittest

from sharing.key_manager import generate_key_pair
from sharing.signatures import sign_note, verify_signature


class TestSignatures(unittest.TestCase):

    def test_valid_signature(self):
        private_key, public_key = generate_key_pair()

        note = "Patient check-up completed."

        signature = sign_note(note, private_key)

        result = verify_signature(note, signature, public_key)

        self.assertTrue(result)


    def test_edited_note_fails_verification(self):
        private_key, public_key = generate_key_pair()

        note = "Patient check-up completed."

        signature = sign_note(note, private_key)

        edited_note = "Patient check-up was cancelled."

        result = verify_signature(edited_note, signature, public_key)

        self.assertFalse(result)


    def test_wrong_doctor_key_fails_verification(self):
        doctor1_private, doctor1_public = generate_key_pair()
        doctor2_private, doctor2_public = generate_key_pair()

        note = "Patient check-up completed."

        signature = sign_note(note, doctor1_private)

        result = verify_signature(note, signature, doctor2_public)

        self.assertFalse(result)