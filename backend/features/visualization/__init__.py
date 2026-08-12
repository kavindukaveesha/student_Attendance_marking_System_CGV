"""F7 - Data visualization feature module (Member 7).

Owns: matplotlib chart generation (bar timeline + summary pie) and HTTP endpoints
that stream PNG charts for a given student.
"""
from backend.features.visualization.controller import router

__all__ = ["router"]
