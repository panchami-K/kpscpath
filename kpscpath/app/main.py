import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.errors import AppError
from app.core.response import error_response
from app.modules.auth.router import router as auth_router
from app.modules.onboarding.router import router as onboarding_router
from app.modules.syllabus.router import router as syllabus_router



app = FastAPI(
    title="KPSCPath API",
    description="AI-powered KPSC exam preparation platform",
    version="1.0.0",
    redirect_slashes=False,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global error handler
# ---------------------------------------------------------------------------
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        content=error_response(exc.code, exc.message),
        status_code=exc.status_code,
    )

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(syllabus_router, prefix="/api/v1")
# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {"service": "KPSCPath API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}