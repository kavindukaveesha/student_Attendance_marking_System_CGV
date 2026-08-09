"""HTTP demo endpoint for F2 (Member 2) — geometric correction (deskew + scale)."""
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.features.image_processing.service import save_stage, to_greyscale
from backend.features.transforms.service import (
    estimate_skew_angle,
    normalize_size,
    rotate,
)


router = APIRouter(prefix="/api/features/transforms", tags=["F2 · transforms"])


def _demo_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    out = Path("output/feature_demos/transforms") / stamp
    out.mkdir(parents=True, exist_ok=True)
    return out


@router.post("/deskew")
async def deskew_endpoint(image: UploadFile = File(...)):
    data = await image.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")

    gray = to_greyscale(img)
    angle = estimate_skew_angle(gray)
    deskewed = rotate(gray, angle)
    resized = normalize_size(deskewed)

    out = _demo_dir()
    return {
        "detected_angle_degrees": round(angle, 3),
        "original":  "/" + save_stage(gray,     "01_input.png",    out).as_posix(),
        "deskewed":  "/" + save_stage(deskewed, "02_deskewed.png", out).as_posix(),
        "resized":   "/" + save_stage(resized,  "03_resized.png",  out).as_posix(),
    }
