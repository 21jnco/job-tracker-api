from pydantic import BaseModel, Field

from datetime import datetime
from decimal import Decimal

from enum import Enum


class JobApplicationStatus(str, Enum):
    APPLIED = "applied"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    OFFER = "offer"
    ACCEPTED = "accepted"

class JobApplicationStatusUpdate(BaseModel):
    status: JobApplicationStatus

class JobApplicationCreate(BaseModel):
    company: str
    position: str = Field(min_length=2, max_length=255)
    salary: Decimal = Field(gt=0)
    link: str | None = None


class JobApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=2, max_length=255)
    position: str | None = Field(default=None, min_length=2, max_length=255)
    salary: Decimal | None = Field(default=None, gt=0)
    link: str | None = Field(default=None, max_length=255)

class JobApplicationResponse(BaseModel):
    id: int
    user_id: int
    company: str
    position: str
    status: JobApplicationStatus
    salary: Decimal
    link: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }