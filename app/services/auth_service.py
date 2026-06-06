from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate

from app.core.security import hash_password, verify_password, create_access_token

from app.models.user import User

from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    
    def register(self, user_data: UserCreate) -> User:
        query_user = self._get_user_by_email(user_data.email)

        self._ensure_email_not_taken(query_user)

        user_hash_password = hash_password(user_data.password)

        user = self._create_user(user_hash_password, user_data)

        saved_user = self._save_user(user)

        return saved_user
    
    
    def login(self, user_data: LoginRequest) -> str:
        user = self._get_user_by_email(user_data.email)    

        self._ensure_user_exists(user)

        self._ensure_password_is_correct(
            user_data.password,
            user.hashed_password
        )

        token = self._create_token(user.id)

        return token


    # --- REGISTER PRIVATE FUNC ---

    def _get_user_by_email(self, data: str) -> User | None:
        query = select(User).where(User.email == data)
        user = self.db.execute(query).scalar_one_or_none()

        return user
    

    def _ensure_email_not_taken(self, user: User | None) -> None:
        if user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exist."
            )
        

    def _create_user(self, hashed_password: str, data: UserCreate) -> User:
        user = User(
            email=data.email,
            hashed_password=hashed_password
        )

        return user
    

    def _save_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user
    

    # --- LOGIN PRIVATE FUNC ---

    def _ensure_user_exists(self, user: User | None) -> None:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        

    def _ensure_password_is_correct(self, plain_password: str, hashed_password: str) -> None:
        result = verify_password(plain_password, hashed_password)

        if result is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password."
            )
    

    def _create_token(self, user_id: int) -> str:
        token = create_access_token({"sub": str(user_id)})

        return token