"""Pipeline orchestrator — chains F1..F5 for one signing sheet.

Saves every stage image to output/processed/<timestamp>/ for report screenshots.
Pure Python: no FastAPI, no DB imports.
"""
from datetime import datetime
from pathlib import Path

import cv2
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.features.attendance import repository
from backend.features.attendance.info_parser import parse_info
from backend.features.image_processing import service as image_processing
from backend.features.signature_detection import service as signature_detection
from backend.features.signature_recognition import service as signature_recognition
from backend.features.table_extraction import service as table_extraction
from backend.features.transforms import service as transforms


def process_sheet(
    image_path: str | Path,
    xml_path: str | Path,
    processed_dir: str | Path | None = None,
    signatures_dir: str | Path | None = None,
) -> dict:
    processed_dir = Path(processed_dir or settings.PROCESSED_DIR)
    signatures_dir = Path(signatures_dir or settings.SIGNATURES_DIR)
    processed_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stage_dir = processed_dir / stamp
    stage_dir.mkdir(parents=True, exist_ok=True)

    subject, students = parse_info(xml_path)
    stages: dict[str, str] = {}

    def _stage(img, name: str, label: str) -> None:
        path = image_processing.save_stage(img, name, stage_dir)
        stages[label] = "/" + path.as_posix()

    original = image_processing.load_image(image_path)
    _stage(original, "01_original.png", "original")

    gray = image_processing.to_greyscale(original)
    _stage(gray, "02_greyscale.png", "greyscale")

    smooth = image_processing.denoise(gray, ksize=5)
    _stage(smooth, "03_denoised.png", "smoothed")

    deskewed = transforms.deskew(smooth)
    _stage(deskewed, "04_deskewed.png", "rotated")

    resized = transforms.normalize_size(deskewed)
    _stage(resized, "05_resized.png", "resized")

    binary = table_extraction.binarize(resized)
    _stage(binary, "06_binarized.png", "binary")

    grid_kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    grid_kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    grid_preview = cv2.add(
        cv2.morphologyEx(binary, cv2.MORPH_OPEN, grid_kernel_h),
        cv2.morphologyEx(binary, cv2.MORPH_OPEN, grid_kernel_v),
    )
    _stage(grid_preview, "07_grid.png", "grid")

    cells = table_extraction.extract_signature_cells(binary, num_students=len(students))

    results: list[dict] = []
    for student, cell in zip(students, cells):
        signed = signature_detection.is_signed(cell, settings.INK_THRESHOLD)
        score: float | None = None
        status: str

        if not signed:
            status = "absent"
        else:
            refs = signature_recognition.references_for(student["index"], signatures_dir)
            if refs:
                cell_gray = 255 - cell
                score, matched = signature_recognition.verify(
                    cell_gray, refs, settings.MATCH_THRESHOLD
                )
                status = "present" if matched else "flagged"
            else:
                status = "present"

        results.append(
            {
                "no": student["no"],
                "index": student["index"],
                "name": student["name"],
                "status": status,
                "score": round(score, 4) if score is not None else None,
            }
        )

    _stage(binary, "08_final_binary.png", "cells")

    return {"subject": subject, "results": results, "stages": stages}


def persist_results(db: Session, results: list[dict], subject: dict) -> int:
    return repository.save_records(db, results, subject)


def list_student_attendance(db: Session, student_idx: str) -> list[dict]:
    rows = repository.get_by_student(db, student_idx)
    return [
        {
            "student_idx": r.student_idx,
            "subject_code": r.subject_code,
            "date": r.date,
            "status": r.status,
            "match_score": r.match_score,
        }
        for r in rows
    ]
