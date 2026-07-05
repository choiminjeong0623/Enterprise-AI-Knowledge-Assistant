from fastapi import APIRouter
from fastapi import Depends

from app.schemas.user import (
    UserCreate,
    UserResponse
)

from app.dependencies.user import (
    get_user_service
)

from app.dependencies.auth import (
    get_current_user
)

from app.services.user_service import (
    UserService
)
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/signup",
    response_model=UserResponse
)

def signup(

    request: UserCreate,

    service: UserService = Depends(
        get_user_service
    )

):

    user = service.create_user(

        request.username,

        request.password

    )

    return user


@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user : User = Depends(get_current_user)
):
    return current_user