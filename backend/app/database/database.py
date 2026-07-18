from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.clients.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# SessionLocal() : DB 연결 객체를 생성한다.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# declarative_base() : 모든 Entity의 부모이다.
Base = declarative_base()
