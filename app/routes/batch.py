from datetime import datetime, timezone

from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.core.dependencies import get_current_admin
from app.database.mongodb import batches_collection
from app.models.batch import batch_document
from app.schemas.batch import (
    BatchCreate,
    BatchResponse,
    BatchUpdate,
)


router = APIRouter(
    tags=["Batches"],
)


# =========================================================
# ADMIN - GET ALL BATCHES
# =========================================================

@router.get(
    "/api/admin/showbatches",
    response_model=list[BatchResponse],
)
async def get_admin_batches(
    current_admin: dict = Depends(get_current_admin),
):
    """
    Get all batches for the admin dashboard.

    Authentication required.
    Admin can see all batches.
    """

    batches = []

    cursor = batches_collection.find({})

    async for batch in cursor:

        batches.append(
            BatchResponse(
                id=str(batch["_id"]),
                course_name=batch["course_name"],
                batch_name=batch["batch_name"],
                start_date=batch["start_date"],
                start_time=batch["start_time"],
                end_time=batch["end_time"],
                mode=batch["mode"],
                status=batch["status"],
                created_at=batch["created_at"],
                updated_at=batch["updated_at"],
            )
        )

    return batches


# =========================================================
# ADMIN - CREATE BATCH
# =========================================================

@router.post(
    "/api/admin/createbatches",
    status_code=status.HTTP_201_CREATED,
)
async def create_batch(
    data: BatchCreate,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Create a new batch.

    Authentication required.
    """

    # -----------------------------------------------------
    # Check duplicate batch name
    # -----------------------------------------------------

    existing_batch = await batches_collection.find_one(
        {
            "batch_name": data.batch_name,
        }
    )

    if existing_batch:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Batch with this name already exists",
        )

    # -----------------------------------------------------
    # Create batch document
    # -----------------------------------------------------

    batch = batch_document(
        course_name=data.course_name,
        batch_name=data.batch_name,
        start_date=data.start_date,
        start_time=data.start_time,
        end_time=data.end_time,
        mode=data.mode,
        status=data.status,
    )

    # -----------------------------------------------------
    # Insert batch
    # -----------------------------------------------------

    result = await batches_collection.insert_one(
        batch
    )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "message": "Batch created successfully",
        "batch": {
            "id": str(result.inserted_id),
            "course_name": batch["course_name"],
            "batch_name": batch["batch_name"],
            "start_date": batch["start_date"],
            "start_time": batch["start_time"],
            "end_time": batch["end_time"],
            "mode": batch["mode"],
            "status": batch["status"],
        },
    }


# =========================================================
# ADMIN - UPDATE BATCH
# =========================================================

@router.put(
    "/api/admin/updatebatches/{batch_id}",
    response_model=BatchResponse,
)
async def update_batch(
    batch_id: str,
    data: BatchUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Update an existing batch.

    Authentication required.
    """

    # -----------------------------------------------------
    # Validate ObjectId
    # -----------------------------------------------------

    if not ObjectId.is_valid(batch_id):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid batch ID",
        )

    batch_object_id = ObjectId(batch_id)

    # -----------------------------------------------------
    # Find existing batch
    # -----------------------------------------------------

    existing_batch = await batches_collection.find_one(
        {
            "_id": batch_object_id,
        }
    )

    if not existing_batch:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    # -----------------------------------------------------
    # Check duplicate batch name
    # -----------------------------------------------------

    if data.batch_name is not None:

        existing_name = await batches_collection.find_one(
            {
                "batch_name": data.batch_name,
                "_id": {
                    "$ne": batch_object_id,
                },
            }
        )

        if existing_name:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another batch already uses this name",
            )

    # -----------------------------------------------------
    # Prepare update data
    # -----------------------------------------------------

    update_data = {}

    if data.course_name is not None:

        update_data["course_name"] = data.course_name

    if data.batch_name is not None:

        update_data["batch_name"] = data.batch_name

    if data.start_date is not None:

        update_data["start_date"] = data.start_date

    if data.start_time is not None:

        update_data["start_time"] = data.start_time

    if data.end_time is not None:

        update_data["end_time"] = data.end_time

    if data.mode is not None:

        update_data["mode"] = data.mode

    if data.status is not None:

        update_data["status"] = data.status

    # -----------------------------------------------------
    # Update timestamp
    # -----------------------------------------------------

    update_data["updated_at"] = datetime.now(
        timezone.utc
    )

    # -----------------------------------------------------
    # Update database
    # -----------------------------------------------------

    await batches_collection.update_one(
        {
            "_id": batch_object_id,
        },
        {
            "$set": update_data,
        },
    )

    # -----------------------------------------------------
    # Get updated batch
    # -----------------------------------------------------

    updated_batch = await batches_collection.find_one(
        {
            "_id": batch_object_id,
        }
    )

    # -----------------------------------------------------
    # Return updated batch
    # -----------------------------------------------------

    return BatchResponse(
        id=str(updated_batch["_id"]),
        course_name=updated_batch["course_name"],
        batch_name=updated_batch["batch_name"],
        start_date=updated_batch["start_date"],
        start_time=updated_batch["start_time"],
        end_time=updated_batch["end_time"],
        mode=updated_batch["mode"],
        status=updated_batch["status"],
        created_at=updated_batch["created_at"],
        updated_at=updated_batch["updated_at"],
    )


# =========================================================
# ADMIN - DELETE BATCH
# =========================================================

@router.delete(
    "/api/admin/deletebatches/{batch_id}",
)
async def delete_batch(
    batch_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Delete an existing batch.

    Authentication required.
    """

    # -----------------------------------------------------
    # Validate ObjectId
    # -----------------------------------------------------

    if not ObjectId.is_valid(batch_id):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid batch ID",
        )

    batch_object_id = ObjectId(batch_id)

    # -----------------------------------------------------
    # Check batch exists
    # -----------------------------------------------------

    existing_batch = await batches_collection.find_one(
        {
            "_id": batch_object_id,
        }
    )

    if not existing_batch:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found",
        )

    # -----------------------------------------------------
    # Delete batch
    # -----------------------------------------------------

    await batches_collection.delete_one(
        {
            "_id": batch_object_id,
        }
    )

    return {
        "message": "Batch deleted successfully",
        "batch_id": batch_id,
    }


# =========================================================
# PUBLIC - GET ALL BATCHES
# =========================================================

@router.get(
    "/api/batches",
    response_model=list[BatchResponse],
)
async def get_public_batches():
    """
    Get batches for the public website.

    Authentication is NOT required.
    """

    batches = []

    cursor = batches_collection.find({})

    async for batch in cursor:

        batches.append(
            BatchResponse(
                id=str(batch["_id"]),
                course_name=batch["course_name"],
                batch_name=batch["batch_name"],
                start_date=batch["start_date"],
                start_time=batch["start_time"],
                end_time=batch["end_time"],
                mode=batch["mode"],
                status=batch["status"],
                created_at=batch["created_at"],
                updated_at=batch["updated_at"],
            )
        )

    return batches