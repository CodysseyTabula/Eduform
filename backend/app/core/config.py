from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Application
    app_name: str = Field(default="IEP Planning Support Service")
    app_version: str = Field(default="1.0.0")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    
    # Database
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: str = Field(default="postgres", alias="DB_PASSWORD")
    db_name: str = Field(default="iep_db", alias="DB_NAME")
    database_url: str | None = None
    
    # Storage
    storage_path: str = Field(default="./storage", alias="STORAGE_PATH")
    
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

