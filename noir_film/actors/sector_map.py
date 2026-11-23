"""
Emergency Sector Radar Map Actor for Project NOIR / Nishidak.
Matches user reference Image 2:
- High-contrast CRT vector map of West Bengal / Nistobdhopur sector
- Glowing crimson emergency header: 'EMERGENCY SECTOR BROADCAST'
- Vector road network, river curves, and district borders
- High-intensity horizontal red/white glitch tear streaks scanning across
- Pulsing hazard target over Nistobdhopur coordinates (22.98° N, 87.85° E)
"""
import math
import cv2
import numpy as np
from .. import text_overlay


def draw_sector_radar_map(frame: np.ndarray, t: float, sub_bass: float = 0.1) -> np.ndarray:
    """Renders the glowing red-and-black emergency CRT sector radar map."""
    h, w = frame.shape[:2]
    frame[:, :] = [10, 8, 14]

    # CRT vignette background
    cx, cy = w // 2, h // 2

    # 1. Glowing Emergency Header
    header_y = int(h * 0.12)
    text_overlay.draw_text(
        frame, "EMERGENCY SECTOR BROADCAST",
        (int(w * 0.08), header_y),
        font_size=int(h * 0.055),
        fill_color=(245, 45, 45),
        anchor="lm"
    )
    # Bengali sub-header
    text_overlay.draw_text(
        frame, "জরুরি অধিক্ষেত্র মানচিত্র — পশ্চিমবঙ্গ সেক্টর",
        (int(w * 0.08), header_y + int(h * 0.05)),
        font_size=int(h * 0.030),
        fill_color=(235, 120, 120),
        anchor="lm"
    )

    # 2. Vector District Border Lines & Rivers
    pts_border = [
        (int(w * 0.15), int(h * 0.30)),
        (int(w * 0.32), int(h * 0.26)),
        (int(w * 0.44), int(h * 0.38)),
        (int(w * 0.52), int(h * 0.52)),
        (int(w * 0.48), int(h * 0.72)),
        (int(w * 0.30), int(h * 0.85)),
        (int(w * 0.18), int(h * 0.70)),
        (int(w * 0.15), int(h * 0.30))
    ]
    cv2.polylines(frame, [np.array(pts_border, np.int32)], True, (80, 180, 210), 1, cv2.LINE_AA)

    # Winding river (Hooghly / Damodar vector curve)
    pts_river = []
    for step_y in range(int(h * 0.22), int(h * 0.90), 8):
        step_x = int(w * 0.58 + math.sin(step_y * 0.025) * 35 - (step_y - h * 0.22) * 0.15)
        pts_river.append((step_x, step_y))
    cv2.polylines(frame, [np.array(pts_river, np.int32)], False, (140, 210, 240), 2, cv2.LINE_AA)

    # Highway grid lines
    rng = np.random.RandomState(42)
    for _ in range(14):
        x1 = rng.randint(int(w * 0.25), int(w * 0.85))
        y1 = rng.randint(int(h * 0.30), int(h * 0.85))
        x2 = rng.randint(int(w * 0.25), int(w * 0.85))
        y2 = rng.randint(int(h * 0.30), int(h * 0.85))
        cv2.line(frame, (x1, y1), (x2, y2), (65, 85, 110), 1, cv2.LINE_AA)

    # 3. Flashing Hazard Target at Nistobdhopur
    target_x = int(w * 0.52)
    target_y = int(h * 0.58)
    pulse = 1.0 + 0.3 * math.sin(t * 8.0)
    target_r = int(22 * pulse)

    # Concentric target circles
    cv2.circle(frame, (target_x, target_y), target_r, (245, 50, 50), 2, cv2.LINE_AA)
    cv2.circle(frame, (target_x, target_y), int(target_r * 0.5), (245, 200, 50), 1, cv2.LINE_AA)
    cv2.circle(frame, (target_x, target_y), 3, (255, 255, 255), -1, cv2.LINE_AA)

    # Crosshairs
    cv2.line(frame, (target_x - target_r - 8, target_y), (target_x + target_r + 8, target_y), (245, 60, 60), 1, cv2.LINE_AA)
    cv2.line(frame, (target_x, target_y - target_r - 8), (target_x, target_y + target_r + 8), (245, 60, 60), 1, cv2.LINE_AA)

    text_overlay.draw_text(
        frame, "NISTOBDHOPUR (EPICENTER)",
        (target_x + target_r + 12, target_y - 6),
        font_size=int(h * 0.028),
        fill_color=(255, 80, 80),
        anchor="lm"
    )
    text_overlay.draw_text(
        frame, "22.9868° N, 87.8550° E • SECTOR R-04",
        (target_x + target_r + 12, target_y + 12),
        font_size=int(h * 0.020),
        fill_color=(200, 220, 200),
        anchor="lm"
    )

    # 4. Intense Horizontal Red/Cyan Glitch Tears (Matching Image 2)
    glitch_rng = np.random.RandomState(int(t * 24.0))
    tear_count = glitch_rng.randint(6, 14)
    for _ in range(tear_count):
        ty = glitch_rng.randint(int(h * 0.20), int(h * 0.90))
        tx = glitch_rng.randint(int(w * 0.15), int(w * 0.70))
        tw = glitch_rng.randint(int(w * 0.15), int(w * 0.45))
        th = glitch_rng.randint(2, 6)

        color_streak = (245, 30, 40) if glitch_rng.rand() > 0.3 else (220, 240, 255)
        cv2.rectangle(frame, (tx, ty), (min(w, tx + tw), ty + th), color_streak, -1)

    # 5. Bottom Telemetry Bar
    bar_y = int(h * 0.88)
    cv2.rectangle(frame, (int(w * 0.08), bar_y), (int(w * 0.92), bar_y + int(h * 0.05)), (160, 20, 25), -1)
    text_overlay.draw_text(
        frame, "[ HAZARD LEVEL: OMEGA  •  ALL TELECOMMUNICATION LINES SEVERED  •  EVACUATION VOID ]",
        (w // 2, bar_y + int(h * 0.025)),
        font_size=int(h * 0.022),
        fill_color=(255, 255, 255),
        anchor="mm"
    )

    return frame
