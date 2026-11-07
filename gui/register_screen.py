# Displays the account registration screen.

import tkinter as tk
from tkinter import messagebox, ttk

from auth import accounts
from gui.helpers import (
    clear_window,
    TITLE_FONT,
    HINT_FONT,
    ENTRY_WIDTH,
    BUTTON_WIDTH,
    HINT_COLOUR
)


def show_register(window):
    # Displays the registration form and clears the previous screen.
    clear_window(window)

    frame = tk.Frame(window, padx=30, pady=20)
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="Create Account",
        font=TITLE_FONT
    ).pack(pady=15)

    # Keep all registration fields aligned on the left.
    form_frame = tk.Frame(frame)
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="Username").pack(anchor="w")

    username_entry = tk.Entry(form_frame, width=ENTRY_WIDTH)
    username_entry.pack(pady=5, anchor="w")

    tk.Label(form_frame, text="Password").pack(anchor="w")

    # Hide passwords so they cannot be read by someone looking at the screen.
    password_entry = tk.Entry(
        form_frame,
        width=ENTRY_WIDTH,
        show="*"
    )
    password_entry.pack(pady=5, anchor="w")

    tk.Label(form_frame, text="Confirm Password").pack(anchor="w")

    confirm_entry = tk.Entry(
        form_frame,
        width=ENTRY_WIDTH,
        show="*"
    )
    confirm_entry.pack(pady=5, anchor="w")

    tk.Label(
        form_frame,
        text="10+ characters, uppercase, lowercase and a number",
        font=HINT_FONT,
        fg=HINT_COLOUR
    ).pack(pady=5, anchor="w")

    tk.Label(form_frame, text="Role").pack(anchor="w")

    role_box = ttk.Combobox(
        form_frame,
        values=["Patient", "Doctor"],
        state="readonly",
        width=27
    )
    role_box.pack(pady=5, anchor="w")
    role_box.current(0)

    def go_to_login():
        # Import here to avoid circular imports between GUI screens.
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
        width=BUTTON_WIDTH,
        command=handle_register
    ).pack(pady=10)

    tk.Button(
        frame,
        text="Back to Login",
        width=BUTTON_WIDTH,
        command=go_to_login
    ).pack(pady=5)
