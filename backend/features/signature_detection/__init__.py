"""F4 - Signature detection feature module (Member 4).

Owns: ink-ratio measurement, present/absent decision.
"""
from backend.features.signature_detection.controller import router
from backend.features.signature_detection.service import detect_all, ink_ratio, is_signed

__all__ = ["router", "ink_ratio", "is_signed", "detect_all"]
