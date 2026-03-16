from __future__ import annotations

import hashlib
import re

SHA256_PATTERN = re.compile(r"[a-fA-F0-9]{64}")
MASKED_PASSWORD = "********"


def hash_password(raw_password: str) -> str:
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def looks_like_sha256(value: str) -> bool:
    return bool(SHA256_PATTERN.fullmatch(str(value).strip()))


def prepare_password_for_storage(password: str) -> str:
    normalized = str(password or "").strip()
    if not normalized:
        return ""
    if looks_like_sha256(normalized):
        return normalized
    return hash_password(normalized)


def password_matches(stored_password: str, input_password: str) -> bool:
    stored = str(stored_password or "").strip()
    provided = str(input_password or "")
    if not stored:
        return False
    if looks_like_sha256(stored):
        return hash_password(provided) == stored
    return stored == provided


def mask_password(_: str) -> str:
    return MASKED_PASSWORD
