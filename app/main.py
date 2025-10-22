from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, users
from app.application.exceptions import ApplicationError

# Create FastAPI application
app = FastAPI(
    title="Coffee Shop API",
    description="User management module for Coffee Shop application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ApplicationError)
async def application_error_handler(request: Request, exc: ApplicationError):
    """
    Global exception handler for application layer errors.
    """
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# Include routers
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/", summary="Health check", description="Check if the API is running")
async def root():
    """
    Root endpoint for health check.
    """
    return {
        "message": "Coffee Shop API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get(
    "/health", summary="Health check", description="Detailed health check endpoint"
)
async def health():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "service": "coffee-shop-api", "version": "1.0.0"}
