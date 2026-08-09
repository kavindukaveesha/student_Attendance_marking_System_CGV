"""2D transformations: deskew (rotation) + resize (scaling).

Course link: L12.1 (2D transformations), L7.1 (Hough transform for skew).
"""
import cv2
import numpy as np


def estimate_skew_angle(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=100, minLineLength=gray.shape[1] // 4, maxLineGap=20
    )
    if lines is None:
        return 0.0

    angles = []
    for line in lines.reshape(-1, 4):
        x1, y1, x2, y2 = line
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if -45 < angle < 45:
            angles.append(angle)

    if not angles:
        return 0.0
    return float(np.median(angles))


def rotate(gray: np.ndarray, angle: float) -> np.ndarray:
    if abs(angle) < 0.1:
        return gray
    h, w = gray.shape[:2]
    center = (w / 2, h / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        gray, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def deskew(gray: np.ndarray) -> np.ndarray:
    angle = estimate_skew_angle(gray)
    return rotate(gray, angle)


def normalize_size(img: np.ndarray, size: tuple[int, int] = (1000, 1400)) -> np.ndarray:
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)
