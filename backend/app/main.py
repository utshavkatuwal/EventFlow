from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings

# Absolute paths anchored at backend/ so mounts work regardless of CWD.
BASE_DIR = Path(__file__).resolve().parent.parent
TICKETS_DIR = BASE_DIR / "uploads" / "tickets"
EVENTS_DIR = BASE_DIR / "uploads" / "events"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.database import ensure_phase1_schema

        ensure_phase1_schema()
    except Exception:
        pass
    yield


app = FastAPI(
    title="EventFlow API",
    description="Professional event discovery, registration, and ticketing API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# QR ticket images (token-only, no PII). Verification docs are NEVER mounted.
TICKETS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads/tickets", StaticFiles(directory=str(TICKETS_DIR)), name="ticket-qr")

# Public event media: organizer-uploaded covers + videos (validated on upload).
EVENTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads/events", StaticFiles(directory=str(EVENTS_DIR)), name="event-media")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EventFlow API"}


@app.get("/api/health")
def api_health_check():
    """Spec alias: frontend → backend → database health in one call."""
    try:
        from sqlalchemy import text

        from app.database import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db = "connected"
    except Exception as e:
        db = f"error: {e}"
    return {"status": "ok" if db == "connected" else "degraded", "database": db}


@app.get("/")
def root():
    return {"message": "EventFlow API", "version": "1.0.0"}
