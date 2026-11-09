# Contains small helper functions shared by the GUI screens.

# Shared styling constants keep all GUI screens looking the same.
TITLE_FONT = ("Arial", 20, "bold")
SUBTITLE_FONT = ("Arial", 12)
RESULT_FONT = ("Arial", 12, "bold")
HINT_FONT = ("Arial", 9)

ENTRY_WIDTH = 30
BUTTON_WIDTH = 20
MENU_BUTTON_WIDTH = 25

SUCCESS_COLOUR = "green"
ERROR_COLOUR = "red"
HINT_COLOUR = "gray"


def clear_window(window):
    # Removes existing widgets before displaying the next screen.
    for widget in window.winfo_children():
        widget.destroy()
