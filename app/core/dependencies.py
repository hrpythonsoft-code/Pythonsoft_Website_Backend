from typing import Annotated

import jwt
from bson import ObjectId
from fastapi import Cookie, HTTPException, status
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


from app.core.security import decode_access_token
from app.database.mongodb import admins_collection


async def get_current_admin(
    access_token: Annotated[
        str | None,
        Cookie()
    ] = None,
):
    """
    Authenticate the current admin using the JWT
    stored in the HTTP-only access_token cookie.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )

    if not access_token:
        raise credentials_exception

    try:
        payload = decode_access_token(access_token)

        admin_id = payload.get("sub")
        role = payload.get("role")

        if not admin_id or not role:
            raise credentials_exception

        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        if not ObjectId.is_valid(admin_id):
            raise credentials_exception

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    admin = await admins_collection.find_one(
        {
            "_id": ObjectId(admin_id),
            "role": "admin",
        }
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin account not found",
        )

    if not admin.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    return admin