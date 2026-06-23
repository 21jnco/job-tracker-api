from fastapi import APIRouter, status, Depends

from app.models.user import User
from app.services.job_application_service import JobApplicationService
from app.utils.pagination import PaginationParams, get_pagination_params
from app.schemas.job_application import (
    JobApplicationResponse,
    JobApplicationCreate,
    JobApplicationStatusUpdate,
    JobApplicationUpdate)

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/job-applications",
    tags=["Job Application"]
)


@router.post("/", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = JobApplicationService(db, current_user)
    
    return service.create_job_application(data)


@router.get("/{job_application_id}", response_model=JobApplicationResponse)
def get_by_id(
    job_application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = JobApplicationService(db, current_user)

    return service.get_job_application_by_id(job_application_id)


@router.get("/", response_model=list[JobApplicationResponse])
def get_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    pagination_params: PaginationParams = Depends(get_pagination_params)
):
    service = JobApplicationService(db, current_user)

    return service.get_all_job_applications(pagination_params)


@router.patch("/{job_application_id}", response_model=JobApplicationResponse)
def update(
    data: JobApplicationUpdate,
    job_application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = JobApplicationService(db, current_user)

    return service.update_job_application(data, job_application_id)


@router.patch("/{job_application_id}/status", response_model=JobApplicationResponse)
def update_status(
    data: JobApplicationStatusUpdate,
    job_application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = JobApplicationService(db, current_user)

    return service.update_job_application_status(job_application_id, data)


@router.delete("/{job_application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    job_application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = JobApplicationService(db, current_user)
    service.delete_job_application_by_id(job_application_id)
    

@router.patch("/{job_application_id}/recovery", response_model=JobApplicationResponse)
def recovery(
    job_application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = JobApplicationService(db, current_user)

    return service.recovery_job_application_by_id(job_application_id)
