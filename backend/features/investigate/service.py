"""Signature-verification reporting.

Look up the most recent stored attendance record for a student and translate its
status + score into a human-readable message for the UI.
"""
from sqlalchemy.orm import Session

from backend.features.attendance.model import Attendance, Student


STATUS_MESSAGE = {
    "present": "Signature matches reference — verified.",
    "absent": "No signature detected for this session.",
    "flagged": "Signature does not match reference — possible proxy.",
}


def latest_verification(db: Session, student_idx: str) -> dict:
    student = db.get(Student, student_idx)
    if student is None:
        return {
            "index": student_idx,
            "name": None,
            "status": "unknown",
            "score": None,
            "date": None,
            "message": "Student not found in the database.",
        }

    row = (
        db.query(Attendance)
        .filter(Attendance.student_idx == student_idx)
        .order_by(Attendance.date.desc(), Attendance.id.desc())
        .first()
    )
    if row is None:
        return {
            "index": student_idx,
            "name": student.name,
            "status": "unknown",
            "score": None,
            "date": None,
            "message": "No attendance records yet for this student.",
        }

    return {
        "index": student_idx,
        "name": student.name,
        "status": row.status,
        "score": row.match_score,
        "date": row.date,
        "message": STATUS_MESSAGE.get(row.status, ""),
    }
