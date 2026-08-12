"""HTTP demo endpoint for F1 (Member 1) — image acquisition & preprocessing.

Lets you POST an arbitrary image and get back URLs for the original, greyscale,
and denoised stages. Same code path as the main pipeline uses; independent
here so Member 1 can demo their module without invoking the whole workflow.
"""
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.features.image_processing.service import denoise, save_stage, to_greyscale


router = APIRouter(prefix="/api/features/image-processing", tags=["F1 · image_processing"])


def _demo_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    out = Path("output/feature_demos/image_processing") / stamp
    out.mkdir(parents=True, exist_ok=True)
    return out


@router.post("/preview")
async def preview(image: UploadFile = File(...)):
    data = await image.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")

    gray = to_greyscale(img)
    smooth = denoise(gray, ksize=5)

    out = _demo_dir()
    return {
        "original":  "/" + save_stage(img,    "01_original.png",  out).as_posix(),
        "greyscale": "/" + save_stage(gray,   "02_greyscale.png", out).as_posix(),
        "smoothed":  "/" + save_stage(smooth, "03_smoothed.png",  out).as_posix(),
    }
