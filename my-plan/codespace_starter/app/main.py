from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="WhatsApp Forensic Analyzer", version="0.1.0")

# Create directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "WhatsApp Forensic Analyzer",
        "cases": []  # Will be populated from DB later
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/api/cases")
async def list_cases():
    """List all cases - placeholder"""
    return {"cases": [], "total": 0}

# Include routers (add as we build)
# from app.routers import cases, chats, evidence
# app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
