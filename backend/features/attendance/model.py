"""SQLAlchemy ORM models.

- `Student`    — one row per student, keyed by university index.
- `Attendance` — one row per (student, subject, date). CHECK constraint enforces
                 the 3-way status (present / absent / flagged).
"""
from sqlalchemy import (
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Student(Base):
    __tablename__ = "students"

    student_idx = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    signature_ref = Column(Text)

    attendance_records = relationship(
        "Attendance", back_populates="student", cascade="all, delete-orphan"
    )


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_idx = Column(String, ForeignKey("students.student_idx"), nullable=False)
    subject_code = Column(String)
    date = Column(String)
    status = Column(String, nullable=False)
    match_score = Column(Float)

    student = relationship("Student", back_populates="attendance_records")

    __table_args__ = (
        UniqueConstraint("student_idx", "subject_code", "date", name="uq_student_subject_date"),
        CheckConstraint("status IN ('present','absent','flagged')", name="ck_status_values"),
    )
