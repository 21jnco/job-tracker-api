from pydantic import BaseModel, EmailStr

from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserEmailUpdate(BaseModel):
    email: EmailStr


class UserPasswordUpdate(BaseModel):
    current_password: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {
        'from_attributes': True
    }