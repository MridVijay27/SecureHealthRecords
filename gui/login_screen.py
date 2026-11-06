# Login screen for the Secure Health Records application.

import tkinter as tk
from tkinter import messagebox

from auth import accounts
from gui.helpers import clear_window


def show_login(window):
    # Displays the login form and clears the previous screen.
    clear_window(window)

    frame = tk.Frame(window, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Secure Health Records",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    # Keep the form fields together so labels and boxes align correctly.
    form_frame = tk.Frame(frame)
    form_frame.pack(pady=15)

    tk.Label(form_frame, text="Username").pack(anchor="w")

    username_entry = tk.Entry(form_frame, width=30)
    username_entry.pack(pady=5, anchor="w")

    tk.Label(form_frame, text="Password").pack(anchor="w")

    # Hide the password from anyone looking at the screen.
    password_entry = tk.Entry(form_frame, width=30, show="*")
    password_entry.pack(pady=5, anchor="w")

    def handle_login():
        # Checks the entered credentials and opens the dashboard.
        username = username_entry.get()
        password = password_entry.get()

        success, message, user = accounts.login(username, password)

        if success:
            messagebox.showinfo("Login", message)

            # Import here to avoid circular imports between screens.
            from gui.dashboard import show_dashboard
            show_dashboard(window, user)

        else:
            messagebox.showerror("Login Failed", message)
            password_entry.delete(0, tk.END)

    def go_to_register():
        # Import here to avoid circular imports between GUI screens.
        from gui.register_screen import show_register
        show_register(window)

    tk.Button(
        frame,
        text="Login",
        width=20,
        command=handle_login
    ).pack(pady=10)

    tk.Button(
        frame,
        text="Register",
        width=20,
        command=go_to_register
    ).pack(pady=5)
