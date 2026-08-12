"""F6 - Attendance feature module (Member 6).

Owns: SQLAlchemy models, info.xml parser, repository, pipeline orchestration
service, and REST controllers for processing + saving attendance sheets, plus
student CRUD endpoints (students are tightly coupled to attendance records).
"""
from backend.features.attendance.controller import router, students_router

__all__ = ["router", "students_router"]
