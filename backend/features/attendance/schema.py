"""Pydantic request/response schemas for the attendance API."""
from typing import Literal

from pydantic import BaseModel, Field


class SubjectInfo(BaseModel):
    code: str
    title: str | None = None
    date: str
    lecturer: str | None = None
    hall: str | None = None


class StudentResult(BaseModel):
    no: int
    index: str
    name: str
    status: Literal["present", "absent", "flagged"]
    score: float | None = None


class ProcessResponse(BaseModel):
    subject: SubjectInfo
    results: list[StudentResult]
    stages: dict[str, str] = Field(default_factory=dict)


class SavePayload(BaseModel):
    subject: SubjectInfo
    results: list[StudentResult]


class SaveResponse(BaseModel):
    saved: int


class AttendanceRecord(BaseModel):
    student_idx: str
    subject_code: str | None
    date: str | None
    status: str
    match_score: float | None

    model_config = {"from_attributes": True}


class StudentOut(BaseModel):
    student_idx: str
    name: str

    model_config = {"from_attributes": True}
