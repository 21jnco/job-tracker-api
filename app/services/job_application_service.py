from sqlalchemy import select, Select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException, status

from app.utils.pagination import apply_pagination, PaginationParams

from datetime import datetime, timezone

from app.core.error_messages import (
    JOB_APPLICATION_NO_DATA_PROVIDED,
    JOB_APPLICATION_NOT_FOUND,
    INVALID_JOB_APPLICATION_DATA,
    FAILED_SAVE
)

from app.models.job_application import JobApplication
from app.models.note import Note
from app.models.user import User
from app.schemas.job_application import(
    JobApplicationCreate,
    JobApplicationStatusUpdate,
    JobApplicationUpdate
)


class JobApplicationService():
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
        
    
    def create_job_application(self, data: JobApplicationCreate) -> JobApplication:
        job_application = self._create_orm_object(data)

        return self._save_job_application(job_application)
    
    
    def update_job_application(self, data: JobApplicationUpdate, job_application_id: int) -> JobApplication:
        job_application = self._get_job_application_by_id(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        received_data = self._validate_update_data(data)

        self._ensure_received_data_is_exists(received_data)

        updated_job_application = self._update_job_application_data(received_data, job_application)

        return self._save_updated_job_application(updated_job_application)
    

    def get_job_application_by_id(self, job_application_id: int) -> JobApplication:
        job_application = self._get_job_application_by_id(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        return job_application
    

    def get_all_job_applications(self, pagination_params: PaginationParams) -> list[JobApplication]:
        query = self._build_current_user_job_applications_query()

        query = self._add_pagination_params(query, pagination_params)

        job_applications = self._scalars_all_job_applications(query)

        return job_applications
    

    def update_job_application_status(
            self,
            job_application_id: int,
            status_data: JobApplicationStatusUpdate
        ) -> JobApplication:
        job_application = self._get_job_application_by_id(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        update_job_application = self._add_updated_status(job_application, status_data)

        return self._save_updated_job_application(update_job_application)


    def delete_job_application_by_id(self, job_application_id: int) -> None:
        job_application = self._get_job_application_by_id(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        notes = self._get_all_notes(job_application.id)

        self._delete_job_application(job_application, notes)

    
    def recovery_job_application_by_id(self, job_application_id: int) -> JobApplication:
        job_application = self._get_deleted_job_application(job_application_id)

        self._ensure_job_application_is_exists(job_application)

        return self._switch_status(job_application)


    def _create_orm_object(self, data: JobApplicationCreate) -> JobApplication:
        job_application = JobApplication(
            user_id=self.current_user.id,
            position=data.position,
            company=data.company,
            salary=data.salary,
            link=data.link
        )

        return job_application


    def _save_job_application(self, job_application: JobApplication) -> JobApplication:
        try:
            self.db.add(job_application)
            self.db.commit()
            self.db.refresh(job_application)

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID_JOB_APPLICATION_DATA
            )
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=FAILED_SAVE
            )

        return job_application
    

    def _get_job_application_by_id(self, job_application_id: int) -> JobApplication | None:
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
        

    def _validate_update_data(self, data: JobApplicationUpdate) -> dict:
        received_data = data.model_dump(exclude_unset=True)
        
        return received_data
    

    def _ensure_received_data_is_exists(self, received_data: dict) -> None:
        if not received_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=JOB_APPLICATION_NO_DATA_PROVIDED
            )
    

    def _update_job_application_data(
            self,
            received_data: dict,
            job_application: JobApplication
    ) -> JobApplication:
        for field, value in received_data.items():
            setattr(job_application, field, value)

        return job_application
    

    def _save_updated_job_application(self, job_application: JobApplication) -> JobApplication:
        try:
            self.db.commit()
            self.db.refresh(job_application)

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID_JOB_APPLICATION_DATA
            )
        
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=FAILED_SAVE
            )

        return job_application


    def _build_current_user_job_applications_query(self) -> Select:
        query = (
            select(JobApplication)
            .where(JobApplication.user_id == self.current_user.id, JobApplication.deleted_at.is_(None))
            .order_by(JobApplication.id.desc())
        )

        return query


    def _add_pagination_params(
            self,
            query: Select,
            pagination_params: PaginationParams
        ) -> Select:
        query = apply_pagination(query, pagination_params)

        return query
    

    def _scalars_all_job_applications(self, query: Select) -> list[JobApplication]:
        job_applications = self.db.execute(query).scalars().all()

        return job_applications


    def _add_updated_status(
            self,
            job_application: JobApplication,
            status_data: JobApplicationStatusUpdate
        ) -> JobApplication:
        job_application.status=status_data.status.value

        return job_application
    

    def _get_all_notes(self, job_application_id: int) -> list[Note]:
        query = select(Note).where(Note.job_application_id == job_application_id, Note.deleted_at.is_(None))
        notes = self.db.execute(query).scalars().all()

        return notes
    

    def _delete_job_application(self, job_application: JobApplication, notes: list[Note]) -> None:
        now = datetime.now(timezone.utc)

        job_application.deleted_at = now

        for note in notes:
            note.deleted_at = now
            note.delete_with_parent = True

        self.db.commit()


    def _get_deleted_job_application(self, job_application_id: int) -> JobApplication | None:
        query = (
            select(JobApplication)
            .where(
                JobApplication.id == job_application_id,
                JobApplication.user_id == self.current_user.id,
                JobApplication.deleted_at.is_not(None)
            )
            
        )
        job_application = self.db.execute(query).scalar_one_or_none()

        return job_application


    def _switch_status(self, job_application: JobApplication) -> JobApplication:
        job_application.deleted_at = None

        query = select(Note).where(Note.job_application_id == job_application.id, Note.delete_with_parent.is_(True))
        notes = self.db.execute(query).scalars().all()
        

        for note in notes:
            note.deleted_at = None
            note.delete_with_parent = False

        self.db.commit()
        self.db.refresh(job_application)

        return job_application