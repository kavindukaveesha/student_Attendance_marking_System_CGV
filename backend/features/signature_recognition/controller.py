"""HTTP demo endpoint for F5 (Member 5) — signature verification via ORB matching."""
import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.core.config import settings
from backend.features.signature_recognition.service import compare


router = APIRouter(
    prefix="/api/features/signature-recognition", tags=["F5 · signature_recognition"]
)


async def _decode_gray(upload: UploadFile) -> np.ndarray:
    data = await upload.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise HTTPException(status_code=400, detail=f"Could not decode {upload.filename!r}.")
    return img


@router.post("/compare")
async def compare_endpoint(
    sample: UploadFile = File(...),
    reference: UploadFile = File(...),
):
    a = await _decode_gray(sample)
    b = await _decode_gray(reference)
    score = compare(a, b)
    matched = score >= settings.MATCH_THRESHOLD

    return {
        "score": round(score, 4),
        "threshold": settings.MATCH_THRESHOLD,
        "matched": matched,
        "verdict": "match" if matched else "mismatch",
    }
