"""
Real-time analog horror CRT and VHS shaders for PROJECT NOIR.
Pure NumPy and OpenCV implementation for 24/30/60 fps high throughput rendering.
"""
import math
import cv2
import numpy as np

# Cache coordinate grids for speed
_GRID_CACHE = {}


def _get_grid(h, w):
    key = (h, w)
    if key not in _GRID_CACHE:
        ys, xs = np.indices((h, w), dtype=np.float32)
        norm_x = (xs / (w * 0.5)) - 1.0
        norm_y = (ys / (h * 0.5)) - 1.0
        r2 = norm_x**2 + norm_y**2
        _GRID_CACHE[key] = (xs, ys, norm_x, norm_y, r2)
    return _GRID_CACHE[key]


def apply_crt(frame, curvature=0.08, scanline_intensity=0.22, vignette=0.85):
    """Simulates a vintage curved glass CRT screen with phosphor scanlines."""
    h, w = frame.shape[:2]
    xs, ys, norm_x, norm_y, r2 = _get_grid(h, w)

    # Barrel distortion for curved glass
    distort = 1.0 + curvature * r2
    map_x = ((norm_x * distort + 1.0) * (w * 0.5)).astype(np.float32)
    map_y = ((norm_y * distort + 1.0) * (h * 0.5)).astype(np.float32)

    curved = cv2.remap(frame, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))

    # CRT horizontal scanlines (alternating cathode beam intensity)
    scanlines = np.ones((h, 1, 1), dtype=np.float32)
    scanlines[::2] *= (1.0 - scanline_intensity)
    curved *= scanlines

    # Corner vignette
    corner_falloff = np.clip(1.0 - 0.35 * (r2 ** 1.5), 0.0, 1.0)
    curved *= corner_falloff[:, :, None]

    return np.clip(curved, 0, 255).astype(np.float32)


def apply_vhs_tracking(frame, t, tear_intensity=1.0, sub_bass=0.0):
    """
    Applies authentic VCR tape tracking errors:
      - Bottom head-switching noise band
      - Horizontal scanline jitter on sub-bass transients
      - Chromatic aberration (RGB shift)
    """
    h, w, c = frame.shape
    out = frame.copy()

    # 1. Chromatic aberration (Red left, Blue right)
    shift = int(2 + 4 * sub_bass)
    if shift > 0:
        red = np.roll(out[:, :, 0], -shift, axis=1)
        blue = np.roll(out[:, :, 2], shift, axis=1)
        out[:, :, 0] = red
        out[:, :, 2] = blue

    # 2. Bottom head-switching glitch (bottom 24 pixels)
    glitch_h = int(20 + 12 * math.sin(t * 3.7))
    y_start = max(0, h - glitch_h)
    band = out[y_start:h, :]
    shift_px = int(math.sin(t * 18.0) * 16.0 + np.random.uniform(-8, 8))
    out[y_start:h, :] = np.roll(band, shift_px, axis=1)
    # Add snow noise to the head switching band
    snow = np.random.uniform(0, 120, band.shape).astype(np.float32)
    out[y_start:h, :] = np.clip(out[y_start:h, :] * 0.5 + snow * 0.5, 0, 255)

    # 3. High-energy horizontal tape tear on sub-bass impact
    if sub_bass > 0.4:
        tear_y = int((math.sin(t * 7.3) * 0.5 + 0.5) * (h - 40))
        tear_len = int(12 + sub_bass * 28)
        tear_shift = int(np.random.choice([-1, 1]) * (8 + sub_bass * 30))
        out[tear_y:tear_y+tear_len] = np.roll(out[tear_y:tear_y+tear_len], tear_shift, axis=1)

    return out


def apply_white_noise(frame, amount=0.08, breathing=0.0):
    """Adds analog antenna static snow."""
    noise = np.random.normal(0, 18.0 * (1.0 + breathing), frame.shape).astype(np.float32)
    return np.clip(frame + noise * (amount / 0.08), 0, 255)


def draw_vcr_osd(frame, t, channel="CH 03", message="PLAY"):
    """Renders authentic VCR green/cyan on-screen display text."""
    h, w = frame.shape[:2]
    # Timestamp calculation
    hours = int(t // 3600)
    mins = int((t % 3600) // 60)
    secs = int(t % 60)
    frames = int((t - int(t)) * 24)

    timestamp_str = f"MAY 14 1994  {hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}"
    osd_color = (65, 235, 125)  # Phosphor green

    # Top-left status
    cv2.putText(frame, f"{message} > SP", (48, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (10, 10, 10), 4, cv2.LINE_AA)
    cv2.putText(frame, f"{message} > SP", (48, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.85, osd_color, 2, cv2.LINE_AA)

    # Top-right channel
    cv2.putText(frame, channel, (w - 180, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (10, 10, 10), 4, cv2.LINE_AA)
    cv2.putText(frame, channel, (w - 180, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.85, osd_color, 2, cv2.LINE_AA)

    # Bottom-left date & time
    cv2.putText(frame, timestamp_str, (48, h - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (10, 10, 10), 4, cv2.LINE_AA)
    cv2.putText(frame, timestamp_str, (48, h - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.75, osd_color, 2, cv2.LINE_AA)

    # Blinking REC dot
    if int(t * 2) % 2 == 0:
        cv2.circle(frame, (w - 70, h - 52), 8, (40, 40, 240), -1, cv2.LINE_AA)
        cv2.putText(frame, "REC", (w - 130, h - 46), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (40, 40, 240), 2, cv2.LINE_AA)
