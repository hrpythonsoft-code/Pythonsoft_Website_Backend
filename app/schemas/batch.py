from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


BatchMode = Literal[
    "offline",
    "online",
    "hybrid",
]


BatchStatus = Literal[
    "upcoming",
    "ongoing",
    "completed",
    "cancelled",
]


# ---------------------------------------------------------
# SHARED VALIDATORS
# ---------------------------------------------------------

def _validate_date(value: str | None) -> str | None:
    if value is None:
        return value

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("start_date must be in YYYY-MM-DD format")

    return value


def _normalize_time(value: str | None) -> str | None:
    """
    Accepts "HH:MM" (sent by <input type="time">) or "HH:MM:SS"
    and always returns "HH:MM:SS", so the database stays consistent.
    """
    if value is None:
        return value

    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(value, fmt).strftime("%H:%M:%S")
        except ValueError:
            continue

    raise ValueError("Time must be in HH:MM or HH:MM:SS format")


# ---------------------------------------------------------
# CREATE
# ---------------------------------------------------------

class BatchCreate(BaseModel):

    course_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    batch_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    start_date: str = Field(
        ...,
        min_length=10,
        max_length=10,
    )

    start_time: str = Field(
        ...,
        min_length=5,
        max_length=8,
    )

    end_time: str = Field(
        ...,
        min_length=5,
        max_length=8,
    )

    mode: BatchMode

    status: BatchStatus = "upcoming"

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, value):
        return _validate_date(value)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time(cls, value):
        return _normalize_time(value)

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# ---------------------------------------------------------
# UPDATE
# ---------------------------------------------------------

class BatchUpdate(BaseModel):

    course_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    batch_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    start_date: str | None = Field(
        default=None,
        min_length=10,
        max_length=10,
    )

    start_time: str | None = Field(
        default=None,
        min_length=5,
        max_length=8,
    )

    end_time: str | None = Field(
        default=None,
        min_length=5,
        max_length=8,
    )

    mode: BatchMode | None = None

    status: BatchStatus | None = None

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, value):
        return _validate_date(value)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time(cls, value):
        return _normalize_time(value)

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# ---------------------------------------------------------
# RESPONSE
# ---------------------------------------------------------

class BatchResponse(BaseModel):

    id: str

    course_name: str

    batch_name: str

    start_date: str

    start_time: str

    end_time: str

    mode: BatchMode

    status: BatchStatus

    created_at: datetime

    updated_at: datetime