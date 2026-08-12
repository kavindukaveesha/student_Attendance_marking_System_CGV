"""ORB feature matching vs reference signatures."""
from pathlib import Path

import cv2
import numpy as np


def _load_reference(path: str | Path) -> np.ndarray | None:
    return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)


def _normalize(img: np.ndarray, size: tuple[int, int] = (300, 150)) -> np.ndarray:
    resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    if resized.dtype != np.uint8:
        resized = resized.astype(np.uint8)
    return resized


def compare(detected: np.ndarray, reference: np.ndarray) -> float:
    if detected is None or reference is None:
        return 0.0
    a = _normalize(detected)
    b = _normalize(reference)

    orb = cv2.ORB_create(nfeatures=500)
    kp1, des1 = orb.detectAndCompute(a, None)
    kp2, des2 = orb.detectAndCompute(b, None)
    if des1 is None or des2 is None or len(kp1) == 0 or len(kp2) == 0:
        return 0.0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    good = [m for m in matches if m.distance < 50]
    return float(len(good)) / float(max(len(kp1), len(kp2)))


def verify(
    detected: np.ndarray, reference_paths: list[str | Path], threshold: float
) -> tuple[float, bool]:
    best = 0.0
    for ref_path in reference_paths:
        ref = _load_reference(ref_path)
        if ref is None:
            continue
        score = compare(detected, ref)
        if score > best:
            best = score
    return best, best >= threshold


def references_for(student_idx: str, signatures_dir: str | Path) -> list[Path]:
    folder = Path(signatures_dir) / student_idx
    if not folder.exists():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"})
