from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.routers import auth, songs, admin
from backend.utils.queueing import song_queue_manager
from backend.utils.fpp_commands import lights_on, lights_off

app = FastAPI(
    title="Christmas Lightshow API",
    description="API for managing Christmas lightshow song requests and controls",
    version="2.0.0"
)

# Initialize scheduler
scheduler = BackgroundScheduler()

# CORS configuration - allow frontend origin
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:80",    # Production nginx
    "http://localhost",       # Production nginx (alternate)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(songs.router, prefix="/api/songs", tags=["songs"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.on_event("startup")
async def startup_event():
    """Start the song queue background thread on application startup."""
    threading.Thread(target=song_queue_manager.loop_songs, daemon=True).start()
    print("[STARTUP] Song queue manager thread started")

    # Schedule lights on/off
    scheduler.add_job(lights_on, CronTrigger(hour=17, minute=0))  # 5:00 PM
    scheduler.add_job(lights_off, CronTrigger(hour=23, minute=0))  # 11:00 PM
    scheduler.start()
    print("[STARTUP] Light scheduler started (ON: 5:00 PM, OFF: 11:00 PM)")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    scheduler.shutdown()
    print("[SHUTDOWN] Application shutting down")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "christmas-lightshow-api"
    }


@app.get("/api/banner")
async def get_banner():
    """Get banner content from banner.md file."""
    banner_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "banner.md")

    try:
        if os.path.exists(banner_path):
            with open(banner_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            return {"content": content if content else None}
        else:
            return {"content": None}
    except Exception as e:
        print(f"[ERROR] Failed to read banner: {e}")
        return {"content": None}
