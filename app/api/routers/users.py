from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session

from app.schemas.user import UserResponse, UserPasswordUpdate, UserEmailUpdate
from app.models.user import User
from app.services.user_service import UserService

from app.core.database import get_db
from app.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["User"]
)


@router.get("/me", response_model=UserResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db, current_user)

    return service.get_my_profile()


@router.patch("/me/password", response_model=UserResponse)
def update_password(
    data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db, current_user)

    return service.update_my_password(data)


@router.patch("/me/email", response_model=UserResponse)
def update_email(
    data: UserEmailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db, current_user)

    return service.update_my_email(data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db, current_user)
    service.delete_my_own_account()