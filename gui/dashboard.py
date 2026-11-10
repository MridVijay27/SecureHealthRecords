# Displays the dashboard based on the logged-in user's role.

import tkinter as tk

from auth import audit_log
from gui.helpers import (
    clear_window,
    TITLE_FONT,
    SUBTITLE_FONT,
    MENU_BUTTON_WIDTH
)


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

    def open_records():
        # Import here to avoid circular imports between GUI screens.
        from gui.records_screen import show_records_screen
        show_records_screen(window, user)

    def open_sharing():
        # Import here to avoid circular imports between GUI screens.
        from gui.sharing_screen import show_sharing_screen
        show_sharing_screen(window, user)

    def open_doctor_screen():
        # Import here to avoid circular imports between GUI screens.
        from gui.doctor_screen import show_doctor_screen
        show_doctor_screen(window, user)

    # Display features according to the user's role.
    if user["role"] == "patient":
        tk.Button(
            frame,
            text="My Records",
            width=MENU_BUTTON_WIDTH,
            command=open_records
        ).pack(pady=8)

        tk.Button(
            frame,
            text="Share a Record",
            width=MENU_BUTTON_WIDTH,
            command=open_sharing
        ).pack(pady=8)

    elif user["role"] == "doctor":
        tk.Button(
            frame,
            text="Shared With Me",
            width=MENU_BUTTON_WIDTH,
            command=open_doctor_screen
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
