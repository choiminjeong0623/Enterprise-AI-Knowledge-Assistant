from fastapi.security import OAuth2PasswordBearer

## 토큰 생성
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)