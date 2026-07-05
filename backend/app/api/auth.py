from fastapi import APIRouter
from fastapi import Depends

from fastapi.security import OAuth2PasswordRequestForm

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



## 로그인API 사용
@router.post("/login")
def login(

    form_data: OAuth2PasswordRequestForm = Depends(),

    service: AuthService = Depends(get_auth_service)

):

    token = service.login(

        form_data.username,

        form_data.password

    )

    return {
        "access_token": token
    }

## JSON 구현
# @router.post(

#     "/login",

#     response_model=LoginResponse

# )

# def login(

#     request: LoginRequest,

#     service: AuthService = Depends(
#         get_auth_service
#     )

# ):

#     token = service.login(

#         request.username,

#         request.password

#     )

#     return LoginResponse(

#         access_token=token

#     )