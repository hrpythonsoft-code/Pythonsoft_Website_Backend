from datetime import datetime, timezone

from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.core.dependencies import get_current_admin
from app.core.security import hash_password
from app.database.mongodb import admins_collection
from app.models.admin import admin_document
from app.schemas.admin import (
    AdminCreate,
    AdminResponse,
    AdminUpdate,
)


router = APIRouter(
    prefix="/api/admin",
    tags=["Admin Management"],
)


# =========================================================
# 1. View All Admins
# =========================================================

@router.get(
    "/admins",
    response_model=list[AdminResponse],
)
async def get_all_admins(
    current_admin: dict = Depends(get_current_admin),
):
    """
    Get all admin accounts.

    Only an authenticated admin can access this route.
    """

    admins = []

    cursor = admins_collection.find({})

    async for admin in cursor:

        admins.append(
            AdminResponse(
                id=str(admin["_id"]),
                name=admin["name"],
                email=admin["email"],
                role=admin["role"],
                is_active=admin["is_active"],
                created_at=admin["created_at"],
                updated_at=admin["updated_at"],
            )
        )

    return admins


# =========================================================
# 2. Add new Admin
# =========================================================

@router.post("/register-admin")
async def register_admin(
    data: AdminCreate,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Create a new admin account.
    Only an authenticated admin can create another admin.
    """

    # Check if email already exists
    existing_admin = await admins_collection.find_one(
        {
            "email": data.email.lower(),
        }
    )

    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin with this email already exists",
        )

    # Hash password
    password_hash = hash_password(data.password)

    # Create admin document
    admin = admin_document(
        name=data.name,
        email=data.email,
        password_hash=password_hash,
        is_active=True,
    )

    # Save admin
    result = await admins_collection.insert_one(admin)

    return {
        "message": "Admin created successfully",
        "admin": {
            "id": str(result.inserted_id),
            "name": admin["name"],
            "email": admin["email"],
            "role": admin["role"],
            "is_active": admin["is_active"],
        },
    }

# =========================================================
# 3. Update Admin
# =========================================================

@router.put(
    "/updateadmins/{admin_id}",
    response_model=AdminResponse,
)
async def update_admin(
    admin_id: str,
    data: AdminUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Update an existing admin.
    """

    # ---------------------------------------------
    # Validate ObjectId
    # ---------------------------------------------

    if not ObjectId.is_valid(admin_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid admin ID",
        )

    admin_object_id = ObjectId(admin_id)

    # ---------------------------------------------
    # Find admin
    # ---------------------------------------------

    existing_admin = await admins_collection.find_one(
        {
            "_id": admin_object_id,
            "role": "admin",
        }
    )

    if not existing_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found",
        )

    # ---------------------------------------------
    # Check duplicate email
    # ---------------------------------------------

    if data.email is not None:

        existing_email = await admins_collection.find_one(
            {
                "email": data.email.lower(),
                "_id": {
                    "$ne": admin_object_id
                },
            }
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another admin already uses this email",
            )

    # ---------------------------------------------
    # Build update data
    # ---------------------------------------------

    update_data = {}

    if data.name is not None:
        update_data["name"] = data.name

    if data.email is not None:
        update_data["email"] = data.email.lower()

    if data.password is not None:
        update_data["password_hash"] = hash_password(
            data.password
        )

    if data.is_active is not None:
        update_data["is_active"] = data.is_active

    # ---------------------------------------------
    # Updated timestamp
    # ---------------------------------------------

    update_data["updated_at"] = datetime.now(
        timezone.utc
    )

    # ---------------------------------------------
    # Update MongoDB
    # ---------------------------------------------

    await admins_collection.update_one(
        {
            "_id": admin_object_id,
        },
        {
            "$set": update_data,
        },
    )

    # ---------------------------------------------
    # Get updated admin
    # ---------------------------------------------

    updated_admin = await admins_collection.find_one(
        {
            "_id": admin_object_id,
        }
    )

    return AdminResponse(
        id=str(updated_admin["_id"]),
        name=updated_admin["name"],
        email=updated_admin["email"],
        role=updated_admin["role"],
        is_active=updated_admin["is_active"],
        created_at=updated_admin["created_at"],
        updated_at=updated_admin["updated_at"],
    )


# =========================================================
# 4. Delete Admin
# =========================================================

@router.delete(
    "/deleteadmins/{admin_id}",
)
async def delete_admin(
    admin_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Delete an admin account.

    An admin cannot delete their own currently
    logged-in account.
    """

    # ---------------------------------------------
    # Validate ObjectId
    # ---------------------------------------------

    if not ObjectId.is_valid(admin_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid admin ID",
        )

    admin_object_id = ObjectId(admin_id)

    # ---------------------------------------------
    # Prevent self deletion
    # ---------------------------------------------

    if admin_object_id == current_admin["_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own currently logged-in account",
        )

    # ---------------------------------------------
    # Check admin exists
    # ---------------------------------------------

    existing_admin = await admins_collection.find_one(
        {
            "_id": admin_object_id,
            "role": "admin",
        }
    )

    if not existing_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found",
        )

    # ---------------------------------------------
    # Delete admin
    # ---------------------------------------------

    await admins_collection.delete_one(
        {
            "_id": admin_object_id,
        }
    )

    return {
        "message": "Admin deleted successfully",
        "admin_id": admin_id,
    }