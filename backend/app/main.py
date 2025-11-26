from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import students, iep_versions, iep_files
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Import all models to register them with Base.metadata
import app.models  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (필요시 정리 작업)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.app_debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(students.router)
app.include_router(iep_versions.router)
app.include_router(iep_files.router)


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
