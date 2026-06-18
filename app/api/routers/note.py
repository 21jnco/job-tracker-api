from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session

from app.schemas.note import NoteResponse, NoteCreate, NoteUpdate
from app.models.user import User
from app.services.note_service import NoteService
from app.utils.pagination import PaginationParams, get_pagination_params

from app.dependencies.auth import get_current_user
from app.core.database import get_db


router = APIRouter(
    prefix="/job_applications/{job_application_id}/notes",
    tags=["Note"]
)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: NoteCreate,
    job_application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NoteService(db, current_user)

    return service.create_note(data, job_application_id)


@router.get("/{note_id}", response_model=NoteResponse)
def get_by_id(
    job_application_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NoteService(db, current_user)

    return service.get_note_by_id(job_application_id, note_id)


@router.get("", response_model=list[NoteResponse])
def get_all(
    job_application_id: int,
    pagination_params: PaginationParams = Depends(get_pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NoteService(db, current_user)

    return service.get_all_notes(job_application_id, pagination_params)


@router.patch("/{note_id}", response_model=NoteResponse)
def update(
    job_application_id: int,
    note_id: int,
    data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NoteService(db, current_user)

    return service.update_note(job_application_id, note_id, data)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    job_application_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NoteService(db, current_user)
    service.delete_note(job_application_id, note_id)


@router.patch("/{note_id}/recovery", response_model=NoteResponse)
def recovery(
    job_application_id: int,
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = NoteService(db, current_user)

    return service.recovery_note_by_id(job_application_id, note_id)