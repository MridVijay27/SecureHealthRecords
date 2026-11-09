# Patient screen for Feature 2: create, list, open, edit and attach files to encrypted records.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from auth import accounts
from records import record_store, tamper_demo
from gui.helpers import (
    clear_window,
    TITLE_FONT,
    SUBTITLE_FONT,
    RESULT_FONT,
    ENTRY_WIDTH,
    BUTTON_WIDTH,
    SUCCESS_COLOUR,
    ERROR_COLOUR
)


def show_records_screen(window, user):
    # Asks the patient to re-enter their password before showing their records.
    clear_window(window)
    record_store.create_records_table()

    frame = tk.Frame(window, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="My Records",
        font=TITLE_FONT
    ).pack(pady=15)

    tk.Label(
        frame,
        text="Re-enter your password to unlock your records",
        font=SUBTITLE_FONT
    ).pack(pady=5)

    # Hide the password from anyone looking at the screen.
    password_entry = tk.Entry(frame, width=ENTRY_WIDTH, show="*")
    password_entry.pack(pady=10)
    password_entry.focus()

    def handle_unlock():
        # Re-checks the password using the login rules, including lockout.
        password = password_entry.get()
        success, message, checked_user = accounts.login(user["username"], password)

        if success:
            show_records_list(window, user, password)
        else:
            messagebox.showerror("Unlock Failed", message)
            password_entry.delete(0, tk.END)

    def go_back():
        # Import here to avoid circular imports between GUI screens.
        window.unbind("<Return>")
        from gui.dashboard import show_dashboard
        show_dashboard(window, user)

    tk.Button(
        frame,
        text="Unlock",
        width=BUTTON_WIDTH,
        command=handle_unlock
    ).pack(pady=5)

    tk.Button(
        frame,
        text="Back",
        width=BUTTON_WIDTH,
        command=go_back
    ).pack(pady=5)

    window.bind("<Return>", lambda event: handle_unlock())


