"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import get_db
from app.core.logging import logger
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import configure_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting RAG Study Assistant API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"AI Provider: {settings.ai_provider}")
    logger.info(f"Embedding Provider: {settings.embedding_provider}")
    logger.info(f"Supabase URL: {settings.supabase_url}")
    
    # Test database connection
    try:
        db_client = get_db()
        result = db_client.table("subjects").select("id").limit(1).execute()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Study Assistant API")


# Create FastAPI app
app = FastAPI(
    title="RAG Study Assistant API",
    description="AI-powered study assistant with flexible model support",
    version="0.1.0",
    lifespan=lifespan
)

# Exception Handlers
configure_exception_handlers(app)

# Middleware
app.add_middleware(RequestIDMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Study Assistant API",
        "version": "0.1.0",
        "ai_provider": settings.ai_provider,
        "embedding_provider": settings.embedding_provider
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "ai_provider": settings.ai_provider,
        "embedding_provider": settings.embedding_provider
    }


# Import and include routers
from app.api.v1 import api_router
app.include_router(api_router, prefix="/api/v1")
