"""
Shelf Life Estimator — FastAPI Application
============================================
Main entry point for the backend server.

Run with:
    uvicorn app.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db, async_session
from app.seed_data import seed_database
from app.schemas.schemas import HealthResponse

# Import routers
from app.routers import foods, scan, inventory

settings = get_settings()


# ============================================
# Application Lifespan (Startup / Shutdown)
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.

    Startup:
        1. Create database tables
        2. Seed database with food items
        3. Create upload directory

    Shutdown:
        - Clean up resources
    """
    # --- Startup ---
    print("🚀 Starting Shelf Life Estimator API...")

    # Create database tables
    await init_db()
    print("📦 Database tables created")

    # Seed database
    async with async_session() as session:
        await seed_database(session)

    # Create upload directory
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Upload directory ready: {upload_dir}")

    # Create models directory (for AI model files)
    models_dir = Path("models")
    models_dir.mkdir(parents=True, exist_ok=True)

    print("✅ Shelf Life Estimator API is ready!")
    print(f"📖 API Docs: http://localhost:8000/docs")
    print(f"📖 ReDoc: http://localhost:8000/redoc")

    yield  # App is running

    # --- Shutdown ---
    print("👋 Shutting down Shelf Life Estimator API...")


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "🍎 **Shelf Life Estimator API — Fruits Edition**\n\n"
        "Scan fruits via camera or manual selection, "
        "get AI-powered freshness assessment and shelf life estimates.\n\n"
        "## Features\n"
        "- 📸 **Fruit Scanning** — Upload an image to identify fruit and assess freshness\n"
        "- 🔍 **Fruit Database** — Browse 40+ fruits with shelf life data\n"
        "- 📋 **Inventory Tracking** — Track your fruits and their expiry dates\n"
        "- 🔔 **Expiry Notifications** — Get alerted before fruit goes bad\n"
        "- 💡 **Storage Tips** — Learn how to store fruits properly\n"
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================
# Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Static Files (uploaded images)
# ============================================

# Serve uploaded images at /uploads/filename.jpg
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


# ============================================
# Include Routers
# ============================================

app.include_router(foods.router)
app.include_router(scan.router)
app.include_router(inventory.router)


# ============================================
# Root Endpoints
# ============================================

@app.get(
    "/",
    summary="Root",
    description="API welcome message and quick links.",
)
async def root():
    """Root endpoint with API info."""
    return {
        "message": f"🍎 Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "scan": "POST /api/scan/",
            "foods": "GET /api/foods/",
            "inventory": "GET /api/inventory/",
        },
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    tags=["System"],
)
async def health_check():
    """Server health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        debug=settings.debug,
    )
