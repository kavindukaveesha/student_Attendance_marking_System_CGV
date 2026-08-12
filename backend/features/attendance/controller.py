"""HTTP routes for the attendance workflow.

Two routers are exposed:
- `router`          — POST /api/attendance/process  and  POST /api/attendance/save
- `students_router` — GET  /api/students, /api/students/{idx}, /{idx}/attendance
"""
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.features.attendance import service
from backend.features.attendance.repository import get_student, list_students
from backend.features.attendance.schema import (
    AttendanceRecord,
    ProcessResponse,
    SavePayload,
    SaveResponse,
    StudentOut,
)


router = APIRouter(prefix="/api/attendance", tags=["attendance"])


async def _persist_upload(upload: UploadFile, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / (upload.filename or "upload.bin")
    with dest.open("wb") as fh:
        shutil.copyfileobj(upload.file, fh)
    return dest


@router.post("/process", response_model=ProcessResponse)
async def process_sheet(
    image: UploadFile = File(...),
    info: UploadFile = File(...),
):
    image_path = await _persist_upload(image, settings.sheets_path)
    xml_path = await _persist_upload(info, Path("data"))
    try:
        return service.process_sheet(image_path, xml_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/save", response_model=SaveResponse)
def save_results(payload: SavePayload, db: Session = Depends(get_db)):
    saved = service.persist_results(
        db,
        results=[r.model_dump() for r in payload.results],
        subject=payload.subject.model_dump(),
    )
    return SaveResponse(saved=saved)


students_router = APIRouter(prefix="/api/students", tags=["students"])


@students_router.get("", response_model=list[StudentOut])
def all_students(db: Session = Depends(get_db)):
    return list_students(db)


@students_router.get("/{student_idx}", response_model=StudentOut)
def student_detail(student_idx: str, db: Session = Depends(get_db)):
    student = get_student(db, student_idx)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@students_router.get("/{student_idx}/attendance", response_model=list[AttendanceRecord])
def student_attendance(student_idx: str, db: Session = Depends(get_db)):
    return service.list_student_attendance(db, student_idx)
