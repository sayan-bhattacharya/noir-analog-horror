"""Bilingual civil-danger interruption with legible banded CRT graphics."""
import math
import cv2
import numpy as np
from .. import text_overlay


def draw_civil_danger_screen(frame: np.ndarray, t: float, sub_bass: float = 0.1) -> np.ndarray:
    """Draw a blue checkered broadcast card with Bengali as the primary language."""
    h, w = frame.shape[:2]
    pulse = 1.0 + 0.025 * math.sin(t * 7.5) + 0.035 * sub_bass
    base = np.array([18, 13, 66], dtype=np.float32)  # BGR: deep broadcast blue
    frame[:] = np.clip(base * pulse, 0, 255).astype(np.uint8)

    # Low-contrast checker texture; solid inset strips keep all copy readable.
    cell = max(28, int(h * 0.075))
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if ((x // cell) + (y // cell)) % 2 == 0:
                cv2.rectangle(frame, (x, y), (min(w - 1, x + cell - 1), min(h - 1, y + cell - 1)), (24, 20, 88), -1)
    cv2.rectangle(frame, (int(w * .055), int(h * .09)), (int(w * .945), int(h * .91)), (7, 9, 42), 2, cv2.LINE_AA)

    bands = [(.18, .36), (.40, .58), (.62, .80)]
    for y1, y2 in bands:
        p1, p2 = (int(w * .09), int(h * y1)), (int(w * .91), int(h * y2))
        cv2.rectangle(frame, p1, p2, (16, 23, 106), -1)
        cv2.rectangle(frame, p1, p2, (150, 188, 237), 1, cv2.LINE_AA)
        cv2.line(frame, (p1[0] + 7, p1[1] + 5), (p2[0] - 7, p1[1] + 5), (67, 91, 162), 1, cv2.LINE_AA)

    # Bengali leads in scale and placement; English stays as a concise secondary caption.
    lines = [
        ("নাগরিক বিপদ সতর্কতা", "CIVIL DANGER WARNING"),
        ("পর্দার দিকে তাকাবেন না", "DO NOT LOOK AT THE SCREEN"),
        ("ডাকের উত্তর দেবেন না", "DO NOT ANSWER THE CALLING"),
    ]
    for (bn, en), (y1, y2) in zip(lines, bands):
        mid = int(h * (y1 + y2) * .5)
        text_overlay.draw_text(frame, bn, (w // 2, mid - int(h * .024)),
                               font_size=int(h * .052), fill_color=(255, 250, 231), anchor="mm",
                               max_width=int(w * .78), with_shadow=True)
        text_overlay.draw_text(frame, en, (w // 2, mid + int(h * .040)),
                               font_size=int(h * .022), fill_color=(209, 223, 255), anchor="mm",
                               max_width=int(w * .78), with_shadow=False)

    text_overlay.draw_text(frame, "EAN / WEST BENGAL  ·  TRANSMISSION SEVERED",
                           (w // 2, int(h * .86)), font_size=int(h * .021),
                           fill_color=(218, 226, 250), anchor="mm", with_shadow=False)
    return frame
