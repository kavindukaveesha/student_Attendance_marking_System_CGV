"""HTTP routes for signature investigation (F5 exposed as an endpoint)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.features.investigate import service


router = APIRouter(prefix="/api/investigate", tags=["investigate"])


@router.post("/{student_idx}")
def investigate(student_idx: str, db: Session = Depends(get_db)):
    return service.latest_verification(db, student_idx)


@router.get("/{student_idx}")
def investigate_get(student_idx: str, db: Session = Depends(get_db)):
    return service.latest_verification(db, student_idx)
