from datetime import datetime, timezone

from bson import ObjectId
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.core.dependencies import get_current_admin
from app.database.mongodb import courses_collection
from app.models.course import course_document
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)


router = APIRouter(
    tags=["Courses"],
)


# =========================================================
# ADMIN - GET ALL COURSES
# =========================================================

@router.get(
    "/api/admin/showcourses",
    response_model=list[CourseResponse],
)
async def get_admin_courses(
    current_admin: dict = Depends(get_current_admin),
):
    """
    Get all courses for the admin dashboard.

    Authentication required.
    Admin can see both active and inactive courses.
    """

    courses = []

    cursor = courses_collection.find({})

    async for course in cursor:

        courses.append(
            CourseResponse(
                id=str(course["_id"]),
                course_name=course["course_name"],
                description=course["description"],
                course_type=course["course_type"],
                course_fees=course["course_fees"],
                discount_rate=course["discount_rate"],
                final_fee=course["final_fee"],
                duration=course["duration"],
                status=course["status"],
                created_at=course["created_at"],
                updated_at=course["updated_at"],
            )
        )

    return courses


# =========================================================
# ADMIN - CREATE COURSE
# =========================================================

@router.post(
    "/api/admin/createcourses",
    status_code=status.HTTP_201_CREATED,
)
async def create_course(
    data: CourseCreate,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Create a new course.

    Authentication required.
    """

    # -----------------------------------------------------
    # Check duplicate course name
    # -----------------------------------------------------

    existing_course = await courses_collection.find_one(
        {
            "course_name": data.course_name,
        }
    )

    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course with this name already exists",
        )

    # -----------------------------------------------------
    # Create course document
    # -----------------------------------------------------

    course = course_document(
        course_name=data.course_name,
        description=data.description,
        course_type=data.course_type,
        course_fees=data.course_fees,
        discount_rate=data.discount_rate,
        duration=data.duration,
        status=data.status,
    )

    # -----------------------------------------------------
    # Insert course
    # -----------------------------------------------------

    result = await courses_collection.insert_one(course)

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "message": "Course created successfully",
        "course": {
            "id": str(result.inserted_id),
            "course_name": course["course_name"],
            "description": course["description"],
            "course_type": course["course_type"],
            "course_fees": course["course_fees"],
            "discount_rate": course["discount_rate"],
            "final_fee": course["final_fee"],
            "duration": course["duration"],
            "status": course["status"],
        },
    }


# =========================================================
# ADMIN - UPDATE COURSE
# =========================================================

@router.put(
    "/api/admin/updatecourses/{course_id}",
    response_model=CourseResponse,
)
async def update_course(
    course_id: str,
    data: CourseUpdate,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Update an existing course.

    Authentication required.
    """

    # -----------------------------------------------------
    # Validate ObjectId
    # -----------------------------------------------------

    if not ObjectId.is_valid(course_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID",
        )

    course_object_id = ObjectId(course_id)

    # -----------------------------------------------------
    # Find existing course
    # -----------------------------------------------------

    existing_course = await courses_collection.find_one(
        {
            "_id": course_object_id,
        }
    )

    if not existing_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # -----------------------------------------------------
    # Check duplicate course name
    # -----------------------------------------------------

    if data.course_name is not None:

        existing_name = await courses_collection.find_one(
            {
                "course_name": data.course_name,
                "_id": {
                    "$ne": course_object_id,
                },
            }
        )

        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another course already uses this name",
            )

    # -----------------------------------------------------
    # Prepare update data
    # -----------------------------------------------------

    update_data = {}

    if data.course_name is not None:
        update_data["course_name"] = data.course_name

    if data.description is not None:
        update_data["description"] = data.description

    if data.course_type is not None:
        update_data["course_type"] = data.course_type

    if data.course_fees is not None:
        update_data["course_fees"] = data.course_fees

    if data.discount_rate is not None:
        update_data["discount_rate"] = data.discount_rate

    if data.duration is not None:
        update_data["duration"] = data.duration

    if data.status is not None:
        update_data["status"] = data.status

    # -----------------------------------------------------
    # Calculate updated fee
    # -----------------------------------------------------

    updated_course_fees = (
        data.course_fees
        if data.course_fees is not None
        else existing_course["course_fees"]
    )

    updated_discount_rate = (
        data.discount_rate
        if data.discount_rate is not None
        else existing_course["discount_rate"]
    )

    final_fee = updated_course_fees - (
        updated_course_fees
        * updated_discount_rate
        / 100
    )

    update_data["final_fee"] = round(
        final_fee,
        2,
    )

    # -----------------------------------------------------
    # Update timestamp
    # -----------------------------------------------------

    update_data["updated_at"] = datetime.now(
        timezone.utc
    )

    # -----------------------------------------------------
    # Update database
    # -----------------------------------------------------

    await courses_collection.update_one(
        {
            "_id": course_object_id,
        },
        {
            "$set": update_data,
        },
    )

    # -----------------------------------------------------
    # Get updated course
    # -----------------------------------------------------

    updated_course = await courses_collection.find_one(
        {
            "_id": course_object_id,
        }
    )

    # -----------------------------------------------------
    # Return updated course
    # -----------------------------------------------------

    return CourseResponse(
        id=str(updated_course["_id"]),
        course_name=updated_course["course_name"],
        description=updated_course["description"],
        course_type=updated_course["course_type"],
        course_fees=updated_course["course_fees"],
        discount_rate=updated_course["discount_rate"],
        final_fee=updated_course["final_fee"],
        duration=updated_course["duration"],
        status=updated_course["status"],
        created_at=updated_course["created_at"],
        updated_at=updated_course["updated_at"],
    )


# =========================================================
# ADMIN - DELETE COURSE
# =========================================================

@router.delete(
    "/api/admin/deletecourses/{course_id}",
)
async def delete_course(
    course_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    """
    Delete an existing course.

    Authentication required.
    """

    # -----------------------------------------------------
    # Validate ObjectId
    # -----------------------------------------------------

    if not ObjectId.is_valid(course_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid course ID",
        )

    course_object_id = ObjectId(course_id)

    # -----------------------------------------------------
    # Check course exists
    # -----------------------------------------------------

    existing_course = await courses_collection.find_one(
        {
            "_id": course_object_id,
        }
    )

    if not existing_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # -----------------------------------------------------
    # Delete course
    # -----------------------------------------------------

    await courses_collection.delete_one(
        {
            "_id": course_object_id,
        }
    )

    return {
        "message": "Course deleted successfully",
        "course_id": course_id,
    }


# =========================================================
# PUBLIC - GET ACTIVE COURSES
# =========================================================

@router.get(
    "/api/courses",
    response_model=list[CourseResponse],
)
async def get_public_courses():
    """
    Get active courses for the public website.

    Authentication is NOT required.
    """

    courses = []

    cursor = courses_collection.find(
        {
            "status": "active",
        }
    )

    async for course in cursor:

        courses.append(
            CourseResponse(
                id=str(course["_id"]),
                course_name=course["course_name"],
                description=course["description"],
                course_type=course["course_type"],
                course_fees=course["course_fees"],
                discount_rate=course["discount_rate"],
                final_fee=course["final_fee"],
                duration=course["duration"],
                status=course["status"],
                created_at=course["created_at"],
                updated_at=course["updated_at"],
            )
        )

    return courses