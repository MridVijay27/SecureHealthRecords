# Handles user registration, login and account lockout.

import time
import db
from auth import passwords, audit_log

# Lock accounts for 5 minutes after 3 failed login attempts.
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_SECONDS = 300

# Only these roles are allowed to register.
ALLOWED_ROLES = ("patient", "doctor")

# Use the same error for unknown usernames and incorrect passwords.
GENERIC_LOGIN_ERROR = "Invalid username or password."


def create_users_table():
    # Creates the users table if it does not already exist.
    conn = db.get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until REAL
        )
    """)

    conn.commit()
    conn.close()


def check_password_strength(password):
    # These rules make passwords harder to guess through brute-force attacks.
    if len(password) < 10:
        return False, "Password must have at least 10 characters."

    if not any(char.isupper() for char in password):
        return False, "Password must contain an uppercase letter."

    if not any(char.islower() for char in password):
        return False, "Password must contain a lowercase letter."

    if not any(char.isdigit() for char in password):
        return False, "Password must contain a number."

    return True, "Password is strong."


def register(username, password, role):
    # Validates registration details and stores a securely hashed password.

    # Lowercasing prevents duplicate usernames with different capitalisation.
    username = username.strip().lower()
    role = role.strip().lower()

    if not username:
        return False, "Username is required."

    # Restrict characters to avoid ambiguity in audit log hash fields.
    if not all(char.isalnum() or char == "_" for char in username):
        return False, "Username can only contain letters, numbers and underscores."

    if role not in ALLOWED_ROLES:
        return False, "Invalid role."

    strong, message = check_password_strength(password)

    if not strong:
        return False, message

    # Hash before opening the database to avoid holding the connection during hashing.
    salt, password_hash = passwords.hash_password(password)

    conn = db.get_connection()

    existing_user = conn.execute("""
        SELECT 1 FROM users WHERE username = ?
    """, (username,)).fetchone()

    if existing_user:
        conn.close()
        return False, "Username already exists."

    # Placeholders keep user input separate from SQL commands.
    conn.execute("""
        INSERT INTO users (username, role, salt, password_hash)
        VALUES (?, ?, ?, ?)
    """, (username, role, salt, password_hash))

    conn.commit()
    conn.close()

    audit_log.log_event(username, "REGISTER")

    return True, "Account created successfully."


def login(username, password):
    # Checks credentials and tracks failed attempts to prevent repeated guessing.
    username = username.strip().lower()

    # Reject unsupported characters to keep audit log fields unambiguous.
    if not username or not all(
        char.isalnum() or char == "_" for char in username
    ):
        passwords.verify_password(password, "00" * 16, "00" * 32)
        audit_log.log_event("invalid_username", "LOGIN_FAIL")
        return False, GENERIC_LOGIN_ERROR, None

    conn = db.get_connection()

    user = conn.execute("""
        SELECT role, salt, password_hash, failed_attempts, locked_until
        FROM users
        WHERE username = ?
    """, (username,)).fetchone()

    if user is None:
        conn.close()

        # Dummy verification reduces timing differences for unknown usernames.
        passwords.verify_password(password, "00" * 16, "00" * 32)

        audit_log.log_event(username, "LOGIN_FAIL")
        return False, GENERIC_LOGIN_ERROR, None

    role, salt, password_hash, failed_attempts, locked_until = user
    now = time.time()

    if locked_until is not None and locked_until > now:
        conn.close()
        audit_log.log_event(username, "LOGIN_BLOCKED")
        return False, "Account is locked. Try again later.", None

    if not passwords.verify_password(password, salt, password_hash):
        failed_attempts += 1

        # Lock the account after 3 failures to slow down password guessing.
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            conn.execute("""
                UPDATE users
                SET failed_attempts = 0, locked_until = ?
                WHERE username = ?
            """, (now + LOCKOUT_SECONDS, username))

            conn.commit()
            conn.close()

            audit_log.log_event(username, "ACCOUNT_LOCKED")

            return False, "Too many failed attempts. Account locked for 5 minutes.", None

        conn.execute("""
            UPDATE users
            SET failed_attempts = ?
            WHERE username = ?
        """, (failed_attempts, username))

        conn.commit()
        conn.close()

        audit_log.log_event(username, "LOGIN_FAIL")

        return False, GENERIC_LOGIN_ERROR, None

    conn.execute("""
        UPDATE users
        SET failed_attempts = 0, locked_until = NULL
        WHERE username = ?
    """, (username,))

    conn.commit()
    conn.close()

    audit_log.log_event(username, "LOGIN_OK")

    return True, "Login successful.", {
        "username": username,
        "role": role
    }


def get_users_by_role(role):
    """Retrieve usernames belonging to a specific role."""

    role = role.strip().lower()

    if role not in ALLOWED_ROLES:
        return []

    conn = db.get_connection()

    users = conn.execute("""
        SELECT username
        FROM users
        WHERE role = ?
        ORDER BY username
    """, (role,)).fetchall()

    conn.close()

    return [user[0] for user in users]
