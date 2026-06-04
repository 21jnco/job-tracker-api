from pydantic import BaseModel

from datetime import datetime


class NoteCreate(BaseModel):
    content: str | None = None


class NoteUpdate(BaseModel):
    content: str | None = None


class NoteResponse(BaseModel):
    id: int
    job_application_id: int
    content: str | None
    created_at: datetime

    model_config = {
        'from_attributes': True
    }