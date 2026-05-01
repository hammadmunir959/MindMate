import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.models.base import Base

# Ensure all models are imported so metadata.create_all finds them
from app.models.admin import Admin
from app.models.patient import Patient
from app.models.specialist import Specialist
from app.models.forum import ForumQuestion, ForumAnswer
from app.models.appointment import Appointment

from app.api.v1.endpoints import specialists, patients, admins, forum, appointments, auth, agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables in the database
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
    yield
    # Cleanup on shutdown...

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(specialists.router, prefix="/api/v1/specialists", tags=["specialists"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])
app.include_router(admins.router, prefix="/api/v1/admins", tags=["admins"])
app.include_router(forum.router, prefix="/api/v1/forum", tags=["forum"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["appointments"])
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
