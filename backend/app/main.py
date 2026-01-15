"""
SplitDumb FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, users, groups, expenses, balances, settlements, activity
from app.core.config import settings
from app.core.database import engine
from app.infrastructure.db.models import Base

# Create tables (in production, use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SplitDumb API",
    description="Expense sharing API",
    version="0.1.0",
)

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(groups.router, prefix="/groups", tags=["groups"])
app.include_router(expenses.router, prefix="/groups", tags=["expenses"])
app.include_router(balances.router, prefix="/groups", tags=["balances"])
app.include_router(settlements.router, prefix="/groups", tags=["settlements"])
app.include_router(activity.router, prefix="/groups", tags=["activity"])


@app.get("/")
async def root():
    return {"message": "SplitDumb API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
