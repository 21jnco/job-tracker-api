from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserEmailUpdate, UserPasswordUpdate

from app.core.security import verify_password, hash_password

from app.core.error_messages import (
    USER_EMAIL_ALREADY_EXISTS,
    PASSWORD_INCORRECT
)


class UserService():
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user

    
    def get_my_profile(self) -> User:
        user = self.current_user

        return user


    def update_my_email(self, update_data: UserEmailUpdate) -> User:
        user = self.current_user

        user_with_same_email = self._search_for_user_with_same_email(update_data.email)

        self._user_with_same_email_exists(user_with_same_email)

        updated_user = self._add_new_email(user, update_data.email)

        return self._commit_updated_user(updated_user)


    def update_my_password(self, password_data: UserPasswordUpdate) -> User:
        user = self.current_user

        result = self._check_current_password(password_data.current_password, user.hashed_password)

        self._ensure_current_password_is_correct(result)

        hashed_password = self._hashed_new_password(password_data.password)

        updated_user = self._add_new_password(user, hashed_password)

        return self._commit_updated_user(updated_user)
    

    def delete_my_own_account(self) -> None:
        user = self.current_user

        self._delete_user_account(user)


    def _search_for_user_with_same_email(self, update_email: str) -> User | None:
        query = select(User).where(User.email == update_email)
        user = self.db.execute(query).scalar_one_or_none()
    
        return user
    

    def _user_with_same_email_exists(self, user_with_same_email: User | None) -> None:
        if user_with_same_email is not None and user_with_same_email.id != self.current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=USER_EMAIL_ALREADY_EXISTS
            )
        

    def _add_new_email(self, user: User, new_email: str) -> User:
        user.email = new_email

        return user


    def _commit_updated_user(self, updated_user: User) -> User:
        self.db.commit()
        self.db.refresh(updated_user)

        return updated_user
    

    def _delete_user_account(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()


    def _check_current_password(self, current_password: str, hashed_password: str) -> bool:
        result = verify_password(current_password, hashed_password)

        return result
    
    
    def _ensure_current_password_is_correct(self, result: bool) -> None:
        if result is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=PASSWORD_INCORRECT
            )
        

    def _hashed_new_password(self, new_password: str) -> str:
        hashed_password = hash_password(new_password)

        return hashed_password
    

    def _add_new_password(self, user: User, new_hashed_password: str) -> User:
        user.hashed_password = new_hashed_password

        return user