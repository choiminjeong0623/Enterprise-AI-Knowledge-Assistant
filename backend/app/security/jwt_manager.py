from datetime import datetime
from datetime import timedelta

from jose import jwt

from app.clients.config import settings


class JWTManager:

    def create_access_token(
        self,
        user: str
    ):

        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {

            "sub": user.username,

            "user_id": user.id,

            "role": user.role,

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

        try:
            payload = jwt.decode(

                token,

                settings.SECRET_KEY,

                algorithms=[settings.ALGORITHM]
            )

            return payload
        

        except JWTError:

            return None
