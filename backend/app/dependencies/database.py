from collections.abc import Generator
from sqlalchemy.orm import Session
from app.database.database import SessionLocal


def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:
        yield db    # DB 연결 자동으로 Close

    finally:
        db.close()