from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.sqlalchemy_database_uri,
    future=True,
    echo=settings.app_debug,  # 디버그 모드에서 SQL 쿼리 출력
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """FastAPI 의존성: 데이터베이스 세션 제공"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

