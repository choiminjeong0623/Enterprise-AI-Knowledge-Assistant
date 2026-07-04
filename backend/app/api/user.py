from fastapi import APIRouter
from fastapi import Depends

from app.schemas.user import (
    UserCreate,
    UserResponse
)

from app.dependencies.user import (
    get_user_service
)

from app.services.user_service import (
    UserService
)

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