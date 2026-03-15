from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes.contracts import router as contracts_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.policies import router as policies_router
from app.api.routes.uploads import router as uploads_router
from app.db.base import Base
from app.services.ocr import NoopOcrClient
from app.services.storage import LocalStorageService


app = FastAPI(title="LegalTech MVP API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///./legaltech.db", connect_args={"check_same_thread": False})
app.state.session_factory = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

Base.metadata.create_all(bind=engine)
app.include_router(policies_router)
app.include_router(contracts_router)
app.include_router(uploads_router)
app.include_router(notifications_router)
app.state.storage_service = LocalStorageService(Path(__file__).resolve().parents[1] / "uploads")
app.state.ocr_client = NoopOcrClient()


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
