
# Starts the Secure Health Records application.

import tkinter as tk

from auth.accounts import create_users_table
from auth.audit_log import create_audit_table
from gui.login_screen import show_login


def main():
    # Make sure the database tables exist before starting the application.
    create_users_table()
    create_audit_table()

    window = tk.Tk()
    window.title("Secure Health Records")
    window.geometry("700x500")

    show_login(window)

    # Keeps the window open and responding to user interactions.
    window.mainloop()


if __name__ == "__main__":
    main()
