"""FastAPI application entry point.

Wires the six feature-module routers, mounts the generated `/output` directory
so pipeline stage images are directly viewable by the browser, and mounts the
static `frontend/` directory at `/` so the SPA and the API share one origin
(no CORS complexity in production).

Run:
    uvicorn backend.main:app --reload --port 8000
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.database import Base, engine
from backend.features.analytics import router as analytics_router
from backend.features.attendance import router as attendance_router, students_router
from backend.features.attendance.model import Attendance, Student  # noqa: F401 (register models)
from backend.features.image_processing import router as image_processing_router
from backend.features.investigate import router as investigate_router
from backend.features.signature_detection import router as signature_detection_router
from backend.features.signature_recognition import router as signature_recognition_router
from backend.features.table_extraction import router as table_extraction_router
from backend.features.transforms import router as transforms_router
from backend.features.visualization import router as visualization_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Attendance Management System",
    description="CS402.3 - Computer Graphics and Visualization coursework. "
    "OpenCV pipeline over photographed signing sheets.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attendance_router)
app.include_router(students_router)
app.include_router(visualization_router)
app.include_router(investigate_router)
app.include_router(analytics_router)

# Per-feature demo routers (F1 – F5). Each is owned by one group member and
# provides a standalone HTTP surface to demo that member's module.
app.include_router(image_processing_router)
app.include_router(transforms_router)
app.include_router(table_extraction_router)
app.include_router(signature_detection_router)
app.include_router(signature_recognition_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


output_dir = Path(__file__).resolve().parent.parent / "output"
output_dir.mkdir(parents=True, exist_ok=True)
app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
