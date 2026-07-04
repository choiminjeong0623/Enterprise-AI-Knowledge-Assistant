from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.database.database import Base
from app.database.database import engine


class Conversation(Base):

    __tablename__ = "conversation"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    sentence = Column(String)
    answer = Column(String)
    corrected_sentence = Column(String)
    time = Column(String)

    Base.metadata.create_all(bind=engine)