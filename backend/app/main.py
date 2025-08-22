"""
InvestAI Backend - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="InvestAI API",
    description="AI-Powered Financial Advisor & Investment Planner for Indian Markets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to InvestAI API",
        "version": "1.0.0",
        "description": "AI-Powered Financial Advisor for Indian Markets",
        "docs": "/docs",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "InvestAI Backend",
        "version": "1.0.0"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    print("🚀 Starting InvestAI - AI-Powered Investment Management Platform")
    print("=" * 70)
    print("🌐 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("❤️ Health: http://localhost:8000/health")
    print("=" * 70)

    uvicorn.run(
        app,  # Use the app object directly instead of string reference
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
