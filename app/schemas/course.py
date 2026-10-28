from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CourseStatus = Literal["active", "inactive"]

CourseType = Literal[
    "short_term",
    "long_term",
]


class CourseCreate(BaseModel):

    course_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
    )

    course_type: CourseType

    course_fees: float = Field(
        ...,
        gt=0,
    )

    discount_rate: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    duration: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    status: CourseStatus = "active"

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class CourseUpdate(BaseModel):

    course_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        min_length=10,
        max_length=500,
    )

    course_type: CourseType | None = None

    course_fees: float | None = Field(
        default=None,
        gt=0,
    )

    discount_rate: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    duration: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    status: CourseStatus | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


class CourseResponse(BaseModel):

    id: str
    course_name: str
    description: str
    course_type: CourseType
    course_fees: float
    discount_rate: float
    final_fee: float
    duration: str
    status: CourseStatus
    created_at: datetime
    updated_at: datetime