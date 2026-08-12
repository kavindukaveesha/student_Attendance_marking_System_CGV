"""Smoke tests for the feature modules.

Real end-to-end pipeline runs need actual signing sheet images in data/signing_sheets/;
these tests exercise the pure-Python image utilities on synthetic input.
"""
import numpy as np

from backend.features.image_processing import service as ip
from backend.features.signature_detection import service as sd
from backend.features.table_extraction import service as te
from backend.features.transforms import service as tf


def _blank(shape=(200, 300), value=255):
    return np.full(shape, value, dtype=np.uint8)


def test_greyscale_passthrough_for_gray_input():
    gray = _blank()
    assert ip.to_greyscale(gray).ndim == 2


def test_denoise_preserves_shape():
    gray = _blank()
    assert ip.denoise(gray, ksize=5).shape == gray.shape


def test_resize_normalises_dimensions():
    gray = _blank(shape=(500, 800))
    resized = tf.normalize_size(gray, size=(1000, 1400))
    assert resized.shape == (1400, 1000)


def test_ink_ratio_zero_for_blank_cell():
    binary = np.zeros((50, 50), dtype=np.uint8)
    assert sd.ink_ratio(binary) == 0.0
    assert sd.is_signed(binary, threshold=0.02) is False


def test_ink_ratio_high_for_filled_cell():
    binary = np.full((50, 50), 255, dtype=np.uint8)
    assert sd.ink_ratio(binary) == 1.0
    assert sd.is_signed(binary, threshold=0.02) is True


def test_binarize_returns_two_values():
    gray = np.random.randint(0, 256, size=(100, 100), dtype=np.uint8)
    binary = te.binarize(gray)
    unique = set(np.unique(binary).tolist())
    assert unique.issubset({0, 255})
