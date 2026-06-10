from sqlalchemy import select, Select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.utils.pagination import apply_pagination, PaginationParams

from app.models.job_application import JobApplication
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

        self._delete_job_application(job_application)

    # CREATE JOB APPLICATION PRIVATE FUNC

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
        self.db.add(job_application)
        self.db.commit()
        self.db.refresh(job_application)

        return job_application
    

    # JOB APPLICATION UPDATE PRIVATE FUNC

    def _get_job_application_by_id(self, job_application_id: int) -> JobApplication | None:
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
                detail="Job application is not exists"
            )
        

    def _validate_update_data(self, data: JobApplicationUpdate) -> dict:
        received_data = data.model_dump(exclude_unset=True)
        
        return received_data
    

    def _ensure_received_data_is_exists(self, received_data: dict) -> None:
        if not received_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data."
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
        self.db.commit()
        self.db.refresh(job_application)

        return job_application


    # GET ALL JOB APPLICATION PRIVATE FUNC

    def _build_current_user_job_applications_query(self) -> Select:
        query = (
            select(JobApplication)
            .where(JobApplication.user_id == self.current_user.id)
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


    # UPDATE JOB APPLICATION STATUS PRICATE FUNC

    def _add_updated_status(
            self,
            job_application: JobApplication,
            status_data: JobApplicationStatusUpdate
        ) -> JobApplication:
        job_application.status=status_data.status.value

        return job_application
    
    
    # DELETE JOB APPLICATION PRIVATE FUNC

    def _delete_job_application(self, job_application: JobApplication) -> None:
        self.db.delete(job_application)
        self.db.commit()
