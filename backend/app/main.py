# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import sys

from app.core.database import init_db, close_db, get_db
from app.api.v1 import auth
from app.api.v1 import api_router

FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")

# PyInstaller 打包模式：数据文件在 sys._MEIPASS 目录
if getattr(sys, 'frozen', False):
    FRONTEND_DIST = os.path.join(sys._MEIPASS, "frontend", "dist")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== Application starting up ===")
    print(f"FRONTEND_DIST = {FRONTEND_DIST}")
    print(f"  exists: {os.path.isdir(FRONTEND_DIST)}")
    print(f"  index.html: {os.path.isfile(os.path.join(FRONTEND_DIST, 'index.html'))}")
    await init_db()
    print(get_db.__name__)
    yield
    print("=== Application shutting down ===")
    await close_db()

app = FastAPI(
    title="NEXUS E-commerce",
    description="电商平台期末考核项目",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS（保留，以防未来需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由（优先于静态文件）
app.include_router(api_router, prefix="/api/v1")

# 托管前端静态资源
if os.path.isdir(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

# SPA 前端入口
@app.get("/")
async def serve_root():
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "NEXUS E-commerce is running"}

# Diagnostic endpoint
@app.get("/api/health")
async def health_check():
    """Health check for debugging blank page issues"""
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    return {
        "status": "ok",
        "frontend_dist_exists": os.path.isdir(FRONTEND_DIST),
        "assets_exists": os.path.isdir(assets_dir),
        "index_exists": os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")),
        "assets": os.listdir(assets_dir) if os.path.isdir(assets_dir) else [],
        "frontend_path": FRONTEND_DIST
    }

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("openapi"):
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "NEXUS E-commerce is running"}
