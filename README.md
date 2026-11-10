# SecureHealthcareRecords

**H7SFD CA1 – Use Case 7**

Secure Healthcare Records is a desktop application built in Python that will enable patients and medical practitioners to handle out their medical data securely with the usage of encryption, authentication, digital signatures and audit logging.

## Team Members & Responsibility:

Member1:
- Mridhula Vijayakumar
- Feature 1: User accounts, login and audit log.

Member2:
- Dhruva Chaklasiya
- Feature 2: Encrypted healthcare records.

Member3:
- Megan Bates
- Feature 3: Record sharing and digital signatures.

## Features:

### Feature 1 – Accounts and Audit Log

- To register, use a unique username as a patient or doctor.
- Use salted password hashing to store passwords securely.
- Log on and off using the graphical login/logout interface.
- Lock accounts for a short duration if access is denied three times.
- Show alternative dashboards for each user type.
- Log user activities in an audit log.
- Use SHA-256 hash chains to check the audit log for changes.

### Feature 2 – Encrypted Healthcare Records

- Allow patients to create, view and manage their healthcare records.
- Support filing and attaching documents with health records.
- Encrypt data attached to records and stored records with AES-256-GCM.
- Derive the encryption key from patient's password by utilizing PBKDF2.
- Require the patient's password to unlock their encrypted records.
- Detect unauthorized changes in encrypted data by computing an integrity check.
- Add a tampering demo to verify that altered encrypted messages do not pass the verification test.

### Feature 3 – Sharing and Digital Signatures

- Allow patients to securely share selected healthcare records with doctors.
- Share information using RSA-OAEP hybrid encryption.
- Generate RSA public and private keys for doctors, with the private key protected using the doctor's password.
- Allow doctors to view records shared with them.
- Give patients the right to withdraw access to previously shared information.
- Use RSA-PSS digital signatures to sign clinical notes.
- Ensure that digital signatures are verified, for the purpose of confirming the authenticity and integrity of notes.
- Note detection in case of failure in the signature verification.

## Security at a Glance:
Feature -- Algorithm -- Security Goal

- 1). Passwords -- PBKDF2-HMAC-SHA256 -- Authentication.
- 2). Stored records -- AES-256-GCM -- Confidentiality and integrity.
- 3). Record sharing -- RSA-OAEP hybrid encryption -- Confidentiality.
- 4). Signed notes -- RSA-PSS -- Authenticity, integrity and non-repudiation.
- 5). Audit log -- SHA-256 hash chain -- Integrity.

## Setup and Installation
### Requirements:

- Python 3.10 or newer
- Windows, macOS or Linux
- Git or GitHub Desktop (optional if downloading ZIP)

### 1. Download the Project

Clone the GitHub repository:

```bash
git clone https://github.com/MridVijay27/SecureHealthRecords.git.
```

Alternatively, select **Code → Download ZIP** on GitHub and extract the downloaded folder.

Open terminal window in the project folder.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

If the activation is not successful in PowerShell, due to script execution being disabled, then run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then re-activate the environment again.

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

The Secure Healthcare Records login screen should appear.

First register as a patient or doctor, and then log in to access your patient or doctor dashboard.

## Running Automated Tests:

The project consists of automated tests of account registration, password security, account lock out, encrypted records, access sharing, audit log verification.

Run the tests from the project root:

```bash
python -m unittest discover tests -v
```

The expected result for the integrated project is:

```text
Ran 41 tests in ...s

OK
```

The tests use Python's built-in `unittest` framework.

## Project Structure:

```text
SecureHealthcareRecords/
│
| auth/
│   accounts.py
│   passwords.py
│   audit_log.py
│
| records/
│   record_crypto.py
|   record_store.py
│   attachment.py
|   tamper_demo.py
|
| gui/
│   helpers.py
│   login_screen.py
│   register_screen.py
│   dashboard.py
│   records_screen.py
│   sharing_screen.py
│   doctor_screen.py
│   audit_screen.py
│
| tests/
│   test_auth.py
│   test_records.py
|   test_key_manager.py
|   test_share_store.py
|   test_signatures.py
│
| data/
│   health.db (created locally)
│
| db.py
| main.py
| requirements.txt
| README.md
```

The `auth` folder includes the account registration, audit logging and password security. The files in the `records` folder are encrypted healthcare data and attachment management. The `sharing` folder includes secure record sharing, access revocations, and the management of RSA keys and digital signatures. The `gui` folder includes the application's Tkinter screens; the `tests` folder includes automated tests of all three features.

Application data is locally stored on the SQLite database.

## Current Scope:

This application was developed as part of H7SFD CA1. It provides examples of how cryptographic techniques can be used to secure healthcare information.

It is an educational project rather than a production healthcare system. It would require further access control, key management, security review, deployment protection etc. prior to use with real patient information.

