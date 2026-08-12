"""HTTP demo endpoint for F3 (Member 3) — table & cell segmentation."""
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.features.image_processing.service import denoise, save_stage, to_greyscale
from backend.features.table_extraction.service import binarize, extract_signature_cells
from backend.features.transforms.service import deskew, normalize_size


router = APIRouter(prefix="/api/features/table-extraction", tags=["F3 · table_extraction"])


def _demo_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    out = Path("output/feature_demos/table_extraction") / stamp
    out.mkdir(parents=True, exist_ok=True)
    return out


@router.post("/cells")
async def cells(image: UploadFile = File(...), num_students: int = Form(6)):
    if num_students < 1 or num_students > 50:
        raise HTTPException(status_code=400, detail="num_students must be between 1 and 50.")

    data = await image.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode the uploaded image.")

    gray = denoise(to_greyscale(img))
    aligned = normalize_size(deskew(gray))
    binary = binarize(aligned)

    out = _demo_dir()
    binary_url = "/" + save_stage(binary, "00_binary.png", out).as_posix()

    extracted = extract_signature_cells(binary, num_students=num_students)
    cell_urls = []
    for i, cell in enumerate(extracted, start=1):
        url = "/" + save_stage(cell, f"cell_{i:02d}.png", out).as_posix()
        cell_urls.append(url)

    return {
        "num_students_requested": num_students,
        "cells_extracted": len(cell_urls),
        "binary": binary_url,
        "cells": cell_urls,
    }
