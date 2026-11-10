import tkinter as tk
from tkinter import messagebox, simpledialog

from auth import accounts
from gui.helpers import (
    clear_window,
    TITLE_FONT,
    SUBTITLE_FONT,
    BUTTON_WIDTH,
    SUCCESS_COLOUR,
    ERROR_COLOUR
)
from sharing import share_store
from sharing import key_manager
from sharing import signatures
from datetime import datetime
from records import record_store


def show_doctor_screen(window, user):
    clear_window(window)

    # Create the sharing database tables if they do not exist.
    share_store.create_sharing_tables()

    doctor = user["username"]

    # Ask the doctor to re-enter their password.
    password = simpledialog.askstring(
        "Doctor Verification",
        "Please enter your password:",
        show="*"
    )

    if not password:
        return

    # Verify the password using the existing login system.
    success, message, verified_user = accounts.login(doctor, password)

    if not success:
        messagebox.showerror("Verification Failed", message)
        return

    # Generate and store RSA keys only if the doctor has no keys yet.
    try:
        keys_created = share_store.setup_doctor_keys(doctor, password)

        if keys_created:
            messagebox.showinfo(
                "Security Setup",
                "Your secure RSA keys have been created successfully."
            )
        else:
            messagebox.showinfo(
                "Security Setup",
                "Your existing secure RSA keys have been loaded."
            )

    except Exception as error:
        messagebox.showerror("Security Error", str(error))
        return

    # Display the doctor screen.
    frame = tk.Frame(window, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Shared With Me",
        font=TITLE_FONT
    ).pack(pady=10)

    tk.Label(
        frame,
        text=f"Welcome, Dr. {doctor}",
        font=SUBTITLE_FONT
    ).pack(pady=5)

    def show_record_details(record_id, patient, record_text):
        details_window = tk.Toplevel(window)
        details_window.title("Patient Record and Medical Notes")
        details_window.geometry("600x600")

        tk.Label(
            details_window,
            text=f"Patient: {patient}",
            font=SUBTITLE_FONT
        ).pack(pady=10)

        tk.Label(
            details_window,
            text="Patient Record",
            font=SUBTITLE_FONT
        ).pack(pady=5)

        record_display = tk.Text(
            details_window,
            height=8,
            width=65,
            wrap="word"
        )
        record_display.pack(padx=10, pady=5)
        record_display.insert("1.0", record_text)
        record_display.config(state="disabled")

        tk.Label(
            details_window,
            text="Doctor's Medical Note",
            font=SUBTITLE_FONT
        ).pack(pady=10)

        note_input = tk.Text(
            details_window,
            height=6,
            width=65,
            wrap="word"
        )
        note_input.pack(padx=10, pady=5)


        def sign_and_save_note():
            note_text = note_input.get("1.0", "end-1c").strip()

            if not note_text:
                messagebox.showerror(
                    "Empty Note",
                    "Please enter a medical note before signing."
                )
                return

            password = simpledialog.askstring(
                "Confirm Identity",
                "Re-enter your password to sign this note:",
                show="*"
            )

            if not password:
                return

            try:
                encrypted_data = share_store.get_encrypted_private_key(doctor)

                private_key = key_manager.decrypt_private_key(
                    encrypted_data,
                    password
                )

                signature = signatures.sign_note(
                    note_text,
                    private_key
                )

                share_store.save_note(
                    record_id,
                    doctor,
                    note_text,
                    signature
                )

                messagebox.showinfo(
                    "Note Signed",
                    "Your medical note has been digitally signed and saved."
                )

                note_input.config(state="disabled")

            except Exception:
                messagebox.showerror(
                    "Signing Failed",
                    "Could not sign the note. Please check your password."
                )
        tk.Button(
            details_window,
            text="Save & Sign Note",
            width=BUTTON_WIDTH,
            command=sign_and_save_note
        ).pack(pady=10)

        def verify_saved_notes():
            notes = share_store.get_record_notes(record_id)

            if not notes:
                messagebox.showinfo(
                    "Medical Notes",
                    "No medical notes have been saved for this record."
                )
                return

            notes_window = tk.Toplevel(details_window)
            notes_window.title("Saved Medical Notes")
            notes_window.geometry("600x500")

            for note_doctor, note_text, created, signature in notes:

                tk.Label(
                    notes_window,
                    text=f"Doctor: {note_doctor} | Date: {created}",
                    font=SUBTITLE_FONT
                ).pack(pady=5)

                note_display = tk.Text(
                    notes_window,
                    height=4,
                    width=65,
                    wrap="word"
                )
                note_display.pack(padx=10, pady=5)
                note_display.insert("1.0", note_text)
                note_display.config(state="disabled")

                try:
                    public_key = share_store.get_doctor_public_key(
                        note_doctor
                    )

                    valid = signatures.verify_signature(
                        note_text,
                        signature,
                        public_key
                    )

                    if valid:
                        result = "Signature VALID"
                    else:
                        result = "Signature INVALID"

                except Exception:
                    result = "Signature could not be verified"

                tk.Label(
                    notes_window,
                    text=result
                ).pack(pady=5)

        tk.Button(
            details_window,
            text="View Saved Notes & Verify Signatures",
            width=40,
            command=verify_saved_notes
        ).pack(pady=10)

    # Retrieve records shared with this doctor.
    try:
        shares = share_store.get_doctor_shares(doctor)
    except Exception as error:
        messagebox.showerror("Sharing Error", str(error))
        shares = []


    if shares:
        tk.Label(
            frame,
            text="Patient records shared with you:"
        ).pack(pady=10)

        for record_id, patient, wrapped_key, created in shares:

            def open_shared_record(selected_record_id=record_id):
                password = simpledialog.askstring(
                    "Unlock Private Key",
                    "Re-enter your password to open this record:",
                    show="*"
                )

                if not password:
                    return

                try:
                    encrypted_data = share_store.get_encrypted_private_key(
                        doctor
                    )

                    private_key = key_manager.decrypt_private_key(
                        encrypted_data,
                        password
                    )

                    share = share_store.get_active_share(
                        selected_record_id,
                        doctor
                    )

                    record_key = key_manager.unwrap_record_key(
                        share["wrapped_key"],
                        private_key
                    )

                    record_text = record_store.open_record_with_key(
                        selected_record_id,
                        record_key
                    )

                    show_record_details(
                        selected_record_id,
                        share["patient"],
                        record_text
                    )

                except Exception:
                    messagebox.showerror(
                        "Access Failed",
                        "Could not open this record. Check your password "
                        "or whether the share is still active."
                    )

            tk.Button(
                frame,
                text=f"Open Record {record_id} - {patient}",
                width=BUTTON_WIDTH,
                command=open_shared_record
            ).pack(pady=5)

    else:
        tk.Label(
            frame,
            text="No patient records have been shared with you yet."
        ).pack(pady=15)


    def go_back():
        from gui.dashboard import show_dashboard
        show_dashboard(window, user)

    tk.Button(
        frame,
        text="Back",
        width=BUTTON_WIDTH,
        command=go_back
    ).pack(pady=10)
