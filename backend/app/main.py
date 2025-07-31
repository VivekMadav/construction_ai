from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os
import time
from contextlib import asynccontextmanager

from .core.config import settings
from .core.database import engine, Base
from .api import projects, drawings, elements, materials, analysis, reports, steel, concrete, enhanced_analysis, drawing_notes

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app with lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Construction AI Platform...")
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Ensure upload directory exists
        os.makedirs("uploads", exist_ok=True)
        logger.info("Upload directory ready")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Construction AI Platform...")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered platform for construction professionals to automate cost estimation and analysis",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response

# Add CORS middleware with improved configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Mount static files with error handling
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    logger.info("Static files mounted at /uploads")
else:
    logger.warning("Uploads directory not found, static files not mounted")

# Include API routes with error handling
try:
    app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
    app.include_router(drawings.router, prefix="/api/v1/drawings", tags=["drawings"])
    app.include_router(elements.router, prefix="/api/v1/elements", tags=["elements"])
    app.include_router(materials.router, prefix="/api/v1/materials", tags=["materials"])
    app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
    app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
    app.include_router(steel.router, prefix="/api/v1/steel", tags=["steel"])
    app.include_router(concrete.router, prefix="/api/v1/concrete", tags=["concrete"])
    app.include_router(enhanced_analysis.router, prefix="/api/v1/enhanced-analysis", tags=["enhanced-analysis"])
    app.include_router(drawing_notes.router, prefix="/api/v1/drawing-notes", tags=["drawing-notes"])
    logger.info("All API routes loaded successfully")
except Exception as e:
    logger.error(f"Error loading API routes: {e}")
    raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Construction AI Platform",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    try:
        # Test database connection
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "version": settings.app_version,
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "version": settings.app_version,
            "database": "disconnected",
            "error": str(e),
            "timestamp": time.time()
        }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global HTTP exception handler"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "path": str(request.url)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 