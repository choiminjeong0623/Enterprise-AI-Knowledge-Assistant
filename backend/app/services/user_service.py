from app.models.user import User
from app.exceptions.custom_exception import AuthenticationException
from app.exceptions.custom_exception import DuplicateUserException


class UserService:

    def __init__(

        self,

        repository,

        password_manager

    ):

        self.repository = repository

        self.password_manager = password_manager

    def create_user(

        self,

        username,

        password

    ):

        exists = self.repository.find_by_username(
            username
        )

        if exists:

            raise DuplicateUserException()

        hashed = self.password_manager.hash(
            password
        )

        user = User(

            username=username,

            password=hashed

        )

        return self.repository.save(user)