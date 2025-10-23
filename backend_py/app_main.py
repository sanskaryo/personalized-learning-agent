import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import get_settings
from .routers import chat, progress, resources, pdf, auth, planner, notes, audio, ocr, pyq, flashcards, gamification
from .utils.logger import setup_logger, log_api_call, log_error, log_success
import time

# Initialize logger
logger = setup_logger()

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="CodeMentor AI - Your AI Study Companion",
    version="1.0.0"
)


# CORS
origins = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log incoming request
    log_api_call(
        endpoint=request.url.path,
        method=request.method,
        user_id=request.headers.get("authorization", "anonymous")[:20]
    )
    
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    logger.info(f"⏱️ Request completed in {process_time:.3f}s - Status: {response.status_code}")
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_error(exc, f"Global exception handler - {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "status": "error"
        }
    )

@app.get("/health")
def health():
    log_success("Health check requested", "HealthEndpoint")
    return {
        "status": "ok",
        "message": "CodeMentor AI Backend is running",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to CodeMentor AI Backend",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(progress.router)
app.include_router(resources.router)
app.include_router(pdf.router)
app.include_router(planner.router)
app.include_router(notes.router)

# New feature routers
app.include_router(audio.router)
app.include_router(ocr.router)
app.include_router(pyq.router)
app.include_router(flashcards.router)
app.include_router(gamification.router)

# Startup event
@app.on_event("startup")
async def startup_event():
    log_success("🚀 CodeMentor AI Backend starting up", "Startup")
    logger.info("📊 Available endpoints:")
    logger.info("  - Auth: /api/auth/*")
    logger.info("  - Chat: /api/chat/*")
    logger.info("  - Progress: /api/progress/*")
    logger.info("  - Resources: /api/resources/*")
    logger.info("  - PDF: /api/pdf/*")
    logger.info("  - Planner: /api/planner/*")
    logger.info("  - Notes: /api/notes/*")
    logger.info("  🎤 Audio Transcription: /api/audio/*")
    logger.info("  📄 OCR: /api/ocr/*")
    logger.info("  🎯 PYQ Practice: /api/pyq/*")
    logger.info("  🎴 Flashcards: /api/flashcards/*")
    logger.info("  🏆 Gamification: /api/gamification/*")
    logger.info("  - Health: /health")
    logger.info("  - Docs: /docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    log_success("🛑 CodeMentor AI Backend shutting down", "Shutdown")


def get_uvicorn_host_port():
    h = "0.0.0.0"
    env_port = os.getenv("PORT")
    try:
        p = int(env_port) if env_port else int(settings.port)
    except (TypeError, ValueError):
        p = int(settings.port)
    return h, p


if __name__ == "__main__":
    import uvicorn
    host_val, port_val = get_uvicorn_host_port()
    uvicorn.run("backend_py.main_app:app", host=host_val, port=port_val, reload=True)
