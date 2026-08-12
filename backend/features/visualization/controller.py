"""HTTP routes for per-student attendance chart rendering."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.attendance import service as attendance_service
from backend.features.attendance.repository import get_student
from backend.features.visualization import service as visualization_service


router = APIRouter(prefix="/api/visualization", tags=["visualization"])


@router.get("/{student_idx}")
def chart(
    student_idx: str,
    kind: str = Query("bar", pattern="^(bar|pie)$"),
    db: Session = Depends(get_db),
):
    student = get_student(db, student_idx)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    records = attendance_service.list_student_attendance(db, student_idx)
    label = f"{student.name} ({student_idx})"

    if kind == "pie":
        buf = visualization_service.attendance_pie_png(records, student_label=label)
    else:
        buf = visualization_service.attendance_bar_png(records, student_label=label)

    return StreamingResponse(buf, media_type="image/png")
