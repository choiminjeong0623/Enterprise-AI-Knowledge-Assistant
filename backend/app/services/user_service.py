from app.models.user import User


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

        hashed = self.password_manager.hash(
            password
        )

        user = User(

            username=username,

            password=hashed

        )

        return self.repository.save(user)