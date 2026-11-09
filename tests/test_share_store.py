
import os
import tempfile
import unittest

import db
from sharing import share_store
from sharing.key_manager import generate_key_pair, encrypt_private_key

class TestShareStore(unittest.TestCase):

    def setUp(self):
        # Use a separate temporary database for each test.
        self.test_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DB_PATH
        db.DB_PATH = os.path.join(self.test_dir.name, "test_sharing.db")

        share_store.create_sharing_tables()

    def tearDown(self):
        # Restore the original database path.
        db.DB_PATH = self.original_db_path
        self.test_dir.cleanup()

    def test_create_sharing_tables(self):
        conn = db.get_connection()

        tables = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table'
        """).fetchall()

        conn.close()

        table_names = [table[0] for table in tables]

        self.assertIn("doctor_keys", table_names)
        self.assertIn("shares", table_names)
        self.assertIn("notes", table_names)


    def test_save_and_retrieve_doctor_keys(self):
        private_key, public_key = generate_key_pair()

        encrypted_private_key = encrypt_private_key(
            private_key, "DoctorPass123!"
        )

        share_store.save_doctor_keys(
            "doctor1", public_key, encrypted_private_key
        )

        saved_public_key = share_store.get_doctor_public_key("doctor1")
        saved_private_key = share_store.get_encrypted_private_key("doctor1")

        self.assertEqual(saved_public_key, public_key)
        self.assertEqual(saved_private_key["salt"], encrypted_private_key["salt"])
        self.assertEqual(saved_private_key["nonce"], encrypted_private_key["nonce"])
        self.assertEqual(saved_private_key["ciphertext"], encrypted_private_key["ciphertext"])
        self.assertEqual(saved_private_key["tag"], encrypted_private_key["tag"])


    def test_create_and_retrieve_share(self):
        record_id = 1
        patient = "alice"
        doctor = "doctor1"
        wrapped_key = b"test_wrapped_key"

        share_store.create_share(
            record_id, patient, doctor, wrapped_key
        )

        shares = share_store.get_doctor_shares(doctor)

        self.assertEqual(len(shares), 1)
        self.assertEqual(shares[0][0], record_id)
        self.assertEqual(shares[0][1], patient)
        self.assertEqual(shares[0][2], wrapped_key)

        active_share = share_store.get_active_share(record_id, doctor)

        self.assertEqual(active_share["patient"], patient)
        self.assertEqual(active_share["wrapped_key"], wrapped_key)


    def test_revoke_share(self):
        record_id = 1
        patient = "alice"
        doctor = "doctor1"
        wrapped_key = b"test_wrapped_key"

        share_store.create_share(
            record_id, patient, doctor, wrapped_key
        )

        revoked = share_store.revoke_share(
            record_id, patient, doctor
        )

        self.assertTrue(revoked)

        # The doctor should no longer see this share.
        shares = share_store.get_doctor_shares(doctor)
        self.assertEqual(len(shares), 0)

        # Retrieving the revoked share should raise an error.
        with self.assertRaises(ValueError):
            share_store.get_active_share(record_id, doctor)


    def test_save_and_retrieve_note(self):
        record_id = 1
        doctor = "doctor1"
        note_text = "Patient check-up completed."
        signature = b"test_signature"

        share_store.save_note(
            record_id, doctor, note_text, signature
        )

        notes = share_store.get_record_notes(record_id)

        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0][0], doctor)
        self.assertEqual(notes[0][1], note_text)
        self.assertEqual(notes[0][3], signature)


if __name__ == "__main__":
    unittest.main()