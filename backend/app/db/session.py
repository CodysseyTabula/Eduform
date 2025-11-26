from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 데이터베이스 엔진 생성
# pool_pre_ping=True: 연결 풀에서 연결을 가져올 때 연결 상태를 확인
engine = create_engine(
    settings.sqlalchemy_database_uri,
    echo=settings.app_debug,  # 디버그 모드에서 SQL 쿼리 로깅
    pool_pre_ping=True,  # 연결 풀 연결 상태 체크
)

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
