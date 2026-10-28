from datetime import datetime, timezone


def course_document(
    course_name: str,
    description: str,
    course_type: str,
    course_fees: float,
    discount_rate: float,
    duration: str,
    status: str = "active",
):
    now = datetime.now(timezone.utc)

    final_fee = course_fees - (
        course_fees * discount_rate / 100
    )

    return {
        "course_name": course_name,
        "description": description,
        "course_type": course_type,
        "course_fees": course_fees,
        "discount_rate": discount_rate,
        "final_fee": round(final_fee, 2),
        "duration": duration,
        "status": status,
        "created_at": now,
        "updated_at": now,
    }