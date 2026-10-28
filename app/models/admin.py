from datetime import datetime, timezone


def admin_document(
    name: str,
    email: str,
    password_hash: str,
    is_active: bool = True,
):
    now = datetime.now(timezone.utc)

    return {
        "name": name,
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "role": "admin",
        "is_active": is_active,
        "created_at": now,
        "updated_at": now,
    }