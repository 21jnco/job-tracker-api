from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm


from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import TokenResponse, LoginRequest
from app.core.database import get_db

from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    auth_service = AuthService(db)

    return auth_service.register(data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login_user(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    token = auth_service.login(data.username, data.password)

    return TokenResponse(access_token=token)


@router.patch("/recovery", response_model=UserResponse)
def recovery(data: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)

    return service.recovery_user(data.email, data.password)