from typing import Annotated

from pydantic import BaseModel, StringConstraints

from datetime import datetime


NoteContent = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=1000
    )
]


class NoteCreate(BaseModel):
    content: NoteContent


class NoteUpdate(BaseModel):
    content: NoteContent


class NoteResponse(BaseModel):
    id: int
    job_application_id: int
    content: str | None
    created_at: datetime

    model_config = {
        'from_attributes': True
    }