from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Precision Agriculture Using Deep Learning - API Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["System"])
def health_check():
    """
    Health check endpoint to verify API service status and connectivity.
    """
    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/", tags=["System"])
def root():
    """
    Root endpoint providing basic API metadata and navigation links.
    """
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "health_check": "/api/health",
        "docs": "/docs"
    }
