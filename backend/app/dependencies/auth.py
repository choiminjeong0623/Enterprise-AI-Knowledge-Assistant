from fastapi import Depends
from fastapi import Header
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories.user_repository import UserRepository
from app.security.jwt_manager import JWTManager
from app.services.auth_service import AuthService


def get_current_user(

    authorization: str = Header(...),

    db: Session = Depends(get_db)

):

    token = authorization.replace(
        "Bearer ",
        ""
    )

    repository = UserRepository(db)

    jwt_manager = JWTManager()

    auth_service = AuthService(

        repository,

        jwt_manager

    )

    return auth_service.get_current_user(
        token
    )