class CustomException(Exception):

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int
    ):

        self.code = code
        self.message = message
        self.status_code = status_code

        super().__init__(message)


class OpenAIException(CustomException):

    def __init__(
        self,
        message="OpenAI API 호출에 실패했습니다."
    ):

        super().__init__(
            code="OPENAI_ERROR",
            message=message,
            status_code=500
        )


class AuthenticationException(CustomException):

    def __init__(
        self,
        message="Invalid username or password."
    ):

        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            status_code=401
        )


class AuthorizationException(CustomException):

    def __init__(
        self,
        message="Access denied."
    ):

        super().__init__(
            code="AUTHORIZATION_ERROR",
            message=message,
            status_code=403
        )


class DuplicateUserException(CustomException):

    def __init__(self):

        super().__init__(
            code="DUPLICATE_USER",
            message="Username already exists.",
            status_code=409
        )


class DatabaseException(CustomException):

    def __init__(
        self,
        message="Database error."
    ):

        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            status_code=500
        )


class NotFoundException(CustomException):

    def __init__(
        self,
        message="Resource not found."
    ):

        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=404
        )