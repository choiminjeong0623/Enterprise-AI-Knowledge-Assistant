from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    def __init__(self, db: Session):

        self.db = db

    def save(self, user: User):

        self.db.add(user)

        self.db.commit()

        self.db.refresh(user)

        return user

    def find_by_username(self, username: str):

        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )