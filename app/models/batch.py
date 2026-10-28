from datetime import datetime, timezone


def batch_document(
    course_name: str,
    batch_name: str,
    start_date: str,
    start_time: str,
    end_time: str,
    mode: str,
    status: str = "upcoming",
):
    now = datetime.now(timezone.utc)

    return {
        "course_name": course_name,
        "batch_name": batch_name,
        "start_date": start_date,
        "start_time": start_time,
        "end_time": end_time,
        "mode": mode,
        "status": status,
        "created_at": now,
        "updated_at": now,
    }