"""HTTP demo endpoint for F4 (Member 4) — signature detection (present/absent)."""
import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.core.config import settings
from backend.features.image_processing.service import to_greyscale
from backend.features.signature_detection.service import ink_ratio, is_signed
from backend.features.table_extraction.service import binarize


router = APIRouter(
    prefix="/api/features/signature-detection", tags=["F4 · signature_detection"]
)


@router.post("/check")
async def check(image: UploadFile = File(...)):
    data = await image.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")

    gray = to_greyscale(img)
    binary = binarize(gray)
    ratio = ink_ratio(binary)
    signed = is_signed(binary, settings.INK_THRESHOLD)

    return {
        "ink_ratio": round(ratio, 6),
        "threshold": settings.INK_THRESHOLD,
        "signed": signed,
        "status": "present" if signed else "absent",
    }
