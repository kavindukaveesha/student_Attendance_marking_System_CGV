"""Investigate feature module — exposes F5 signature verification as an endpoint.

Owns: signature verification detail (which references matched, individual scores)
so a lecturer can audit a student's signatures across sessions.
"""
from backend.features.investigate.controller import router

__all__ = ["router"]
