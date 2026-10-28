from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminCreate(BaseModel):
    
    name: str = Field(...,min_length=2,max_length=100,)
    email: EmailStr
    password: str = Field(...,min_length=8,max_length=128,)
    model_config = ConfigDict(str_strip_whitespace=True)


class AdminLogin(BaseModel):

    email: EmailStr
    password: str = Field(...,min_length=1,max_length=128,)
    model_config = ConfigDict(str_strip_whitespace=True)


class AdminUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
    )

    is_active: bool | None = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )


class AdminResponse(BaseModel):
    
    id: str
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        str_strip_whitespace=True
    )