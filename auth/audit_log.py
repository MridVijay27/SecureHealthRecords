
# Records important user actions in a hash-chained audit log.
# Each entry links to the previous one so changes can be detected.

import hashlib
from datetime import datetime
import db

# Previous hash used for the first entry when the log is empty.
GENESIS_HASH = "0" * 64


def create_audit_table():
    # Creates the audit log table if it does not already exist.
    conn = db.get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            entry_hash TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def compute_hash(prev_hash, timestamp, username, action):
    # Separators keep the fields distinct when generating the hash.
    entry_text = "|".join([
        prev_hash,
        timestamp,
        username,
        action
    ])

    return hashlib.sha256(
        entry_text.encode("utf-8")
    ).hexdigest()


def log_event(username, action):
    # Links each new event to the latest entry in the log.
    conn = db.get_connection()

    last_entry = conn.execute("""
        SELECT entry_hash
        FROM audit_log
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    # The first event uses the genesis hash because no previous entry exists.
    if last_entry is None:
        previous_hash = GENESIS_HASH
    else:
        previous_hash = last_entry[0]

    timestamp = datetime.now().isoformat(timespec="seconds")

    entry_hash = compute_hash(
        previous_hash,
        timestamp,
        username,
        action
    )

    conn.execute("""
        INSERT INTO audit_log
        (timestamp, username, action, prev_hash, entry_hash)
        VALUES (?, ?, ?, ?, ?)
    """, (
        timestamp,
        username,
        action,
        previous_hash,
        entry_hash
    ))

    conn.commit()
    conn.close()


def get_all_entries():
    # Returns the audit records in order for the GUI to display.
    conn = db.get_connection()

    entries = conn.execute("""
        SELECT id, timestamp, username, action, prev_hash, entry_hash
        FROM audit_log
        ORDER BY id
    """).fetchall()

    conn.close()
    return entries


def verify_chain():
    # Returns (True, None) if valid, or (False, id) for the first broken entry.
    entries = get_all_entries()
    expected_prev = GENESIS_HASH

    for entry in entries:
        entry_id, timestamp, username, action, prev_hash, entry_hash = entry

        # Detects broken links caused by deleted or reordered entries.
        if prev_hash != expected_prev:
            return False, entry_id

        calculated_hash = compute_hash(
            prev_hash,
            timestamp,
            username,
            action
        )

        # Detects changes to an entry's stored information.
        if calculated_hash != entry_hash:
            return False, entry_id

        expected_prev = entry_hash

    return True, None
