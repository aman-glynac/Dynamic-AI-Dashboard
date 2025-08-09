from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .endpoints import router
from .models import ErrorResponse

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Dashboard API",
    description="API for AI-powered dashboard generation with natural language prompts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "http://localhost:3001",  # Alternative port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["dashboard"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP {exc.status_code}",
            message=exc.detail,
            details=None
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            details=str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
        ).dict()
    )

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    print("🚀 AI Dashboard API starting up...")
    
    # Check if GROQ_API_KEY is set
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  WARNING: GROQ_API_KEY not found in environment variables")
        print("   Set GROQ_API_KEY to enable chart generation functionality")
    else:
        print("✅ GROQ_API_KEY found")
    
    # Check database directory
    if not os.path.exists("data"):
        os.makedirs("data")
        print("📁 Created data directory for SQLite database")
    
    # Check ChromaDB directory
    if not os.path.exists("chroma_db"):
        os.makedirs("chroma_db")
        print("📁 Created chroma_db directory for vector storage")
    
    print("✅ AI Dashboard API is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("🛑 AI Dashboard API shutting down...")

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )