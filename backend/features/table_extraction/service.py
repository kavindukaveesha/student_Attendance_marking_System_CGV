"""Detect the signing-sheet grid and return signature cells in row order.

Strategy (robust to weak grid lines and multi-header layouts):
1. Detect horizontal grid lines via morphological opening + row profile with a
   permissive threshold (7% of image width) — this catches faint lines but also
   noise.
2. Deduplicate near-adjacent detections (same physical line detected at its
   top and bottom edge).
3. If we get many candidate lines, find the longest run of approximately
   equally-spaced lines — the student rows are always uniformly spaced whereas
   header/subject rows are not. Prefer the bottom-most run since the student
   table is always at the bottom.
4. Take (num_students + 1) lines from the run as row boundaries.
5. Within that student-row y-range, detect vertical grid lines with a
   permissive threshold (must span 40% of the ROI height).
6. Signature column = interval between the last two vertical lines. If no
   vertical lines found, fall back to the right 25% of the image width, capped
   at 97% (avoid empty right margin diluting the ink ratio).

Course link: L4.3 (dilation & erosion), L6 (segmentation).
"""
import cv2
import numpy as np


def binarize(gray: np.ndarray) -> np.ndarray:
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 10
    )


def _line_positions(profile: np.ndarray, threshold: int) -> list[int]:
    positions: list[int] = []
    in_run = False
    run_start = 0
    for i, value in enumerate(profile):
        if value > threshold and not in_run:
            in_run = True
            run_start = i
        elif value <= threshold and in_run:
            in_run = False
            positions.append((run_start + i) // 2)
    if in_run:
        positions.append((run_start + len(profile)) // 2)
    return positions


def _dedupe(positions: list[int], min_gap: int) -> list[int]:
    if not positions:
        return []
    positions = sorted(positions)
    merged = [positions[0]]
    for p in positions[1:]:
        if p - merged[-1] < min_gap:
            merged[-1] = (merged[-1] + p) // 2
        else:
            merged.append(p)
    return merged


def _uniform_run(lines: list[int], target_count: int,
                 min_spacing: int = 20, max_spacing: int = 80,
                 tolerance: float = 0.25) -> list[int]:
    """Return a subset of `lines` that forms an approximately equally-spaced run
    of at least `target_count` positions. When multiple runs are the same length,
    prefer the one whose FIRST line is furthest down the image (student rows are
    always at the bottom). Returns [] if nothing matches."""
    n = len(lines)
    best: list[int] = []
    for start in range(n):
        for spacing in range(min_spacing, max_spacing + 1, 2):
            run = [lines[start]]
            expected = lines[start] + spacing
            for j in range(start + 1, n):
                if abs(lines[j] - expected) <= max(3, int(spacing * tolerance)):
                    run.append(lines[j])
                    expected = run[-1] + spacing
            # Prefer longer runs; ties broken by bottom-most start
            if (len(run) > len(best)) or (
                len(run) == len(best) and run and (not best or run[0] > best[0])
            ):
                best = run
    if len(best) >= target_count:
        # Trim excess from the top — keep the bottom-most target_count lines
        return best[-target_count:]
    return []


def _detect_h_lines(binary: np.ndarray, min_frac: float = 0.07) -> list[int]:
    h_img, w_img = binary.shape
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(30, w_img // 20), 1))
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel)
    row_sums = horizontal.sum(axis=1)
    threshold = int(w_img * 255 * min_frac)
    y_lines = _line_positions(row_sums, threshold)
    return _dedupe(y_lines, min_gap=8)


def _detect_v_lines(binary: np.ndarray, y0: int, y1: int,
                    min_frac: float = 0.40) -> list[int]:
    roi = binary[y0:y1, :]
    roi_h, w_img = roi.shape
    if roi_h < 20:
        return []
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(15, roi_h // 6)))
    vertical = cv2.morphologyEx(roi, cv2.MORPH_OPEN, v_kernel)
    col_sums = vertical.sum(axis=0)
    threshold = int(roi_h * 255 * min_frac)
    x_lines = _line_positions(col_sums, threshold)
    return _dedupe(x_lines, min_gap=10)


def _detect_grid_lines(binary: np.ndarray) -> tuple[list[int], list[int]]:
    """Legacy shape retained for compatibility — returns (y_lines, x_lines)."""
    y_lines = _detect_h_lines(binary)
    if len(y_lines) >= 2:
        x_lines = _detect_v_lines(binary, y_lines[0], y_lines[-1])
    else:
        x_lines = []
    return y_lines, x_lines


def detect_row_boxes(binary: np.ndarray) -> list[tuple[int, int, int, int]]:
    y_lines, x_lines = _detect_grid_lines(binary)
    if len(y_lines) < 2 or len(x_lines) < 2:
        return []
    boxes = []
    for i in range(len(y_lines) - 1):
        y0, y1 = y_lines[i], y_lines[i + 1]
        x0, x1 = x_lines[0], x_lines[-1]
        boxes.append((x0, y0, x1 - x0, y1 - y0))
    return boxes


def _naive_slice(binary: np.ndarray, num_students: int) -> list[np.ndarray]:
    h_img, w_img = binary.shape
    header = int(h_img * 0.35)
    usable = h_img - header
    row_h = max(1, usable // num_students)
    x0 = int(w_img * 0.72)
    x1 = int(w_img * 0.97)
    cells: list[np.ndarray] = []
    for i in range(num_students):
        y0 = header + i * row_h
        y1 = y0 + row_h
        cells.append(binary[y0:y1, x0:x1])
    return cells


def extract_signature_cells(binary: np.ndarray, num_students: int) -> list[np.ndarray]:
    y_lines = _detect_h_lines(binary)

    # Try progressively lower thresholds if too few lines
    for min_frac in (0.07, 0.05, 0.03):
        if len(y_lines) >= num_students + 1:
            break
        y_lines = _detect_h_lines(binary, min_frac=min_frac)

    if len(y_lines) < num_students + 1:
        return _naive_slice(binary, num_students)

    # Filter noise: keep only lines that fit a uniform-spacing pattern.
    # Student rows are always uniformly spaced; header rows aren't.
    run = _uniform_run(y_lines, target_count=num_students + 1)
    if len(run) >= num_students + 1:
        student_ys = run
    else:
        # Fallback: take the last (num_students+1) lines
        student_ys = y_lines[-(num_students + 1):]

    x_lines = _detect_v_lines(binary, y0=student_ys[0], y1=student_ys[-1])
    if len(x_lines) < 2:
        # Try more permissive vertical detection
        x_lines = _detect_v_lines(binary, y0=student_ys[0], y1=student_ys[-1], min_frac=0.25)

    h_img, w_img = binary.shape
    if len(x_lines) >= 2:
        sig_x0 = x_lines[-2] + 3
        sig_x1 = x_lines[-1] - 3
    else:
        sig_x0 = int(w_img * 0.72)
        sig_x1 = int(w_img * 0.97)

    if sig_x1 - sig_x0 < 30:
        sig_x0 = int(w_img * 0.72)
        sig_x1 = int(w_img * 0.97)

    cells: list[np.ndarray] = []
    for i in range(num_students):
        y0 = student_ys[i] + 3
        y1 = student_ys[i + 1] - 3
        if y1 - y0 < 10:
            y1 = min(y0 + 10, binary.shape[0])
        cells.append(binary[y0:y1, sig_x0:sig_x1])
    return cells
