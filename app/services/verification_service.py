import random
import string
from typing import Dict
from datetime import datetime, timedelta, timezone

# Simple in-memory store: {email: (code, expiration)}
verification_store: Dict[str, tuple[str, datetime]] = {}

def generate_verification_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))

def save_verification_code(email: str, code: str, ttl_minutes: int = 10):
    verification_store[email] = (code, datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes))


def verify_code(email: str, code: str) -> bool:
    entry = verification_store.get(email)
    if not entry:
        return False
    saved_code, expires_at = entry
    return code == saved_code and datetime.now(timezone.utc) <= expires_at