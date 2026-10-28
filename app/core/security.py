from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


# JWT configuration
JWT_ALGORITHM = settings.JWT_ALGORITHM


# -------------------------
# Password Hashing
# -------------------------

def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure bcrypt hash.
    """

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(
        password_bytes,
        salt,
    )

    return hashed_password.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against the stored bcrypt hash.
    """

    plain_password_bytes = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(
        plain_password_bytes,
        hashed_password_bytes,
    )


# -------------------------
# JWT
# -------------------------

def create_access_token(
    admin_id: str,
    role: str,
) -> str:
    """
    Create a JWT access token.
    """

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": admin_id,
        "role": role,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    """

    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
    )

    return payload