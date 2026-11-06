# Contains small helper functions shared by the GUI screens.


def clear_window(window):
    # Removes existing widgets so the next screen starts with a blank window.
    for widget in window.winfo_children():
        widget.destroy()
