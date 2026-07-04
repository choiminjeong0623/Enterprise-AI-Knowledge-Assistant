from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories.user_repository import UserRepository
from app.security.password import PasswordManager
from app.services.user_service import UserService


def get_user_service(
    db: Session = Depends(get_db)
):

    repository = UserRepository(db)

    password_manager = PasswordManager()

    return UserService(
        repository,
        password_manager
    )