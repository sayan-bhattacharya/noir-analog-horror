"""
Night Sky Cloud Time-Lapse Engine for Project NOIR.
Renders continuous cinematic time-lapse cloud motion across the midnight moon.
Reusable across the 1:07 tube-well scene, 2:33 dedicated cloud time-lapse, and future projects.
"""
import math
import cv2
import numpy as np


def render_cloud_timelapse_sky(frame: np.ndarray,
                               t: float,
                               width: int = 1280,
                               height: int = 720,
                               moon_pos: tuple = None,
                               cloud_speed: float = 40.0,
                               density: float = 1.0) -> np.ndarray:
    """
    Renders full-frame or sky-region atmospheric cloud time-lapse:
    - Base deep indigo nocturnal sky with faint starfield.
    - Pale luminous moon with lunar halo.
    - 3 volumetric strata of moonlit clouds drifting at staggered parallax speeds.
    - Silver edge-illumination as clouds pass in front of the lunar disc.
    """
    if moon_pos is None:
        moon_cx = int(width * 0.72)
        moon_cy = int(height * 0.24)
    else:
        moon_cx, moon_cy = moon_pos

    moon_r = int(height * 0.052)

    # 1. Sky Gradient (Deep midnight indigo to dark horizon)
    sky = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        frac = y / float(height)
        r = int(6 + frac * 10)
        g = int(8 + frac * 14)
        b = int(18 + frac * 16)
        sky[y, :] = [b, g, r]

    # 2. Distant Starfield (twinkling gently)
    np.random.seed(1994)
    num_stars = 70
    star_x = np.random.randint(0, width, num_stars)
    star_y = np.random.randint(0, int(height * 0.55), num_stars)
    star_b = np.random.uniform(140, 240, num_stars)

    for i in range(num_stars):
        twinkle = 0.8 + 0.2 * math.sin(t * 4.0 + i)
        val = int(star_b[i] * twinkle)
        cv2.circle(sky, (star_x[i], star_y[i]), 1, (val, val, val), -1)

    # 3. Luminous Moon & Lunar Corona
    for r_glow, alpha in [(moon_r * 3.5, 0.06), (moon_r * 2.2, 0.14), (int(moon_r * 1.3), 0.26)]:
        overlay = sky.copy()
        cv2.circle(overlay, (moon_cx, moon_cy), int(r_glow), (210, 225, 235), -1)
        cv2.addWeighted(overlay, alpha, sky, 1.0 - alpha, 0, sky)

    cv2.circle(sky, (moon_cx, moon_cy), moon_r, (235, 240, 245), -1, cv2.LINE_AA)
    # Craters & Maria
    cv2.ellipse(sky, (moon_cx - int(moon_r * 0.22), moon_cy - int(moon_r * 0.12)),
                (int(moon_r * 0.36), int(moon_r * 0.26)), -20, 0, 360, (195, 200, 208), -1)
    cv2.ellipse(sky, (moon_cx + int(moon_r * 0.26), moon_cy + int(moon_r * 0.16)),
                (int(moon_r * 0.30), int(moon_r * 0.20)), 15, 0, 360, (200, 205, 212), -1)

    # 4. Volumetric Time-Lapse Cloud Layers
    cloud_overlay = sky.copy()

    layers = [
        # (layer_idx, speed_mult, y_base, opacity, puff_count, scale_w, scale_h)
        (1, 1.00, int(height * 0.20), 0.78 * density, 10, 160, 52),
        (2, 0.65, int(height * 0.28), 0.65 * density, 8, 200, 60),
        (3, 1.35, int(height * 0.12), 0.50 * density, 12, 130, 42)
    ]

    for layer_idx, speed_mult, y_base, opacity, p_count, pw_base, ph_base in layers:
        drift_x = (t * cloud_speed * speed_mult) % (width + 800) - 400
        for p in range(p_count):
            px = int(drift_x + p * (pw_base * 0.95))
            py = int(y_base + math.sin(t * 0.7 + p * 1.4) * 14)
            pw = int(pw_base + 30 * math.sin(p * 2.1))
            ph = int(ph_base + 12 * math.cos(p * 1.8))

            dist = math.hypot(px - moon_cx, py - moon_cy)
            if dist < moon_r * 2.6:
                # Silver-lined backlit edge
                col = (155, 165, 178)
            elif dist < moon_r * 4.0:
                col = (75, 82, 94)
            else:
                col = (18, 22, 28)

            cv2.ellipse(cloud_overlay, (px, py), (pw, ph), 0, 0, 360, col, -1)

    cv2.addWeighted(cloud_overlay, 0.68, sky, 0.32, 0, sky)

    # Blend sky into frame where frame is dark or as background
    if np.mean(frame) < 15:
        frame[:] = sky
    else:
        # Sky replaces upper 55% of the frame with soft blend to horizon
        mask_h = int(height * 0.55)
        for y in range(mask_h):
            alpha = max(0.0, 1.0 - (y / float(mask_h)) ** 2.0)
            frame[y, :] = cv2.addWeighted(sky[y, :], alpha, frame[y, :], 1.0 - alpha, 0)

    return frame
