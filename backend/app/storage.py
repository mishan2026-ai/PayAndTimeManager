from __future__ import annotations
import json
from pathlib import Path
from threading import Lock
from typing import Any, Dict

DATA_PATH = Path(__file__).resolve().parents[1] / "data"
DB_FILE = DATA_PATH / "db.json"
_lock = Lock()

DEFAULT_DB: Dict[str, Any] = {
    "workers": [],
    "time_entries": [],
    "deductions": []
}

DATA_PATH.mkdir(parents=True, exist_ok=True)
if not DB_FILE.exists():
    DB_FILE.write_text(json.dumps(DEFAULT_DB, indent=2, default=str), encoding="utf-8")

def read_db() -> Dict[str, Any]:
    with _lock:
        return json.loads(DB_FILE.read_text(encoding="utf-8"))

def write_db(data: Dict[str, Any]) -> None:
    with _lock:
        DB_FILE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

def get_collection(name: str) -> list:
    data = read_db()
    return data.get(name, [])

def update_collection(name: str, items: list) -> None:
    data = read_db()
    data[name] = items
    write_db(data)
