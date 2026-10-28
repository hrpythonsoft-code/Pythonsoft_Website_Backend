from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from app.core.config import settings
from app.core.dependencies import get_current_admin
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.mongodb import admins_collection
from app.models.admin import admin_document
from app.schemas.admin import (
    AdminCreate,
    AdminLogin,
    AdminResponse,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)



# -------------------------
# Admin Login
# -------------------------

@router.post("/login")
async def admin_login(
    data: AdminLogin,
    response: Response,
):
    admin = await admins_collection.find_one(
        {
            "email": data.email.lower(),
        }
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    password_valid = verify_password(
        data.password,
        admin["password_hash"],
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not admin.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    token = create_access_token(
        admin_id=str(admin["_id"]),
        role=admin["role"],
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "message": "Login successful",
        "admin": AdminResponse(
            id=str(admin["_id"]),
            name=admin["name"],
            email=admin["email"],
            role=admin["role"],
            is_active=admin["is_active"],
            created_at=admin["created_at"],
            updated_at=admin["updated_at"],
        ),
    }


# -------------------------
# Admin Logout
# -------------------------

@router.post("/logout")
async def admin_logout(
    response: Response,
):
    response.delete_cookie(
        key="access_token",
    )

    return {
        "message": "Logout successful"
    }


# -------------------------
# Current Admin
# -------------------------

@router.get(
    "/me",
    response_model=AdminResponse,
)
async def get_me(
    current_admin: dict = Depends(get_current_admin),
):
    return AdminResponse(
        id=str(current_admin["_id"]),
        name=current_admin["name"],
        email=current_admin["email"],
        role=current_admin["role"],
        is_active=current_admin["is_active"],
        created_at=current_admin["created_at"],
        updated_at=current_admin["updated_at"],
    )