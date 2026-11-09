# Displays the dashboard based on the logged-in user's role.

import tkinter as tk
from tkinter import messagebox

from auth import audit_log
from gui.helpers import (
    clear_window,
    TITLE_FONT,
    SUBTITLE_FONT,
    MENU_BUTTON_WIDTH
)

from gui.records_screen import show_records_screen
from gui.sharing_screen import show_sharing_screen
from gui.doctor_screen import show_doctor_screen


def show_dashboard(window, user):
    # Displays the dashboard for the logged-in user.
    clear_window(window)

    frame = tk.Frame(window, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Welcome, " + user["username"],
        font=TITLE_FONT
    ).pack(pady=15)

    tk.Label(
        frame,
        text="Role: " + user["role"].capitalize(),
        font=SUBTITLE_FONT
    ).pack(pady=10)

    def coming_soon(feature_name):
        # Temporary placeholders until the other team features are connected.
        messagebox.showinfo(
            feature_name,
            feature_name + " will be available soon."
        )

    # Display features according to the user's role.
    if user["role"] == "patient":
        tk.Button(
            frame,
            text="My Records",
            width=MENU_BUTTON_WIDTH,
            command=lambda: show_records_screen(window, user)
        ).pack(pady=8)

        tk.Button(
            frame,
            text="Share a Record",
            width=MENU_BUTTON_WIDTH,
            command=lambda: show_sharing_screen(window, user)
        ).pack(pady=8)

    elif user["role"] == "doctor":
        tk.Button(
            frame,
            text="Shared With Me",
            width=MENU_BUTTON_WIDTH,
            command=lambda: show_doctor_screen(window, user)
        ).pack(pady=8)

    def open_audit_log():
        # Import here to avoid circular imports between GUI screens.
        from gui.audit_screen import show_audit_screen
        show_audit_screen(window, user)

    tk.Button(
        frame,
        text="Audit Log",
        width=MENU_BUTTON_WIDTH,
        command=open_audit_log
    ).pack(pady=8)

    def handle_logout():
        # Record logout before returning to the login screen.
        audit_log.log_event(user["username"], "LOGOUT")

        # Import here to avoid circular imports between GUI screens.
        from gui.login_screen import show_login
        show_login(window)

    tk.Button(
        frame,
        text="Logout",
        width=MENU_BUTTON_WIDTH,
        command=handle_logout
    ).pack(pady=15)
