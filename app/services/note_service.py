from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.schemas.note import NoteCreate, NoteUpdate
from app.models.note import Note
from app.models.user import User
from app.models.job_application import JobApplication
from app.utils.pagination import PaginationParams, apply_pagination
from app.core.error_messages import (
    NOTE_NO_DATA_PROVIDED,
    NOTE_NOT_FOUND,
    NO_DATA_PROVIDED,
    JOB_APPLICATION_NOT_FOUND,
    FAILED_SAVE
)


class NoteService():
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user


    def create_note(self, note_data: NoteCreate, job_application_id: int) -> Note:
        job_application = self._get_job_application(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        self._ensure_content_is_exists(note_data)

        note = self._create_orm_object(note_data, job_application.id)

        return self._save_note(note)
    

    def get_all_notes(self, job_application_id: int, pagination_params: PaginationParams) -> list[Note]:
        job_application = self._get_job_application(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        query = self._select_notes(job_application.id)

        query_with_pagination = self._apply_pagination_params(query, pagination_params)

        return self._get_notes(query_with_pagination)
    

    def get_note_by_id(self):
        pass


    def update_note(self):
        pass


    def delete_note(self):
        pass


    def _get_job_application(self, job_application_id: int) -> JobApplication | None:
        query = select(JobApplication).where(
            JobApplication.id == job_application_id,
            JobApplication.user_id == self.current_user.id
        )

        job_application = self.db.execute(query).scalar_one_or_none()

        return job_application
    

    def _ensure_job_application_is_exists(self, job_application: JobApplication | None) -> None:
        if job_application is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=JOB_APPLICATION_NOT_FOUND
            )


    def _ensure_content_is_exists(self, data: NoteCreate) -> None:
        if data.content is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=NOTE_NO_DATA_PROVIDED
            )

 
    def _create_orm_object(self, data: NoteCreate, job_application_id: int) -> Note:
        note = Note(
            job_application_id = job_application_id,
            content = data.content
        )

        return note


    def _save_note(self, note: Note) -> Note:
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        
        return note
    

    def _select_notes(self, job_application_id: int) -> Select:
        query = (
            select(Note)
            .where(Note.job_application_id == job_application_id)
            .order_by(Note.id.desc())
        )

        return query

    def _apply_pagination_params(self, query: Select, pagination_params: PaginationParams) -> Select:
        query = apply_pagination(query, pagination_params)

        return query
    
    
    def _get_notes(self, query: Select) -> list[Note]:
        notes = self.db.execute(query).scalars().all()

        return notes