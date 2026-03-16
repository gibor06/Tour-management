from __future__ import annotations

import re

USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_.-]{3,30}")
PHONE_PATTERN = re.compile(r"0\d{9}")
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def normalize_username(username: str) -> str:
    return str(username or "").strip()


def normalize_fullname(fullname: str) -> str:
    return " ".join(str(fullname or "").strip().split())


def normalize_phone(phone: str) -> str:
    return str(phone or "").strip()


def is_valid_username(username: str) -> bool:
    return bool(USERNAME_PATTERN.fullmatch(normalize_username(username)))


def is_valid_password(password: str) -> bool:
    return len(str(password or "").strip()) >= 3


def is_valid_fullname(fullname: str) -> bool:
    return len(normalize_fullname(fullname)) >= 3


def is_valid_phone(phone: str) -> bool:
    value = normalize_phone(phone)
    return not value or bool(PHONE_PATTERN.fullmatch(value))


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(str(email or "").strip()))
