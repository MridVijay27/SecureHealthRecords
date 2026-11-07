# Shared SQLite database connection used by all project features.

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "health.db")


def get_connection():
    folder = os.path.dirname(DB_PATH)

    if folder:
        os.makedirs(folder, exist_ok=True)

    return sqlite3.connect(DB_PATH, timeout=10)
