# Displays audit log entries and checks whether the hash chain is intact.

import tkinter as tk
from tkinter import ttk

from auth import audit_log
from gui.helpers import clear_window


def show_audit_screen(window, user):
    # Displays recorded activities and allows the user to verify the log.
    clear_window(window)

    frame = tk.Frame(window, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="Audit Log",
        font=("Arial", 20, "bold")
    ).pack(pady=10)

    table_frame = tk.Frame(frame)
    table_frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(
        table_frame,
        columns=("id", "time", "user", "action", "hash"),
        show="headings",
        height=10
    )

    tree.heading("id", text="ID")
    tree.heading("time", text="Timestamp")
    tree.heading("user", text="Username")
    tree.heading("action", text="Action")
    tree.heading("hash", text="Entry Hash")

    tree.column("id", width=50)
    tree.column("time", width=160)
    tree.column("user", width=110)
    tree.column("action", width=140)
    tree.column("hash", width=140)

    # A scrollbar makes longer audit logs easier to navigate.
    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for entry in audit_log.get_all_entries():
        entry_id, timestamp, username, action, prev_hash, entry_hash = entry

        # Show only the first 12 hash characters to keep the table readable.
        tree.insert(
            "",
            tk.END,
            values=(
                entry_id,
                timestamp,
                username,
                action,
                entry_hash[:12] + "..."
            )
        )

    result_label = tk.Label(
        frame,
        text="",
        font=("Arial", 12, "bold")
    )
    result_label.pack(pady=8)

    def handle_verify():
        # Checks each entry's hash and its link to the previous entry.
        valid, broken_id = audit_log.verify_chain()

        if valid:
            result_label.config(
                text="Log intact: no tampering detected",
                fg="green"
            )
        else:
            result_label.config(
                text="Tampering detected at entry #" + str(broken_id),
                fg="red"
            )

    def go_back():
        # Import here to avoid circular imports between GUI screens.
        from gui.dashboard import show_dashboard
        show_dashboard(window, user)

    tk.Button(
        frame,
        text="Verify Log",
        width=20,
        command=handle_verify
    ).pack(pady=5)

    tk.Button(
        frame,
        text="Back",
        width=20,
        command=go_back
    ).pack(pady=5)
