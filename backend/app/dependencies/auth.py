from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories.user_repository import UserRepository
from app.security.password import PasswordManager
from app.security.jwt_manager import JWTManager
from app.services.auth_service import AuthService


def get_auth_service(

    db: Session = Depends(get_db)

):

    repository = UserRepository(db)

    password_manager = PasswordManager()

    jwt_manager = JWTManager()

    return AuthService(

        repository,

        password_manager,

        jwt_manager

    )