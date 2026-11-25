"""
Geometric displacement, lens breathing, and gravity warp distortion for Project NOIR.
"""
import math
import cv2
import numpy as np

_GRID_CACHE = {}


def _get_displacement_grid(h: int, w: int):
    key = (h, w)
    if key not in _GRID_CACHE:
        ys, xs = np.indices((h, w), dtype=np.float32)
        norm_x = (xs / (w * 0.5)) - 1.0
        norm_y = (ys / (h * 0.5)) - 1.0
        r = np.sqrt(norm_x**2 + norm_y**2)
        _GRID_CACHE[key] = (xs, ys, norm_x, norm_y, r)
    return _GRID_CACHE[key]


def apply_radial_pinch(frame: np.ndarray, strength: float = 0.15, cx: float = 0.5, cy: float = 0.5) -> np.ndarray:
    """Applies optical radial pinch/bulge towards a center point."""
    if abs(strength) < 0.001:
        return frame
    h, w = frame.shape[:2]
    xs, ys, norm_x, norm_y, r = _get_displacement_grid(h, w)

    # Shift center
    shifted_x = norm_x - (cx * 2.0 - 1.0)
    shifted_y = norm_y - (cy * 2.0 - 1.0)
    dist = np.sqrt(shifted_x**2 + shifted_y**2)

    factor = 1.0 + strength * (dist**2)
    map_x = ((shifted_x * factor + (cx * 2.0 - 1.0) + 1.0) * (w * 0.5)).astype(np.float32)
    map_y = ((shifted_y * factor + (cy * 2.0 - 1.0) + 1.0) * (h * 0.5)).astype(np.float32)

    return cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def apply_lens_breathing(frame: np.ndarray, t: float, amplitude: float = 0.03, freq: float = 0.5) -> np.ndarray:
    """Simulates organic camera lens breathing (dread respiration)."""
    if amplitude <= 0.0:
        return frame
    h, w = frame.shape[:2]
    scale = 1.0 + math.sin(t * freq * 2.0 * math.pi) * amplitude
    M = cv2.getRotationMatrix2D((w * 0.5, h * 0.5), 0, scale)
    return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def apply_gravity_warp(frame: np.ndarray, t: float, intensity: float = 0.3) -> np.ndarray:
    """Applies non-Euclidean gravitational downward wave distortion."""
    if intensity <= 0.0:
        return frame
    h, w = frame.shape[:2]
    xs, ys, _, _, _ = _get_displacement_grid(h, w)
    warp_y = ys + np.sin(xs / 32.0 + t * 5.0) * (intensity * 12.0)
    return cv2.remap(frame, xs, warp_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
