from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Application
    app_name: str = Field(default="IEP Planning Support API")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="local")
    app_debug: bool = Field(default=True)
    app_port: int = Field(default=8000)
    
    # Database
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=5432)
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="postgres")
    db_name: str = Field(default="iep_db")
    database_url: str | None = None
    
    # Storage
    storage_path: str = Field(default="./storage")
    
    @property
    def sqlalchemy_database_uri(self) -> str:
        """SQLAlchemy 데이터베이스 URI 생성"""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# 싱글톤 인스턴스
settings = Settings()
