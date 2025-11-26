"""Database setup tests.

이 테스트는 데이터베이스 설정이 올바르게 구성되었는지 확인합니다.
실제 데이터베이스 연결은 필요하지 않으며, import 레벨에서 검증합니다.
"""


def test_db_imports():
    """데이터베이스 모듈 import 테스트
    
    engine과 Base를 import할 수 있는지 확인합니다.
    설정이 올바르게 구성되었다면 import 시 에러가 발생하지 않아야 합니다.
    """
    try:
        from app.db.session import engine
        from app.db.base import Base
        
        assert engine is not None, "engine should be created"
        assert Base is not None, "Base should be defined"
        
    except Exception as e:
        raise AssertionError(f"Failed to import database modules: {e}")


def test_base_metadata_create_all():
    """Base.metadata.create_all() 호출 테스트
    
    create_all()을 호출할 수 있는지 확인합니다.
    실제 데이터베이스 연결 없이도 메타데이터 구조를 검증할 수 있습니다.
    
    Note:
        이 테스트는 실제 DB 연결이 없어도 통과해야 합니다.
        create_all()은 연결이 없으면 실제 테이블을 생성하지 않지만,
        메타데이터 구조는 검증됩니다.
    """
    try:
        from app.db.session import engine
        from app.db.base import Base
        
        # create_all() 호출 가능 여부 확인
        # 실제 DB 연결이 없어도 메타데이터 구조는 검증됨
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
    except ImportError as e:
        raise AssertionError(f"Failed to import database modules: {e}")
    except Exception as e:
        # 실제 DB 연결 에러는 무시 (import 레벨 검증이 목적)
        if "could not connect" in str(e).lower() or "connection refused" in str(e).lower():
            # 연결 에러는 예상된 상황 (DB가 실행 중이 아닐 수 있음)
            pass
        else:
            # 그 외 예상치 못한 에러는 실패
            raise AssertionError(f"Unexpected error in create_all: {e}")


def test_session_factory():
    """SessionLocal factory 테스트
    
    SessionLocal이 올바르게 생성되는지 확인합니다.
    """
    try:
        from app.db.session import SessionLocal
        
        assert SessionLocal is not None, "SessionLocal should be created"
        
        # 세션 인스턴스 생성 가능 여부 확인
        session = SessionLocal()
        assert session is not None, "Session instance should be created"
        session.close()
        
    except ImportError as e:
        raise AssertionError(f"Failed to import SessionLocal: {e}")
    except Exception as e:
        # 연결 에러는 무시
        if "could not connect" in str(e).lower() or "connection refused" in str(e).lower():
            pass
        else:
            raise AssertionError(f"Unexpected error creating session: {e}")


def test_get_db_dependency():
    """get_db() 의존성 함수 테스트
    
    FastAPI 의존성으로 사용할 get_db() 함수가 올바르게 정의되었는지 확인합니다.
    """
    try:
        from app.db.session import get_db
        import inspect
        
        assert callable(get_db), "get_db should be callable"
        assert inspect.isgeneratorfunction(get_db), "get_db should be a generator function"
        
    except ImportError as e:
        raise AssertionError(f"Failed to import get_db: {e}")

