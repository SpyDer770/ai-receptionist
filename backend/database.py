import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "receptionist.db"

CREATE_APPOINTMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS appointments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    phone         TEXT NOT NULL,
    date          TEXT NOT NULL,
    time          TEXT NOT NULL,
    purpose       TEXT,
    status        TEXT NOT NULL DEFAULT 'booked'
                  CHECK (status IN ('booked', 'cancelled')),
    created_at    TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""

# Holds the path currently in use. Tests can point this elsewhere.
_active_db_path = DB_PATH


def set_db_path(path) -> None:
    """Override which database file get_connection() uses. Used by tests."""
    global _active_db_path
    _active_db_path = path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_active_db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.execute(CREATE_APPOINTMENTS_TABLE)
        conn.commit()
    finally:
        conn.close()