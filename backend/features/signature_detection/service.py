"""Decide present vs empty by measuring ink content in a signature cell."""
import cv2
import numpy as np


def ink_ratio(cell_binary: np.ndarray) -> float:
    if cell_binary.size == 0:
        return 0.0
    return float(cv2.countNonZero(cell_binary)) / float(cell_binary.size)


def is_signed(cell_binary: np.ndarray, threshold: float) -> bool:
    return ink_ratio(cell_binary) >= threshold


def detect_all(cells: list[np.ndarray], threshold: float) -> list[bool]:
    return [is_signed(c, threshold) for c in cells]
