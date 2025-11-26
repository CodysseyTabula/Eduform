import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

def _create_engine():
    """
    실행 환경에 따라 알맞은 DB 엔진을 생성합니다.
    
    - TEST_DATABASE_URL 환경변수가 있으면 그 값을 우선 사용 (pytest에서 SQLite 인메모리 강제)
    - APP_ENV=test 이면 SQLite 인메모리 사용
    - 그 외에는 설정에 정의된 기본 DB(PostgreSQL) 사용
    """
    test_db_url = os.getenv("TEST_DATABASE_URL")
    app_env = os.getenv("APP_ENV", "").lower()
    
    if test_db_url:
        return create_engine(
            test_db_url,
            echo=settings.app_debug,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    
    if app_env == "test":
        return create_engine(
            "sqlite:///:memory:",
            echo=settings.app_debug,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    
    # 기본: 운영 DB (PostgreSQL)
    return create_engine(
        settings.sqlalchemy_database_uri,
        echo=settings.app_debug,  # 디버그 모드에서 SQL 쿼리 로깅
        pool_pre_ping=True,  # 연결 풀 연결 상태 체크
    )


# 데이터베이스 엔진 생성
engine = _create_engine()

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """FastAPI 의존성: 데이터베이스 세션 제공
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    
    Yields:
        Session: SQLAlchemy 데이터베이스 세션
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
