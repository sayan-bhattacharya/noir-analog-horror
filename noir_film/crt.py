"""
1994 Doordarshan CRT glass post-processing pipeline for Project NOIR.
Includes barrel distortion, scanlines, phosphor glow, chromatic aberration, vignette, and head switching.
"""
import math
import cv2
import numpy as np

_CRT_CACHE = {}


def _get_crt_grid(h: int, w: int):
    key = (h, w)
    if key not in _CRT_CACHE:
        ys, xs = np.indices((h, w), dtype=np.float32)
        norm_x = (xs / (w * 0.5)) - 1.0
        norm_y = (ys / (h * 0.5)) - 1.0
        r2 = norm_x**2 + norm_y**2
        _CRT_CACHE[key] = (xs, ys, norm_x, norm_y, r2)
    return _CRT_CACHE[key]


def apply_crt(frame: np.ndarray,
              curvature: float = 0.08,
              scanline_strength: float = 0.22,
              vignette_strength: float = 0.35,
              chromatic_aberration_px: float = 2.0,
              head_switching_px: int = 24,
              sub_bass: float = 0.0,
              t: float = 0.0) -> np.ndarray:
    """
    Applies the authentic 1994 Indian CRT television post-processing pipeline.
    """
    h, w = frame.shape[:2]
    xs, ys, norm_x, norm_y, r2 = _get_crt_grid(h, w)

    # 1. Curved Glass Barrel Distortion
    distort = 1.0 + (curvature + sub_bass * 0.02) * r2
    map_x = ((norm_x * distort + 1.0) * (w * 0.5)).astype(np.float32)
    map_y = ((norm_y * distort + 1.0) * (h * 0.5)).astype(np.float32)
    curved = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    curved = curved.astype(np.float32)

    # 2. Chromatic Aberration (Phosphor Convergence Error)
    shift = int(chromatic_aberration_px + sub_bass * 3.0)
    if shift > 0:
        red = np.roll(curved[:, :, 0], -shift, axis=1)
        blue = np.roll(curved[:, :, 2], shift, axis=1)
        curved[:, :, 0] = red
        curved[:, :, 2] = blue

    # 3. Horizontal Cathode Ray Scanlines
    scanlines = np.ones((h, 1, 1), dtype=np.float32)
    scanlines[::2] *= (1.0 - scanline_strength)
    curved *= scanlines

    # 4. Corner Vignette & Phosphor Falloff
    falloff = np.clip(1.0 - vignette_strength * (r2 ** 1.4), 0.0, 1.0)[:, :, None]
    curved *= falloff

    # 5. Bottom VCR Head-Switching Noise Band
    out = np.clip(curved, 0, 255).astype(np.uint8)
    if head_switching_px > 0:
        band_h = min(h, head_switching_px + int(math.sin(t * 3.7) * 4))
        y_start = h - band_h
        band = out[y_start:h, :]
        shift_px = int(math.sin(t * 17.0) * 14.0 + np.random.uniform(-6, 6))
        shifted_band = np.roll(band, shift_px, axis=1)
        snow = np.random.uniform(0, 100, band.shape).astype(np.float32)
        out[y_start:h, :] = np.clip(shifted_band.astype(np.float32) * 0.5 + snow * 0.5, 0, 255).astype(np.uint8)

    return out
