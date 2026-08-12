"""F3 - Table & cell segmentation feature module (Member 3).

Owns: binarization, grid detection via morphology, signature-cell extraction.
"""
from backend.features.table_extraction.controller import router
from backend.features.table_extraction.service import (
    binarize,
    detect_row_boxes,
    extract_signature_cells,
)

__all__ = ["router", "binarize", "detect_row_boxes", "extract_signature_cells"]
