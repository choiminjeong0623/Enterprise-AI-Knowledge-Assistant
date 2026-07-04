from app.exceptions.custom_exception import AuthenticationException


class AuthService:

    def __init__(

        self,

        repository,

        jwt_manager

    ):

        self.repository = repository

        self.jwt_manager = jwt_manager

    def get_current_user(
        self,
        token: str
    ):

        payload = self.jwt_manager.verify_token(
            token
        )

        if payload is None:

            raise AuthenticationException(
                "Invalid token."
            )

        username = payload.get("sub")

        if username is None:

            raise AuthenticationException(
                "Invalid token."
            )

        user = self.repository.find_by_username(
            username
        )

        if user is None:

            raise AuthenticationException(
                "User not found."
            )

        return user