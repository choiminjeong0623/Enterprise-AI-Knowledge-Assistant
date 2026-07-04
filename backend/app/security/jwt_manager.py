from datetime import datetime
from datetime import timedelta

from jose import jwt

from app.core.config import settings


class JWTManager:

    def create_access_token(
        self,
        username: str
    ):

        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {

            "sub": username,

            "exp": expire

        }

        return jwt.encode(

            payload,

            settings.SECRET_KEY,

            algorithm=settings.ALGORITHM

        )

    def verify_token(
        self,
        token: str
    ):

        payload = jwt.decode(

            token,

            settings.SECRET_KEY,

            algorithms=[settings.ALGORITHM]

        )

        return payload