def show_records_list(window, user, password):
    # Lists the patient's records and lets them create, open, edit and attach files.
    # The password is kept only in memory while this screen is open.
    clear_window(window)
    window.unbind("<Return>")

    patient = user["username"]

    frame = tk.Frame(window, padx=20, pady=10)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="My Records",
        font=TITLE_FONT
    ).pack(pady=5)

    # Table of records. Titles are shown, but the record text stays encrypted.
    tree = ttk.Treeview(
        frame,
        columns=("id", "title", "created", "attachment"),
        show="headings",
        height=5
    )

    tree.heading("id", text="ID")
    tree.heading("title", text="Title")
    tree.heading("created", text="Created")
    tree.heading("attachment", text="Attachment")

    tree.column("id", width=40)
    tree.column("title", width=200)
    tree.column("created", width=150)
    tree.column("attachment", width=150)

    tree.pack(fill="x")

    # Form for the title and text of the record being created or edited.
    form_frame = tk.Frame(frame)
    form_frame.pack(fill="x", pady=5)

    tk.Label(form_frame, text="Title").grid(row=0, column=0, sticky="w")

    title_entry = tk.Entry(form_frame, width=50)
    title_entry.grid(row=0, column=1, sticky="w", padx=5)

    tk.Label(form_frame, text="Text").grid(row=1, column=0, sticky="nw")

    text_box = tk.Text(form_frame, width=60, height=5)
    text_box.grid(row=1, column=1, sticky="w", padx=5, pady=5)

    result_label = tk.Label(frame, text="", font=RESULT_FONT)
    result_label.pack(pady=2)

    def show_result(message, colour):
        # Shows the outcome of the last action under the form.
        result_label.config(text=message, fg=colour)

    def refresh_list():
        # Reloads the table from the database.
        for row in tree.get_children():
            tree.delete(row)

        for record_id, title, created, attachment in record_store.list_records(patient):
            tree.insert(
                "",
                tk.END,
                values=(record_id, title, created, attachment or "-")
            )

    def selected_record_id():
        # Returns the id of the record selected in the table, or None.
        selection = tree.selection()

        if not selection:
            messagebox.showwarning("No Record Selected", "Please select a record first.")
            return None

        return tree.item(selection[0])["values"][0]

    def clear_form():
        # Empties the title and text boxes.
        title_entry.delete(0, tk.END)
        text_box.delete("1.0", tk.END)

    def handle_new():
        # Encrypts the form contents as a new record.
        title = title_entry.get().strip()
        text = text_box.get("1.0", tk.END).strip()

        if not title or not text:
            messagebox.showwarning("Missing Details", "Please enter a title and some text.")
            return

        record_store.create_record(patient, password, title, text)
        clear_form()
        refresh_list()
        show_result("Record encrypted and saved.", SUCCESS_COLOUR)

    def handle_open():
        # Decrypts the selected record and shows it in the form.
        record_id = selected_record_id()

        if record_id is None:
            return

        try:
            text = record_store.open_record(record_id, patient, password)
        except ValueError:
            show_result("Record rejected: it has been changed or damaged.", ERROR_COLOUR)
            return

        clear_form()
        title_entry.insert(0, tree.item(tree.selection()[0])["values"][1])
        text_box.insert("1.0", text)
        show_result("Record decrypted and integrity verified.", SUCCESS_COLOUR)

    def handle_save_changes():
        # Re-encrypts the edited text of the selected record.
        record_id = selected_record_id()

        if record_id is None:
            return

        text = text_box.get("1.0", tk.END).strip()

        if not text:
            messagebox.showwarning("Missing Details", "The record text cannot be empty.")
            return

        try:
            record_store.edit_record(record_id, patient, password, text)
        except ValueError:
            show_result("Could not save: the record has been changed or damaged.", ERROR_COLOUR)
            return

        show_result("Changes encrypted and saved.", SUCCESS_COLOUR)

    def handle_attach():
        # Encrypts a chosen file and attaches it to the selected record.
        record_id = selected_record_id()

        if record_id is None:
            return

        file_path = filedialog.askopenfilename(title="Choose a file to attach")

        if not file_path:
            return

        try:
            record_store.attach_file(record_id, patient, password, file_path)
        except (ValueError, OSError) as error:
            show_result("Could not attach file: " + str(error), ERROR_COLOUR)
            return

        refresh_list()
        show_result("File encrypted and attached.", SUCCESS_COLOUR)

    def handle_save_attachment():
        # Decrypts the selected record's attachment and saves it where the patient chooses.
        record_id = selected_record_id()

        if record_id is None:
            return

        attachment_name = tree.item(tree.selection()[0])["values"][3]

        if attachment_name == "-":
            messagebox.showinfo("No Attachment", "This record has no attachment.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save decrypted attachment",
            initialfile=attachment_name
        )

        if not output_path:
            return

        try:
            record_store.save_attachment(record_id, patient, password, output_path)
        except ValueError:
            show_result("Attachment rejected: it has been changed or damaged.", ERROR_COLOUR)
            return

        show_result("Attachment decrypted and saved.", SUCCESS_COLOUR)

    def handle_tamper():
        # Changes one bit of the stored record and shows that decryption is refused.
        record_id = selected_record_id()

        if record_id is None:
            return

        if tamper_demo.simulate_tampering(record_id, patient, password):
            show_result(
                "Tampering detected: AES-GCM tag check failed, record refused.",
                ERROR_COLOUR
            )
            messagebox.showwarning(
                "Tampering Detected",
                "One bit of record #" + str(record_id) + " was changed in the database.\n\n"
                "Decryption was refused because the GCM authentication tag no longer matches.\n\n"
                "The record has now been restored for this demonstration."
            )
        else:
            show_result("Tampering was NOT detected.", ERROR_COLOUR)

    def go_back():
        # Import here to avoid circular imports between GUI screens.
        from gui.dashboard import show_dashboard
        show_dashboard(window, user)

    # Two rows of buttons so the screen fits the 700x500 window.
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=5)

    buttons = [
        ("New Record", handle_new),
        ("Open", handle_open),
        ("Save Changes", handle_save_changes),
        ("Attach File", handle_attach),
        ("Save Attachment", handle_save_attachment),
        ("Simulate Tampering", handle_tamper),
        ("Clear Form", clear_form),
        ("Back", go_back)
    ]

    for index, (text, command) in enumerate(buttons):
        tk.Button(
            button_frame,
            text=text,
            width=16,
            command=command
        ).grid(row=index // 4, column=index % 4, padx=4, pady=3)

    refresh_list()