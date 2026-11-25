"""
Emergency Sector Radar Map Actor for Project NOIR / Nishidak.
High-contrast, 100% human-readable CRT vector radar of West Bengal / Nistobdhopur sector.
"""
import math
import cv2
import numpy as np
from .. import text_overlay


def draw_sector_radar_map(frame: np.ndarray, t: float, sub_bass: float = 0.1) -> np.ndarray:
    """Renders the glowing red-and-black emergency CRT sector radar map with crisp readability."""
    h, w = frame.shape[:2]
    frame[:, :] = [10, 8, 14]

    # 1. Background Glitch Tears (drawn UNDER text so text is 100% readable)
    glitch_rng = np.random.RandomState(int(t * 16.0))
    tear_count = glitch_rng.randint(4, 9)
    for _ in range(tear_count):
        ty = glitch_rng.randint(int(h * 0.24), int(h * 0.82))
        tx = glitch_rng.randint(int(w * 0.10), int(w * 0.65))
        tw = glitch_rng.randint(int(w * 0.12), int(w * 0.35))
        th = glitch_rng.randint(2, 4)
        color_streak = (110, 20, 28) if glitch_rng.rand() > 0.3 else (75, 85, 105)
        cv2.rectangle(frame, (tx, ty), (min(w, tx + tw), ty + th), color_streak, -1)

    # 2. Vector District Border Lines & Rivers
    pts_border = [
        (int(w * 0.14), int(h * 0.30)),
        (int(w * 0.32), int(h * 0.26)),
        (int(w * 0.44), int(h * 0.38)),
        (int(w * 0.52), int(h * 0.52)),
        (int(w * 0.48), int(h * 0.72)),
        (int(w * 0.30), int(h * 0.82)),
        (int(w * 0.16), int(h * 0.70)),
        (int(w * 0.14), int(h * 0.30))
    ]
    cv2.polylines(frame, [np.array(pts_border, np.int32)], True, (80, 180, 210), 2, cv2.LINE_AA)

    pts_river = []
    for step_y in range(int(h * 0.24), int(h * 0.84), 8):
        step_x = int(w * 0.54 + math.sin(step_y * 0.025) * 32 - (step_y - h * 0.24) * 0.15)
        pts_river.append((step_x, step_y))
    cv2.polylines(frame, [np.array(pts_river, np.int32)], False, (140, 210, 240), 2, cv2.LINE_AA)

    rng = np.random.RandomState(42)
    for _ in range(12):
        x1 = rng.randint(int(w * 0.20), int(w * 0.80))
        y1 = rng.randint(int(h * 0.28), int(h * 0.80))
        x2 = rng.randint(int(w * 0.20), int(w * 0.80))
        y2 = rng.randint(int(h * 0.28), int(h * 0.80))
        cv2.line(frame, (x1, y1), (x2, y2), (55, 75, 100), 1, cv2.LINE_AA)

    # 3. Glowing Emergency Header (Top Banner with clean dark backing)
    cv2.rectangle(frame, (0, 0), (w, int(h * 0.21)), (12, 10, 16), -1)
    cv2.line(frame, (int(w * 0.06), int(h * 0.21)), (int(w * 0.94), int(h * 0.21)), (215, 45, 45), 2)

    text_overlay.draw_text(
        frame, "EMERGENCY SECTOR BROADCAST",
        (int(w * 0.06), int(h * 0.08)),
        font_size=int(h * 0.054),
        fill_color=(245, 65, 65),
        anchor="lm"
    )
    text_overlay.draw_text(
        frame, "জরুরি এলাকার ম্যাপ: পশ্চিমবঙ্গ সেক্টর",
        (int(w * 0.06), int(h * 0.155)),
        font_size=int(h * 0.032),
        fill_color=(240, 195, 195),
        anchor="lm"
    )

    # 4. Flashing Hazard Target at Nistobdhopur
    target_x = int(w * 0.46)
    target_y = int(h * 0.56)
    pulse = 1.0 + 0.25 * math.sin(t * 8.0) + sub_bass * 0.2
    target_r = int(24 * pulse)

    cv2.circle(frame, (target_x, target_y), target_r, (245, 50, 50), 2, cv2.LINE_AA)
    cv2.circle(frame, (target_x, target_y), int(target_r * 0.5), (245, 200, 50), 1, cv2.LINE_AA)
    cv2.circle(frame, (target_x, target_y), 4, (255, 255, 255), -1, cv2.LINE_AA)

    cv2.line(frame, (target_x - target_r - 10, target_y), (target_x + target_r + 10, target_y), (245, 60, 60), 1, cv2.LINE_AA)
    cv2.line(frame, (target_x, target_y - target_r - 10), (target_x, target_y + target_r + 10), (245, 60, 60), 1, cv2.LINE_AA)

    # High-readability dark card behind target coordinates so nothing collides
    card_x1 = target_x + 42
    card_y1 = target_y - 40
    card_x2 = min(w - int(w * 0.04), card_x1 + int(w * 0.42))
    card_y2 = target_y + 42
    cv2.rectangle(frame, (card_x1, card_y1), (card_x2, card_y2), (14, 12, 18), -1)
    cv2.rectangle(frame, (card_x1, card_y1), (card_x2, card_y2), (225, 55, 55), 1)

    text_overlay.draw_text(
        frame, "NISTOBDHOPUR (EPICENTER)",
        (card_x1 + 14, target_y - 16),
        font_size=int(h * 0.030),
        fill_color=(255, 95, 95),
        max_width=(card_x2 - card_x1 - 24),
        anchor="lm"
    )
    text_overlay.draw_text(
        frame, "22.9868° N, 87.8550° E • SECTOR R-04",
        (card_x1 + 14, target_y + 18),
        font_size=int(h * 0.022),
        fill_color=(215, 235, 215),
        max_width=(card_x2 - card_x1 - 24),
        anchor="lm"
    )

    # 5. Bottom Telemetry Bar
    bar_y = int(h * 0.87)
    bar_h = int(h * 0.065)
    cv2.rectangle(frame, (int(w * 0.06), bar_y), (int(w * 0.94), bar_y + bar_h), (165, 20, 25), -1)
    cv2.rectangle(frame, (int(w * 0.06), bar_y), (int(w * 0.94), bar_y + bar_h), (240, 240, 240), 1)
    text_overlay.draw_text(
        frame, "HAZARD LEVEL: OMEGA  •  ALL LINES SEVERED  •  DO NOT LEAVE HOME",
        (w // 2, bar_y + bar_h // 2),
        font_size=int(h * 0.025),
        fill_color=(255, 255, 255),
        max_width=int(w * 0.84),
        anchor="mm"
    )

    return frame
