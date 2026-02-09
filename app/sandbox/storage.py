# app/storage.py

import json
from pathlib import Path

DATA_FILE = Path("shared_list.json")


def ensure_file_exists():
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_items() -> list[str]:
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_items(items: list[str]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def clear_file():
    DATA_FILE.write_text("[]", encoding="utf-8")
