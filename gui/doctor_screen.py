
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

                    messagebox.showinfo(
                        "Patient Record",
                        f"Patient: {share['patient']}\n\n{record_text}"
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
