from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import students, iep_versions
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Import all models to register them with Base.metadata
import app.models  # noqa

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.app_debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """애플리케이션 시작 이벤트"""
    Base.metadata.create_all(bind=engine)


# Include routers
app.include_router(students.router)
app.include_router(iep_versions.router)


@app.get("/")
def root():
    """루트 엔드포인트"""
    return {"message": "IEP Planning Support API"}


@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }
