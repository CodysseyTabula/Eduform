from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """모든 ORM 모델의 베이스 클래스
    
    Usage:
        1. 새로운 모델 생성 시 이 클래스를 상속받습니다:
            class MyModel(Base):
                __tablename__ = "my_table"
                ...
        
        2. Base.metadata.create_all()이 작동하려면 
           모델을 이 파일에서 import해야 합니다:
            # Import all models here for metadata.create_all()
            # from app.models.student import Student  # noqa: F401
            # from app.models.iep_version import IEPVersion  # noqa: F401
            # from app.models.iep_file import IEPFile  # noqa: F401
    """
    pass


# Import all models here for metadata registration
# 모델이 생성되면 아래에 import 추가 (예시):
# from app.models.student import Student  # noqa: F401
# from app.models.iep_version import IEPVersion  # noqa: F401
# from app.models.iep_file import IEPFile  # noqa: F401
