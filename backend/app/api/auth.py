from fastapi import APIRouter
from fastapi import Depends

from app.schemas.auth import (
    LoginRequest,
    LoginResponse
)

from app.dependencies.auth import (
    get_auth_service
)

from app.services.auth_service import (
    AuthService
)

router = APIRouter(

    prefix="/auth",

    tags=["Authentication"]

)


@router.post(

    "/login",

    response_model=LoginResponse

)

def login(

    request: LoginRequest,

    service: AuthService = Depends(

        get_auth_service

    )

):

    token = service.login(

        request.username,

        request.password

    )

    return LoginResponse(

        access_token=token

    )