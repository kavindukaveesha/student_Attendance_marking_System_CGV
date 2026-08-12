"""F5 - Signature verification feature module (Member 5).

Owns: ORB feature matching against reference signatures, similarity scoring.
"""
from backend.features.signature_recognition.controller import router
from backend.features.signature_recognition.service import (
    compare,
    references_for,
    verify,
)

__all__ = ["router", "compare", "verify", "references_for"]
