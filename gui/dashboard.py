# Displays the dashboard based on the logged-in user's role.

import tkinter as tk
from tkinter import messagebox

from auth import audit_log
from gui.helpers import clear_window


def show_dashboard(window, user):
    # Displays the dashboard for the logged-in user.
    clear_window(window)

    frame = tk.Frame(window, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Welcome, " + user["username"],
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    tk.Label(
        frame,
        text="Role: " + user["role"].capitalize(),
        font=("Arial", 12)
    ).pack(pady=10)

    def coming_soon(feature_name):
        # Temporary message until the other team features are connected.
        messagebox.showinfo(
            feature_name,
            feature_name + " will be available soon."
        )

    # Show different features depending on the user's role.
    if user["role"] == "patient":
        tk.Button(
            frame,
            text="My Records",
            width=25,
            command=lambda: coming_soon("My Records")
        ).pack(pady=8)

        tk.Button(
            frame,
            text="Share a Record",
            width=25,
            command=lambda: coming_soon("Share a Record")
        ).pack(pady=8)

    elif user["role"] == "doctor":
        tk.Button(
            frame,
            text="Shared With Me",
            width=25,
            command=lambda: coming_soon("Shared With Me")
        ).pack(pady=8)

    tk.Button(
        frame,
        text="Audit Log",
        width=25,
        command=lambda: coming_soon("Audit Log")
    ).pack(pady=8)

    def handle_logout():
        # Record logout before returning to the login screen.
        audit_log.log_event(user["username"], "LOGOUT")

        #import here to avoid circular imports between the GUI screens.
        from gui.login_screen import show_login
        show_login(window)

    tk.Button(
        frame,
        text="Logout",
        width=25,
        command=handle_logout
    ).pack(pady=15)
