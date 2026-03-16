from __future__ import annotations

import json
import os
from datetime import datetime


def _resolve_log_file(datastore=None, log_file: str | None = None) -> str:
    if log_file:
        return log_file
    if datastore is not None and getattr(datastore, "path", None):
        return os.path.join(os.path.dirname(datastore.path), "activity_logs.json")
    return os.path.join(os.getcwd(), "activity_logs.json")


def _load_entries(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    return data if isinstance(data, list) else []


def write_activity_log(
    action: str,
    actor: str,
    role: str,
    status: str,
    detail: str = "",
    datastore=None,
    log_file: str | None = None,
) -> None:
    path = _resolve_log_file(datastore=datastore, log_file=log_file)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    entries = _load_entries(path)
    entries.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "actor": actor,
            "role": role,
            "action": action,
            "status": status,
            "detail": detail,
        }
    )

    with open(path, "w", encoding="utf-8") as file:
        json.dump(entries[-1000:], file, ensure_ascii=False, indent=2)
