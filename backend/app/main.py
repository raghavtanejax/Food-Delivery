"""
FastAPI application entry point.
Serves the API and the static frontend files.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.database import init_db, close_db
from app.routers import auth, menu, orders, notices, user


# --- Lifespan (startup / shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup, close on shutdown."""
    await init_db()
    yield
    await close_db()


# --- Create the FastAPI app ---
app = FastAPI(
    title="🍔 FoodieExpress API",
    description="Single-restaurant food delivery application",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Register Routers ---
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(notices.router)
app.include_router(user.router)

# --- Serve Frontend Static Files ---
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

# Mount static assets (CSS, JS)
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")


# --- Frontend Page Routes ---
@app.get("/")
async def serve_home():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/home")
async def serve_home_page():
    return FileResponse(str(FRONTEND_DIR / "home.html"))


@app.get("/menu")
async def serve_menu():
    return FileResponse(str(FRONTEND_DIR / "menu.html"))


@app.get("/orders")
async def serve_orders():
    return FileResponse(str(FRONTEND_DIR / "orders.html"))


@app.get("/admin")
async def serve_admin():
    return FileResponse(str(FRONTEND_DIR / "admin.html"))


@app.get("/settings")
async def serve_settings():
    return FileResponse(str(FRONTEND_DIR / "settings.html"))
