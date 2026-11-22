"""
Procedural noise, dust, scratches, and static snow shaders for Project NOIR.
Pure NumPy and OpenCV implementation for deterministic reproducibility.
"""
import math
import cv2
import numpy as np


def apply_static_snow(frame: np.ndarray, amount: float = 0.12, seed: int = None) -> np.ndarray:
    """Adds analog antenna static snow."""
    if amount <= 0.0:
        return frame
    rng = np.random.RandomState(seed) if seed is not None else np.random
    h, w, c = frame.shape
    noise = rng.normal(0, 32.0 * amount, (h, w, c)).astype(np.float32)
    return np.clip(frame.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def apply_film_dust_and_scratches(frame: np.ndarray, t: float, scratch_prob: float = 0.4, dust_count: int = 10) -> np.ndarray:
    """Adds archival nitrate vertical film scratches and dust specks."""
    h, w = frame.shape[:2]
    out = frame.copy()

    # Vertical scratches
    seed = int(t * 18.0)
    rng = np.random.RandomState(seed)

    if rng.uniform(0, 1) < scratch_prob:
        num_scratches = rng.randint(1, 3)
        for _ in range(num_scratches):
            sx = rng.randint(20, w - 20)
            drift = rng.randint(-2, 3)
            col = (rng.randint(60, 95), rng.randint(60, 95), rng.randint(60, 95))
            cv2.line(out, (sx, 0), (sx + drift, h), col, 1, cv2.LINE_AA)

    # Dust specks
    for _ in range(dust_count):
        dx = rng.randint(10, w - 10)
        dy = rng.randint(10, h - 10)
        dr = rng.randint(1, 3)
        col = (rng.randint(140, 190), rng.randint(140, 190), rng.randint(140, 190))
        cv2.circle(out, (dx, dy), dr, col, -1)

    return out


def apply_electromagnetic_interference(frame: np.ndarray, t: float, intensity: float = 0.2) -> np.ndarray:
    """Simulates high-voltage electromagnetic hum bands rolling across the raster."""
    if intensity <= 0.0:
        return frame
    h, w = frame.shape[:2]
    ys = np.arange(h, dtype=np.float32)[:, None, None]
    band = np.sin((ys / 45.0) - t * 4.0) * (intensity * 24.0)
    return np.clip(frame.astype(np.float32) + band, 0, 255).astype(np.uint8)
