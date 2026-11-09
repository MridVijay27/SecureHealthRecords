# Feature 2: saves, lists, opens and edits a patient's encrypted records in the database.
# Each record has its own random AES-256 key (the "record key"). 

from datetime import datetime
from Crypto.Random import get_random_bytes
import db
from auth import audit_log
from records.record_crypto import derive_key, encrypt, decrypt, KEY_LENGTH
from records.attachments import encrypt_file, decrypt_file



def create_records_table():
        # Creates the records table if it does not already exist.

    conn = db.get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient TEXT NOT NULL,
            title TEXT NOT NULL,
            created TEXT NOT NULL,
            salt BLOB NOT NULL,
            key_nonce BLOB NOT NULL,
            wrapped_key BLOB NOT NULL,
            key_tag BLOB NOT NULL,
            nonce BLOB NOT NULL,
            ciphertext BLOB NOT NULL,
            tag BLOB NOT NULL,
            attachment_name TEXT,
            att_nonce BLOB,
            att_ciphertext BLOB,
            att_tag BLOB
        )
    """)
    conn.commit()
    conn.close()

    

def create_record(patient, password, title, text):
    # Encrypts a new record and saves it. Returns the new record's id.

    # Each record gets its own random key, so one record can be shared without exposing others.
    record_key = get_random_bytes(KEY_LENGTH)

    # The record key is locked with a key derived from the patient's password.
    salt = get_random_bytes(16)
    password_key = derive_key(password, salt)
    key_nonce, wrapped_key, key_tag = encrypt(password_key, record_key)

    # The record text is locked with the record key.
    nonce, ciphertext, tag = encrypt(record_key, text.encode("utf-8"))

    created = datetime.now().isoformat(timespec="seconds")

    conn = db.get_connection()

    # ?  prevent SQL injection.
    result = conn.execute("""
        INSERT INTO records
        (patient, title, created, salt, key_nonce, wrapped_key, key_tag,
         nonce, ciphertext, tag)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient,
        title,
        created,
        salt,
        key_nonce,
        wrapped_key,
        key_tag,
        nonce,
        ciphertext,
        tag
    ))

    record_id = result.lastrowid

    conn.commit()
    conn.close()

    audit_log.log_event(patient, "RECORD_CREATED")
    return record_id


def list_records(patient):
    # Returns (id, title, created, attachment_name) for each of the patient's records.
    conn = db.get_connection()

    rows = conn.execute("""
        SELECT id, title, created, attachment_name
        FROM records
        WHERE patient = ?
        ORDER BY id
    """, (patient,)).fetchall()

    conn.close()
    return rows


def get_record_key(record_id, patient, password):
    # Unlocks a record's key with the patient's password.
    # Member 3 uses this to share a single record with a doctor.
    # Raises ValueError if the password is wrong or the stored key was changed.
    conn = db.get_connection()

    row = conn.execute("""
        SELECT salt, key_nonce, wrapped_key, key_tag
        FROM records
        WHERE id = ? AND patient = ?
    """, (record_id, patient)).fetchone()

    conn.close()

    if row is None:
        raise ValueError("Record not found.")

    salt, key_nonce, wrapped_key, key_tag = row
    password_key = derive_key(password, salt)

    return decrypt(password_key, key_nonce, wrapped_key, key_tag)


def open_record_with_key(record_id, record_key):
    # Decrypts a record's text using its record key.
    # Member 3's doctor screen uses this after unwrapping a shared key.
    conn = db.get_connection()

    row = conn.execute("""
        SELECT nonce, ciphertext, tag
        FROM records
        WHERE id = ?
    """, (record_id,)).fetchone()

    conn.close()

    if row is None:
        raise ValueError("Record not found.")

    nonce, ciphertext, tag = row

    return decrypt(record_key, nonce, ciphertext, tag).decode("utf-8")


def open_record(record_id, patient, password):
    # Opens one of the patient's own records and returns its text.
    record_key = get_record_key(record_id, patient, password)
    text = open_record_with_key(record_id, record_key)

    audit_log.log_event(patient, "RECORD_OPENED")
    return text


def edit_record(record_id, patient, password, new_text):
    # Replaces a record's text. It is re-encrypted with a fresh nonce.
    record_key = get_record_key(record_id, patient, password)
    nonce, ciphertext, tag = encrypt(record_key, new_text.encode("utf-8"))

    conn = db.get_connection()

    conn.execute("""
        UPDATE records
        SET nonce = ?, ciphertext = ?, tag = ?
        WHERE id = ? AND patient = ?
    """, (nonce, ciphertext, tag, record_id, patient))

    conn.commit()
    conn.close()

    audit_log.log_event(patient, "RECORD_EDITED")


def attach_file(record_id, patient, password, file_path):
    # Encrypts a file with the record's key and attaches it to the record.
    record_key = get_record_key(record_id, patient, password)
    name, nonce, ciphertext, tag = encrypt_file(record_key, file_path)

    conn = db.get_connection()

    conn.execute("""
        UPDATE records
        SET attachment_name = ?, att_nonce = ?, att_ciphertext = ?, att_tag = ?
        WHERE id = ? AND patient = ?
    """, (name, nonce, ciphertext, tag, record_id, patient))

    conn.commit()
    conn.close()

    audit_log.log_event(patient, "ATTACHMENT_ADDED")


def save_attachment(record_id, patient, password, output_path):
    # Decrypts a record's attachment and saves it to output_path.
    # Raises ValueError if there is no attachment or it was tampered with.
    record_key = get_record_key(record_id, patient, password)

    conn = db.get_connection()

    row = conn.execute("""
        SELECT att_nonce, att_ciphertext, att_tag
        FROM records
        WHERE id = ?
    """, (record_id,)).fetchone()

    conn.close()

    if row is None or row[1] is None:
        raise ValueError("This record has no attachment.")

    nonce, ciphertext, tag = row
    decrypt_file(record_key, nonce, ciphertext, tag, output_path)

    audit_log.log_event(patient, "ATTACHMENT_OPENED")