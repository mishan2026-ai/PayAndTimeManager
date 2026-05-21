from __future__ import annotations
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

DATA_PATH = Path(__file__).resolve().parents[1] / "data"
DB_FILE = DATA_PATH / "app.db"
_lock = Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    hourly_rate REAL NOT NULL,
    start_date TEXT,
    active INTEGER NOT NULL,
    leave_accrued REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS time_entries (
    id TEXT PRIMARY KEY,
    worker_id TEXT NOT NULL,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    notes TEXT,
    hours REAL NOT NULL,
    FOREIGN KEY(worker_id) REFERENCES workers(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS deductions (
    id TEXT PRIMARY KEY,
    worker_id TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    monthly INTEGER NOT NULL,
    FOREIGN KEY(worker_id) REFERENCES workers(id) ON DELETE CASCADE
);
"""


def ensure_db() -> None:
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    with _lock, sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)


def normalize_value(value: Any) -> Any:
    if isinstance(value, bool):
        return int(value)
    return value


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def get_collection(name: str) -> List[Dict[str, Any]]:
    ensure_db()
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(f"SELECT * FROM {name}")
        return [row_to_dict(row) for row in cursor.fetchall()]


def update_collection(name: str, items: list) -> None:
    ensure_db()
    if not items:
        with _lock, sqlite3.connect(DB_FILE) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(f"DELETE FROM {name}")
        return

    columns = [key for key in items[0].keys()]
    placeholders = ",".join("?" for _ in columns)
    query = f"INSERT INTO {name} ({','.join(columns)}) VALUES ({placeholders})"

    with _lock, sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(f"DELETE FROM {name}")
        conn.executemany(
            query,
            [[normalize_value(item[col]) for col in columns] for item in items],
        )
