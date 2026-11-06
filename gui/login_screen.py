
# Login screen for the Secure Health Records application.

import tkinter as tk
from tkinter import messagebox

from auth import accounts
from gui.helpers import clear_window


def show_login(window):
    # Displays the login form and clears any previous screen.
    clear_window(window)

    frame = tk.Frame(window, padx=30, pady=30)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Secure Health Records",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    tk.Label(frame, text="Username").pack(anchor="w")

    username_entry = tk.Entry(frame, width=30)
    username_entry.pack(pady=5)

    tk.Label(frame, text="Password").pack(anchor="w")

    # Hide password characters from anyone looking at the screen.
    password_entry = tk.Entry(frame, width=30, show="*")
    password_entry.pack(pady=5)

    def handle_login():
        # Checks the entered credentials and displays the login result.
        username = username_entry.get()
        password = password_entry.get()

        success, message, user = accounts.login(username, password)

        if success:
            messagebox.showinfo("Login", message)

            # Temporary welcome screen until the dashboard is created.
            clear_window(window)

            tk.Label(
                window,
                text="Welcome, " + user["username"],
                font=("Arial", 18, "bold")
            ).pack(pady=40)

            tk.Label(
                window,
                text="Role: " + user["role"]
            ).pack(pady=10)

            tk.Button(
                window,
                text="Logout",
                command=lambda: show_login(window)
            ).pack(pady=20)

        else:
            messagebox.showerror("Login Failed", message)
            password_entry.delete(0, tk.END)

    tk.Button(
        frame,
        text="Login",
        width=20,
        command=handle_login
    ).pack(pady=15)

    # Registration will be connected when the register screen is ready.
    tk.Button(
        frame,
        text="Register",
        width=20,
        state="disabled"
    ).pack(pady=5)
