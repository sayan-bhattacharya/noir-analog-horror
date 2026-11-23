"""
Civil Danger Warning Screen Actor for Project NOIR / Nishidak.
Matches user reference Image 3:
- Saturated blood-red CRT screen with phosphor scanlines and horizontal retrace lines
- Stark, chilling Emergency Action Notification (EAS / civil defense) text centered:
    CIVIL DANGER WARNING:
    DO NOT LOOK AT THE SCREEN
    DO NOT ANSWER THE CALLING
- Bilingual Bengali typography:
    নাগরিক বিপদ সতর্কতা:
    টিভির পর্দায় তাকাবেন না
- Subtle CRT phosphor breathing, scanline tear, and VCR distortion
"""
import math
import cv2
import numpy as np
from .. import text_overlay


def draw_civil_danger_screen(frame: np.ndarray, t: float, sub_bass: float = 0.1) -> np.ndarray:
    """Renders the stark saturated red civil danger warning screen."""
    h, w = frame.shape[:2]

    # Blood-red CRT raster with subtle flicker
    flicker = 1.0 + 0.04 * math.sin(t * 40.0) + 0.08 * sub_bass
    r_val = int(np.clip(185 * flicker, 160, 245))
    g_val = int(np.clip(16 * flicker, 10, 30))
    b_val = int(np.clip(18 * flicker, 12, 35))
    frame[:, :] = [b_val, g_val, r_val]

    # Horizontal CRT Retrace Grid Lines (Matching Image 3)
    retrace_spacing = max(18, int(h * 0.075))
    for y_retrace in range(int(h * 0.15), int(h * 0.85), retrace_spacing):
        cv2.line(frame, (int(w * 0.08), y_retrace), (int(w * 0.92), y_retrace), (240, 240, 245), 1, cv2.LINE_AA)

    # Vertical subtle sync grid line on left
    grid_x = int(w * 0.22)
    cv2.line(frame, (grid_x, int(h * 0.12)), (grid_x, int(h * 0.88)), (240, 240, 245), 1, cv2.LINE_AA)
    cv2.line(frame, (grid_x + 16, int(h * 0.12)), (grid_x + 16, int(h * 0.88)), (240, 240, 245), 1, cv2.LINE_AA)

    # Stark Monospaced Warning Text in English & Bengali
    center_y = int(h * 0.44)
    line_spacing = int(h * 0.068)

    warning_lines_en = [
        "CIVIL DANGER WARNING:",
        "DO NOT LOOK AT THE SCREEN",
        "DO NOT ANSWER THE CALLING"
    ]

    for idx, line in enumerate(warning_lines_en):
        y_pos = center_y - int(h * 0.10) + idx * line_spacing
        text_overlay.draw_text(
            frame, line,
            (w // 2, y_pos),
            font_size=int(h * 0.048),
            fill_color=(255, 255, 255),
            anchor="mm"
        )

    # Bengali civil warning text below
    ben_y1 = center_y + int(h * 0.16)
    ben_y2 = ben_y1 + int(h * 0.06)

    text_overlay.draw_text(
        frame, "নাগরিক বিপদ সতর্কতা:",
        (w // 2, ben_y1),
        font_size=int(h * 0.042),
        fill_color=(255, 245, 245),
        anchor="mm"
    )
    text_overlay.draw_text(
        frame, "টিভির পর্দায় তাকাবেন না, ঘরের দরজা বন্ধ রাখুন",
        (w // 2, ben_y2),
        font_size=int(h * 0.034),
        fill_color=(245, 220, 220),
        anchor="mm"
    )

    # Telemetry code at bottom
    text_overlay.draw_text(
        frame, "[ EAN / SECTOR WEST BENGAL  •  TRANSMISSION SEVERED ]",
        (w // 2, int(h * 0.88)),
        font_size=int(h * 0.022),
        fill_color=(255, 255, 255),
        anchor="mm"
    )

    return frame
