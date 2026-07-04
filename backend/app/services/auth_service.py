from app.exceptions.custom_exception import AuthenticationException


class AuthService:

    def __init__(
        self,
        repository,
        password_manager,
        jwt_manager
    ):

        self.repository = repository
        self.password_manager = password_manager
        self.jwt_manager = jwt_manager

    def login(
        self,
        username,
        password
    ):

        user = self.repository.find_by_username(
            username
        )

        if user is None:

            raise AuthenticationException()

        valid = self.password_manager.verify(

            password,

            user.password

        )

        if not valid:

            raise AuthenticationException()

        token = self.jwt_manager.create_access_token(

            user.username

        )

        return token