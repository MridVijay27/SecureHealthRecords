import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from auth import audit_log
from sharing import key_manager

from auth import accounts
from records import record_store
from gui.helpers import (
    clear_window,
    TITLE_FONT,
    SUBTITLE_FONT,
    BUTTON_WIDTH,
    SUCCESS_COLOUR,
    ERROR_COLOUR
)
from sharing import share_store


def show_sharing_screen(window, user):
    clear_window(window)

    record_store.create_records_table()
    share_store.create_sharing_tables()

    frame = tk.Frame(window, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Share a Record",
        font=TITLE_FONT
    ).pack(pady=10)

    tk.Label(
        frame,
        text="Choose a record and a doctor to share it with.",
        font=SUBTITLE_FONT
    ).pack(pady=5)

    # Load the patient's records.
    patient = user["username"]
    records = record_store.list_records(patient)

    tk.Label(frame, text="Select Record").pack(pady=5)

    record_options = {
        f"{record_id} - {title}": record_id
        for record_id, title, created, attachment in records
    }

    record_dropdown = ttk.Combobox(
        frame,
        values=list(record_options.keys()),
        state="readonly",
        width=40
    )
    record_dropdown.pack(pady=5)

    # Load registered doctors.
    doctors = accounts.get_users_by_role("doctor")

    tk.Label(frame, text="Select Doctor").pack(pady=5)

    doctor_dropdown = ttk.Combobox(
        frame,
        values=doctors,
        state="readonly",
        width=40
    )
    doctor_dropdown.pack(pady=5)

    result_label = tk.Label(frame, text="")
    result_label.pack(pady=10)

    if not records:
        result_label.config(
            text="You have no records to share.",
            fg=ERROR_COLOUR
        )

    elif not doctors:
        result_label.config(
            text="No registered doctors were found.",
            fg=ERROR_COLOUR
        )


    def handle_share():
        # Check that the patient selected a record and doctor.
        selected_record = record_dropdown.get()
        selected_doctor = doctor_dropdown.get()

        if not selected_record:
            messagebox.showerror(
                "Missing Record",
                "Please select a record to share."
            )
            return

        if not selected_doctor:
            messagebox.showerror(
                "Missing Doctor",
                "Please select a doctor."
            )
            return

        # Ask the patient to verify their password.
        password = simpledialog.askstring(
            "Patient Verification",
            "Re-enter your password to share this record:",
            show="*"
        )

        if not password:
            return

        try:
            # Verify the patient's password.
            success, message, verified_user = accounts.login(
                patient,
                password
            )

            if not success:
                messagebox.showerror("Verification Failed", message)
                return

            # Get the selected record ID.
            record_id = record_options[selected_record]

            # Retrieve the patient's AES record key.
            record_key = record_store.get_record_key(
                record_id,
                patient,
                password
            )

            # Retrieve the selected doctor's RSA public key.
            doctor_public_key = share_store.get_doctor_public_key(
                selected_doctor
            )

            # Encrypt the AES key using the doctor's public key.
            wrapped_key = key_manager.wrap_record_key(
                record_key,
                doctor_public_key
            )

            # Save the secure share.
            share_store.create_share(
                record_id,
                patient,
                selected_doctor,
                wrapped_key
            )

            # Record the sharing event.
            audit_log.log_event(patient, "RECORD_SHARED")

            result_label.config(
                text="Record shared successfully!",
                fg=SUCCESS_COLOUR
            )

            messagebox.showinfo(
                "Sharing Successful",
                "Your record has been securely shared with "
                + selected_doctor + "."
            )

        except ValueError as error:
            messagebox.showerror("Sharing Failed", str(error))

        except Exception:
            messagebox.showerror(
                "Sharing Failed",
                "An unexpected error occurred while sharing the record."
            )



    def go_back():
        from gui.dashboard import show_dashboard
        show_dashboard(window, user)

    tk.Button(
        frame,
        text="Share Record",
        width=BUTTON_WIDTH,
        command=handle_share
    ).pack(pady=5)

        # Display records currently shared with doctors.
    tk.Label(
        frame,
        text="Currently Shared Records",
        font=SUBTITLE_FONT
    ).pack(pady=10)

    share_options = {}

    share_dropdown = ttk.Combobox(
        frame,
        values=[],
        state="readonly",
        width=40
    )
    share_dropdown.pack(pady=5)

    def refresh_shares():
        # Get all active shares belonging to this patient.
        shares = share_store.get_patient_shares(patient)

        # Clear the existing dropdown options.
        share_options.clear()

        display_options = []

        for record_id, doctor, created in shares:
            display_text = (
                f"Record {record_id} - {doctor} ({created})"
            )

            display_options.append(display_text)
            share_options[display_text] = (record_id, doctor)

        # Update the dropdown.
        share_dropdown["values"] = display_options

        if display_options:
            share_dropdown.current(0)
        else:
            share_dropdown.set("")

    # Load the shares when the screen opens.
    refresh_shares()


    def handle_revoke():
        selected_share = share_dropdown.get()

        if not selected_share:
            messagebox.showerror(
                "No Share Selected",
                "Please select a shared record to revoke."
            )
            return

        password = simpledialog.askstring(
            "Patient Verification",
            "Re-enter your password to revoke access:",
            show="*"
        )

        if not password:
            return

        try:
            success, message, verified_user = accounts.login(
                patient,
                password
            )

            if not success:
                messagebox.showerror("Verification Failed", message)
                return

            confirmed = messagebox.askyesno(
                "Confirm Revocation",
                "Are you sure you want to revoke this doctor's access?"
            )

            if not confirmed:
                return

            record_id, doctor = share_options[selected_share]

            revoked = share_store.revoke_share(
                record_id,
                patient,
                doctor
            )

            if revoked:
                audit_log.log_event(patient, "SHARE_REVOKED")

                messagebox.showinfo(
                    "Access Revoked",
                    f"{doctor} can no longer access this shared record."
                )

                refresh_shares()

            else:
                messagebox.showerror(
                    "Revocation Failed",
                    "The share could not be found or is already revoked."
                )

        except Exception:
            messagebox.showerror(
                "Revocation Failed",
                "An unexpected error occurred while revoking access."
            )

    tk.Button(
        frame,
        text="Revoke Access",
        width=BUTTON_WIDTH,
        command=handle_revoke
    ).pack(pady=5)

    tk.Button(
        frame,
        text="Back",
        width=BUTTON_WIDTH,
        command=go_back
    ).pack(pady=5)