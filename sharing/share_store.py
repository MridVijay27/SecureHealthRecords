import db
from datetime import datetime

def create_sharing_tables():
    """Create the database tables required for secure record sharing."""

    conn = db.get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctor_keys (
            doctor TEXT PRIMARY KEY,
            public_key BLOB NOT NULL,
            private_key_salt BLOB NOT NULL,
            private_key_nonce BLOB NOT NULL,
            private_key_ciphertext BLOB NOT NULL,
            private_key_tag BLOB NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            patient TEXT NOT NULL,
            doctor TEXT NOT NULL,
            wrapped_key BLOB NOT NULL,
            created TEXT NOT NULL,
            revoked INTEGER NOT NULL DEFAULT 0,
            UNIQUE(record_id, doctor)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id INTEGER NOT NULL,
            doctor TEXT NOT NULL,
            note_text TEXT NOT NULL,
            created TEXT NOT NULL,
            signature BLOB NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_doctor_keys(doctor, public_key, encrypted_private_key):
    """Save a doctor's public key and encrypted private key."""

    conn = db.get_connection()

    conn.execute("""
        INSERT OR REPLACE INTO doctor_keys (
            doctor,
            public_key,
            private_key_salt,
            private_key_nonce,
            private_key_ciphertext,
            private_key_tag
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        doctor,
        public_key,
        encrypted_private_key["salt"],
        encrypted_private_key["nonce"],
        encrypted_private_key["ciphertext"],
        encrypted_private_key["tag"]
    ))

    conn.commit()
    conn.close() 


def get_doctor_public_key(doctor):
    """Retrieve a doctor's public key."""

    conn = db.get_connection()

    row = conn.execute("""
        SELECT public_key
        FROM doctor_keys
        WHERE doctor = ?
    """, (doctor,)).fetchone()

    conn.close()

    if row is None:
        raise ValueError("Doctor keys not found.")

    return row[0]


def get_encrypted_private_key(doctor):
    """Retrieve a doctor's encrypted private key."""

    conn = db.get_connection()

    row = conn.execute("""
        SELECT
            private_key_salt,
            private_key_nonce,
            private_key_ciphertext,
            private_key_tag
        FROM doctor_keys
        WHERE doctor = ?
    """, (doctor,)).fetchone()

    conn.close()

    if row is None:
        raise ValueError("Doctor keys not found.")

    return {
        "salt": row[0],
        "nonce": row[1],
        "ciphertext": row[2],
        "tag": row[3]
    }


def create_share(record_id, patient, doctor, wrapped_key):
    """Give a doctor access to a patient's encrypted record."""

    conn = db.get_connection()

    created = datetime.now().isoformat(timespec="seconds")

    conn.execute("""
        INSERT INTO shares (
            record_id,
            patient,
            doctor,
            wrapped_key,
            created
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(record_id, doctor)
        DO UPDATE SET
            wrapped_key = excluded.wrapped_key,
            patient = excluded.patient,
            created = excluded.created,
            revoked = 0
    """, (record_id, patient, doctor, wrapped_key, created))

    conn.commit()
    conn.close()


def get_doctor_shares(doctor):
    """Retrieve all active records shared with a doctor."""

    conn = db.get_connection()

    rows = conn.execute("""
        SELECT record_id, patient, wrapped_key, created
        FROM shares
        WHERE doctor = ? AND revoked = 0
        ORDER BY created DESC
    """, (doctor,)).fetchall()

    conn.close()

    return rows


def revoke_share(record_id, patient, doctor):
    """Revoke a doctor's access to a shared record."""

    conn = db.get_connection()

    result = conn.execute("""
        UPDATE shares
        SET revoked = 1
        WHERE record_id = ?
        AND patient = ?
        AND doctor = ?
        AND revoked = 0
    """, (record_id, patient, doctor))

    conn.commit()
    conn.close()

    return result.rowcount > 0


def get_active_share(record_id, doctor):
    """Retrieve an active share for a specific doctor and record."""

    conn = db.get_connection()

    row = conn.execute("""
        SELECT patient, wrapped_key
        FROM shares
        WHERE record_id = ?
        AND doctor = ?
        AND revoked = 0
    """, (record_id, doctor)).fetchone()

    conn.close()

    if row is None:
        raise ValueError("No active share found for this record.")

    return {
        "patient": row[0],
        "wrapped_key": row[1]
    }


def save_note(record_id, doctor, note_text, signature):
    """Save a doctor's digitally signed note."""

    conn = db.get_connection()

    created = datetime.now().isoformat(timespec="seconds")

    conn.execute("""
        INSERT INTO notes (
            record_id,
            doctor,
            note_text,
            created,
            signature
        )
        VALUES (?, ?, ?, ?, ?)
    """, (record_id, doctor, note_text, created, signature))

    conn.commit()
    conn.close()


def get_record_notes(record_id):
    """Retrieve all notes associated with a record."""

    conn = db.get_connection()

    rows = conn.execute("""
        SELECT doctor, note_text, created, signature
        FROM notes
        WHERE record_id = ?
        ORDER BY created DESC
    """, (record_id,)).fetchall()

    conn.close()

    return rows