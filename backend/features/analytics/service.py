"""Aggregate stats over the attendance + students tables."""
from collections import defaultdict

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.features.attendance.model import Attendance, Student


def summary(db: Session) -> dict:
    total_students = db.query(func.count(Student.student_idx)).scalar() or 0
    total_records = db.query(func.count(Attendance.id)).scalar() or 0
    total_sessions = (
        db.query(func.count(func.distinct(Attendance.date)))
        .filter(Attendance.date.isnot(None))
        .scalar()
        or 0
    )

    status_rows = (
        db.query(Attendance.status, func.count(Attendance.id))
        .group_by(Attendance.status)
        .all()
    )
    status_counts = {"present": 0, "absent": 0, "flagged": 0}
    for status, count in status_rows:
        status_counts[status] = count

    per_session_rows = (
        db.query(
            Attendance.date,
            Attendance.status,
            func.count(Attendance.id),
        )
        .group_by(Attendance.date, Attendance.status)
        .order_by(Attendance.date.asc())
        .all()
    )
    sessions: dict[str, dict] = defaultdict(
        lambda: {"present": 0, "absent": 0, "flagged": 0, "total": 0}
    )
    for date, status, count in per_session_rows:
        if not date:
            continue
        sessions[date][status] = count
        sessions[date]["total"] += count

    per_session = []
    for date in sorted(sessions.keys()):
        row = sessions[date]
        total = row["total"] or 1
        present_pct = round(100.0 * row["present"] / total, 1)
        per_session.append(
            {
                "date": date,
                "present": row["present"],
                "absent": row["absent"],
                "flagged": row["flagged"],
                "total": row["total"],
                "attendance_rate": present_pct,
            }
        )

    absentee_rows = (
        db.query(
            Attendance.student_idx,
            Student.name,
            func.count(Attendance.id),
        )
        .join(Student, Student.student_idx == Attendance.student_idx)
        .filter(Attendance.status == "absent")
        .group_by(Attendance.student_idx, Student.name)
        .order_by(func.count(Attendance.id).desc())
        .limit(5)
        .all()
    )
    top_absentees = [
        {"student_idx": idx, "name": name, "absent_count": cnt}
        for idx, name, cnt in absentee_rows
    ]

    overall_rate = 0.0
    if total_records > 0:
        overall_rate = round(100.0 * status_counts["present"] / total_records, 1)

    return {
        "total_students": total_students,
        "total_sessions": total_sessions,
        "total_records": total_records,
        "status_counts": status_counts,
        "overall_attendance_rate": overall_rate,
        "per_session": per_session,
        "top_absentees": top_absentees,
    }
