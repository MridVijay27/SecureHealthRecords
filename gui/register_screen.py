# Displays the account registration screen.

import tkinter as tk
from tkinter import messagebox, ttk

from auth import accounts
from gui.helpers import clear_window


def show_register(window):
    # Displays the registration form and clears the previous screen.
    clear_window(window)

    frame = tk.Frame(window, padx=30, pady=20)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Create Account",
        font=("Arial", 20, "bold")
    ).pack(pady=15)

    tk.Label(frame, text="Username").pack(anchor="w")

    username_entry = tk.Entry(frame, width=30)
    username_entry.pack(pady=5, anchor="w")

    tk.Label(frame, text="Password").pack(anchor="w")

    # Hide passwords so they cannot be read by someone looking at the screen.
    password_entry = tk.Entry(frame, width=30, show="*")
    password_entry.pack(pady=5, anchor="w")

    tk.Label(frame, text="Confirm Password").pack(anchor="w")

    confirm_entry = tk.Entry(frame, width=30, show="*")
    confirm_entry.pack(pady=5, anchor="w")

    tk.Label(
        frame,
        text="10+ characters, uppercase, lowercase and a number",
        font=("Arial", 9),
        fg="gray"
    ).pack(pady=5)

    tk.Label(frame, text="Role").pack(anchor="w")

    role_box = ttk.Combobox(
        frame,
        values=["Patient", "Doctor"],
        state="readonly",
        width=27
    )
    role_box.pack(pady=5, anchor="w")
    role_box.current(0)

    def go_to_login():
        # Import here to avoid circular imports between the GUI screens.
        from gui.login_screen import show_login
        show_login(window)

    def handle_register():
        # Checks the form details before creating the account.
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_entry.get()
        role = role_box.get()

        if password != confirm_password:
            messagebox.showerror(
                "Registration Failed",
                "Passwords do not match."
            )
            password_entry.delete(0, tk.END)
            confirm_entry.delete(0, tk.END)
            return

        success, message = accounts.register(username, password, role)

        if success:
            messagebox.showinfo("Registration", message)
            go_to_login()
        else:
            messagebox.showerror("Registration Failed", message)
            password_entry.delete(0, tk.END)
            confirm_entry.delete(0, tk.END)

    tk.Button(
        frame,
        text="Register",
        width=20,
        command=handle_register
    ).pack(pady=15)

    tk.Button(
        frame,
        text="Back to Login",
        width=20,
        command=go_to_login
    ).pack(pady=5)
