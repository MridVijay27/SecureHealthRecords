# Tests registration, login security and audit log integrity.

import unittest
import tempfile
import os

import db
from auth import accounts, passwords, audit_log


# Automated tests for Feature 1: passwords, accounts and the audit log.
class TestAuthentication(unittest.TestCase):

    def setUp(self):
        # Use a separate database so tests do not change real user records.
        self.test_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db.DB_PATH
        db.DB_PATH = os.path.join(self.test_dir.name, "test_health.db")

        accounts.create_users_table()
        audit_log.create_audit_table()

    def tearDown(self):
        # Restore the original database path after each test.
        db.DB_PATH = self.original_db_path
        self.test_dir.cleanup()

    def test_register_user(self):
        # Check that a patient account can be registered successfully.
        success, message = accounts.register(
            "alice", "GoodPass123", "patient"
        )

        self.assertTrue(success)
        self.assertEqual(message, "Account created successfully.")

    def test_duplicate_username(self):
        # Usernames are case-insensitive, so ALICE should clash with alice.
        accounts.register("alice", "GoodPass123", "patient")

        success, message = accounts.register(
            "ALICE", "GoodPass123", "patient"
        )

        self.assertFalse(success)
        self.assertEqual(message, "Username already exists.")

    def test_weak_password(self):
        # Check that registration rejects passwords that are too weak.
        success, message = accounts.register(
            "alice", "weak", "patient"
        )

        self.assertFalse(success)
        self.assertIn("10 characters", message)

    def test_password_hashing(self):
        # Random salts should produce different hashes for the same password.
        salt1, hash1 = passwords.hash_password("GoodPass123")
        salt2, hash2 = passwords.hash_password("GoodPass123")

        self.assertNotEqual(salt1, salt2)
        self.assertNotEqual(hash1, hash2)

        self.assertTrue(
            passwords.verify_password("GoodPass123", salt1, hash1)
        )

        self.assertFalse(
            passwords.verify_password("WrongPass123", salt1, hash1)
        )

    def test_successful_login(self):
        # Check that correct credentials allow a user to log in.
        accounts.register("alice", "GoodPass123", "patient")

        success, message, user = accounts.login(
            "alice", "GoodPass123"
        )

        self.assertTrue(success)
        self.assertEqual(message, "Login successful.")
        self.assertEqual(user["username"], "alice")
        self.assertEqual(user["role"], "patient")

    def test_wrong_password(self):
        # Check that an incorrect password does not allow login.
        accounts.register("alice", "GoodPass123", "patient")

        success, message, user = accounts.login(
            "alice", "WrongPass123"
        )

        self.assertFalse(success)
        self.assertEqual(message, accounts.GENERIC_LOGIN_ERROR)
        self.assertIsNone(user)

    def test_account_lockout(self):
        # Three incorrect passwords should lock the account for five minutes.
        accounts.register("alice", "GoodPass123", "patient")

        for i in range(3):
            success, message, user = accounts.login(
                "alice", "WrongPass123"
            )
            self.assertFalse(success)

        self.assertIn("locked for 5 minutes", message)

        success, message, user = accounts.login(
            "alice", "GoodPass123"
        )

        self.assertFalse(success)
        self.assertEqual(
            message,
            "Account is locked. Try again later."
        )

    def test_invalid_username(self):
        # Check that usernames containing invalid characters are rejected.
        success, message = accounts.register(
            "bob|x", "GoodPass123", "doctor"
        )

        self.assertFalse(success)
        self.assertIn("letters, numbers and underscores", message)

    def test_invalid_role(self):
        # Only patient and doctor roles should be accepted.
        success, message = accounts.register(
            "bob", "GoodPass123", "nurse"
        )

        self.assertFalse(success)
        self.assertEqual(message, "Invalid role.")

    def test_audit_chain_valid(self):
        # Check that genuine audit events form a valid hash chain.
        audit_log.log_event("alice", "REGISTER")
        audit_log.log_event("alice", "LOGIN_OK")
        audit_log.log_event("alice", "LOGOUT")

        valid, broken_id = audit_log.verify_chain()

        self.assertTrue(valid)
        self.assertIsNone(broken_id)

    def test_audit_tampering(self):
        # Changing an existing event should make its stored hash invalid.
        audit_log.log_event("alice", "REGISTER")
        audit_log.log_event("alice", "LOGIN_OK")
        audit_log.log_event("alice", "LOGOUT")

        conn = db.get_connection()

        conn.execute("""
            UPDATE audit_log
            SET action = ?
            WHERE id = ?
        """, ("LOGIN_FAIL", 2))

        conn.commit()
        conn.close()

        valid, broken_id = audit_log.verify_chain()

        self.assertFalse(valid)
        self.assertEqual(broken_id, 2)

    def test_audit_deleted_entry(self):
        # Deleting a middle event should break the next entry's hash link.
        audit_log.log_event("alice", "REGISTER")
        audit_log.log_event("alice", "LOGIN_OK")
        audit_log.log_event("alice", "LOGOUT")

        conn = db.get_connection()

        conn.execute("""
            DELETE FROM audit_log
            WHERE id = ?
        """, (2,))

        conn.commit()
        conn.close()

        valid, broken_id = audit_log.verify_chain()

        self.assertFalse(valid)
        self.assertEqual(broken_id, 3)


if __name__ == "__main__":
    unittest.main()
