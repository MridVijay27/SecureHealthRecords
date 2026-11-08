# Feature 2: shows that AES-GCM detects tampering. 

import db
from auth import audit_log
from records import record_store


def flip_one_bit(record_id):
    # Flips one bit of the record's stored ciphertext in the database.
    # Flipping the same bit a second time restores the original.
    conn = db.get_connection()

    row = conn.execute("""
        SELECT ciphertext
        FROM records
        WHERE id = ?
    """, (record_id,)).fetchone()

    if row is None:
        conn.close()
        raise ValueError("Record not found.")

    tampered = bytearray(row[0])
    tampered[0] ^= 1

    conn.execute("""
        UPDATE records
        SET ciphertext = ?
        WHERE id = ?
    """, (bytes(tampered), record_id))

    conn.commit()
    conn.close()


def simulate_tampering(record_id, patient, password):
    # Tampers with a record, tries to open it, then restores it.
    # Returns True if the tampering was detected.

    # Check the password first, so a wrong password is not mistaken for tampering.
    record_store.get_record_key(record_id, patient, password)

    flip_one_bit(record_id)

    try:
        record_store.open_record(record_id, patient, password)
        detected = False
    except ValueError:
        detected = True
        audit_log.log_event(patient, "TAMPER_DETECTED")
    finally:
        # Restore the record so the demo can be repeated.
        flip_one_bit(record_id)

    return detected