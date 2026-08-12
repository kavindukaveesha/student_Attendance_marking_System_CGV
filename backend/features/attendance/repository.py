"""DB access layer for students + attendance.

Repository is the only place that touches SQLAlchemy queries; controllers and
services call these helpers instead of writing raw ORM.
"""
from sqlalchemy.orm import Session

from backend.features.attendance.model import Attendance, Student


def upsert_student(db: Session, index: str, name: str) -> Student:
    student = db.get(Student, index)
    if student is None:
        student = Student(student_idx=index, name=name)
        db.add(student)
    else:
        student.name = name
    return student


def save_records(db: Session, results: list[dict], subject: dict) -> int:
    saved = 0
    for r in results:
        upsert_student(db, r["index"], r["name"])

        existing = (
            db.query(Attendance)
            .filter(
                Attendance.student_idx == r["index"],
                Attendance.subject_code == subject.get("code"),
                Attendance.date == subject.get("date"),
            )
            .one_or_none()
        )
        if existing is None:
            db.add(
                Attendance(
                    student_idx=r["index"],
                    subject_code=subject.get("code"),
                    date=subject.get("date"),
                    status=r["status"],
                    match_score=r.get("score"),
                )
            )
        else:
            existing.status = r["status"]
            existing.match_score = r.get("score")
        saved += 1

    db.commit()
    return saved


def get_by_student(db: Session, student_idx: str) -> list[Attendance]:
    return (
        db.query(Attendance)
        .filter(Attendance.student_idx == student_idx)
        .order_by(Attendance.date.asc())
        .all()
    )


def get_student(db: Session, student_idx: str) -> Student | None:
    return db.get(Student, student_idx)


def list_students(db: Session) -> list[Student]:
    return db.query(Student).order_by(Student.student_idx.asc()).all()
