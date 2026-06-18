from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from datetime import datetime, timezone

from app.schemas.note import NoteCreate, NoteUpdate
from app.models.note import Note
from app.models.user import User
from app.models.job_application import JobApplication
from app.utils.pagination import PaginationParams, apply_pagination
from app.core.error_messages import (
    NOTE_NO_DATA_PROVIDED,
    NOTE_NOT_FOUND,
    JOB_APPLICATION_NOT_FOUND
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
    

    def get_note_by_id(self, job_application_id: int, note_id: int) -> Note:
        job_application = self._get_job_application(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        note = self._get_note(note_id, job_application.id)

        self._ensure_note_is_exists(note)

        return note


    def update_note(self, job_application_id: int, note_id: int, update_data: NoteUpdate) -> Note:
        job_application = self._get_job_application(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        note = self._get_note(note_id, job_application.id)

        self._ensure_note_is_exists(note)

        updated_note = self._apply_update_data(note, update_data)

        return self._commit_updated_note(updated_note)


    def delete_note(self, job_application_id: int, note_id: int) -> None:
        job_application = self._get_job_application(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        note = self._get_note(note_id, job_application.id)

        self._ensure_note_is_exists(note)

        self._delete_note(note)


    def recovery_note_by_id(self, job_application_id: int, note_id: int) -> Note:
        job_application = self._get_job_application(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        deleted_note = self._get_deleted_note(note_id, job_application.id)

        self._ensure_note_is_exists(deleted_note)

        return self._recovery_note(deleted_note)


    def _get_job_application(self, job_application_id: int) -> JobApplication | None:
        query = select(JobApplication).where(
            JobApplication.id == job_application_id,
            JobApplication.user_id == self.current_user.id,
            JobApplication.deleted_at.is_(None)
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
            .where(Note.job_application_id == job_application_id, Note.deleted_at.is_(None))
            .order_by(Note.id.desc())
        )

        return query


    def _apply_pagination_params(self, query: Select, pagination_params: PaginationParams) -> Select:
        query = apply_pagination(query, pagination_params)

        return query
    
    
    def _get_notes(self, query: Select) -> list[Note]:
        notes = self.db.execute(query).scalars().all()

        return notes


    def _get_note(self, note_id: int, job_application_id: int) -> Note | None:
        query = (
            select(Note)
            .where(
                Note.id == note_id,
                Note.job_application_id == job_application_id,
                Note.deleted_at.is_(None)
            )
        )
        note = self.db.execute(query).scalar_one_or_none()

        return note
    

    def _get_deleted_note(self, note_id: int, job_application_id: int) -> Note | None:
        query = (
            select(Note)
            .where(
                Note.id == note_id,
                Note.job_application_id == job_application_id,
                Note.deleted_at.is_not(None),
                Note.delete_with_parent.is_(False)
            )
        )
        deleted_note = self.db.execute(query).scalar_one_or_none()

        return deleted_note
    

    def _ensure_note_is_exists(self, note: Note | None) -> None:
        if note is None: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=NOTE_NOT_FOUND
            )
        
    
    def _apply_update_data(self, note: Note, update_data: NoteUpdate) -> Note:
        note.content = update_data.content

        return note
    

    def _commit_updated_note(self, note: Note) -> Note:
        self.db.commit()
        self.db.refresh(note)

        return note
    

    def _delete_note(self, note: Note) -> None:
        note.deleted_at = datetime.now(timezone.utc)

        self.db.commit()


    def _recovery_note(self, deleted_note: Note) -> Note:
        deleted_note.deleted_at = None

        self.db.commit()
        self.db.refresh(deleted_note)

        return deleted_note
