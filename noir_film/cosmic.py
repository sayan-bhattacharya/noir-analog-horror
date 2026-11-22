"""
Cosmic horror procedural generation for Project NOIR.
Star fields, void gradients, and the hypnotic 'After Midnight, Somewhere Else' optical spiral abyss with the tumbling falling man.
"""
import math
import cv2
import numpy as np

_ABYSS_GRID_CACHE = {}


def _get_abyss_grid(h: int, w: int):
    key = (h, w)
    if key not in _ABYSS_GRID_CACHE:
        cy, cx = h // 2, w // 2
        ys, xs = np.indices((h, w), dtype=np.float32)
        dx = xs - cx
        dy = ys - cy
        r = np.sqrt(dx**2 + dy**2)
        theta = np.arctan2(dy, dx)
        _ABYSS_GRID_CACHE[key] = (cx, cy, r, theta)
    return _ABYSS_GRID_CACHE[key]


def render_starfield(frame: np.ndarray, count: int = 150, seed: int = 1994) -> np.ndarray:
    """Renders faint, desolate cosmic star specks."""
    h, w = frame.shape[:2]
    rng = np.random.RandomState(seed)
    out = frame.copy()
    for _ in range(count):
        sx = rng.randint(0, w)
        sy = rng.randint(0, int(h * 0.75))
        brightness = rng.randint(90, 210)
        out[sy, sx] = [brightness, brightness, int(brightness * 0.85)]
    return out


def draw_after_midnight_abyss(frame: np.ndarray, t: float, sub_bass: float = 0.1, arms: int = 6, twist: float = 0.088) -> np.ndarray:
    """
    Renders the hypnotic 'After Midnight, Somewhere Else' spinning optical illusion spiral abyss
    with the silhouette of the man tumbling and falling into the endless vortex.
    """
    h, w = frame.shape[:2]
    cx, cy, r, theta = _get_abyss_grid(h, w)

    # Hypnotic spiral mathematics
    speed = 2.8 + 1.6 * sub_bass
    spiral_phase = arms * theta + twist * np.sqrt(r) * 16.0 - t * speed
    val = np.sin(spiral_phase)

    bone_white = np.array([220, 214, 202], dtype=np.uint8)
    deep_void = np.array([12, 10, 16], dtype=np.uint8)

    mask = (val > 0).astype(np.float32)[:, :, None]
    core_void = np.clip((r - 28.0) / 250.0, 0.0, 1.0)
    outer_vignette = np.clip(1.25 - r / (w * 0.58), 0.0, 1.0)
    depth_falloff = (core_void * outer_vignette)[:, :, None]

    base_spiral = (mask * bone_white + (1.0 - mask) * deep_void) * depth_falloff
    frame[:] = np.clip(base_spiral, 0, 255).astype(np.uint8)

    # Vector tumbling falling man in free-fall vertigo
    def draw_tumbler(canvas, px, py, angle_rad, scale, alpha=1.0):
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        def tf(lx, ly):
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            return int(px + rx * scale), int(py + ry * scale)

        col = (int(8 * alpha), int(6 * alpha), int(10 * alpha))
        target = canvas if alpha >= 0.99 else canvas.copy()

        # Head & Torso
        cv2.circle(target, tf(0, -32), int(11 * scale), col, -1, cv2.LINE_AA)
        cv2.line(target, tf(0, -20), tf(0, 18), col, int(15 * scale), cv2.LINE_AA)

        # Arms in freefall flail
        cv2.line(target, tf(-6, -18), tf(-24, -36), col, int(6 * scale), cv2.LINE_AA)
        cv2.line(target, tf(-24, -36), tf(-38, -52), col, int(5 * scale), cv2.LINE_AA)
        cv2.line(target, tf(6, -18), tf(26, -26), col, int(6 * scale), cv2.LINE_AA)
        cv2.line(target, tf(26, -26), tf(42, -38), col, int(5 * scale), cv2.LINE_AA)

        # Legs kicking / curled
        cv2.line(target, tf(-5, 16), tf(-18, 48), col, int(7 * scale), cv2.LINE_AA)
        cv2.line(target, tf(-18, 48), tf(-30, 76), col, int(6 * scale), cv2.LINE_AA)
        cv2.line(target, tf(5, 16), tf(20, 42), col, int(7 * scale), cv2.LINE_AA)
        cv2.line(target, tf(20, 42), tf(36, 68), col, int(6 * scale), cv2.LINE_AA)

        if alpha < 0.99:
            cv2.addWeighted(target, alpha, canvas, 1.0 - alpha, 0, canvas)

    tumble_ang = t * 2.1
    drift_radius = 85.0 * (0.75 + 0.25 * math.sin(t * 1.1))
    man_x = int(cx + math.cos(t * 0.95) * drift_radius)
    man_y = int(cy + math.sin(t * 0.95) * drift_radius * 0.68)
    man_scale = 1.0 + 0.20 * math.sin(t * 1.5)

    # Ghost vertigo echo trails
    draw_tumbler(frame,
                 int(cx + math.cos((t - 0.25) * 0.95) * (drift_radius + 20)),
                 int(cy + math.sin((t - 0.25) * 0.95) * (drift_radius + 20) * 0.68),
                 (t - 0.25) * 2.1, man_scale * 1.25, alpha=0.30)
    draw_tumbler(frame,
                 int(cx + math.cos((t - 0.12) * 0.95) * (drift_radius + 10)),
                 int(cy + math.sin((t - 0.12) * 0.95) * (drift_radius + 10) * 0.68),
                 (t - 0.12) * 2.1, man_scale * 1.12, alpha=0.55)
    draw_tumbler(frame, man_x, man_y, tumble_ang, man_scale, alpha=1.0)
    return frame

# Backward compatibility alias
draw_twilight_zone_abyss = draw_after_midnight_abyss
