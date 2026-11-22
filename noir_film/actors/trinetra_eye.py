"""
The Colossal Celestial Third Eye (Trinetra / ত্রিনেত্র) Actor for Project NOIR.
Delta river-branching red capillaries, pulsing pupil dilation, and cosmic void aperture.
"""
import math
import cv2
import numpy as np


def draw_trinetra_eye(frame: np.ndarray,
                      cx: int,
                      cy: int,
                      t: float,
                      scale: float = 1.0,
                      pupil_radius_base: int = 35,
                      dilation_extra: float = 0.0) -> np.ndarray:
    """Renders the colossal third-eye aperture in the void."""
    # Outer bruised eyelid shape
    eye_w = int(240 * scale)
    eye_h = int(120 * scale)
    sclera_col = (215, 205, 195)

    # Sclera base
    cv2.ellipse(frame, (cx, cy), (eye_w, eye_h), 0, 0, 360, sclera_col, -1, cv2.LINE_AA)

    # River delta capillary branching in sclera
    rng = np.random.RandomState(42)
    capillary_col = (30, 20, 185)  # Crimson
    for branch_i in range(16):
        ang = branch_i * (2.0 * math.pi / 16.0)
        px, py = cx, cy
        dist_step = (eye_w * 0.75) / 5.0
        for step in range(5):
            nx = int(px + math.cos(ang) * dist_step + rng.randint(-8, 9))
            ny = int(py + math.sin(ang) * (dist_step * 0.45) + rng.randint(-4, 5))
            cv2.line(frame, (px, py), (nx, ny), capillary_col, 1, cv2.LINE_AA)
            px, py = nx, ny

    # Iris
    iris_r = int(70 * scale)
    iris_col = (35, 15, 120)  # Deep cosmic purple
    cv2.circle(frame, (cx, cy), iris_r, iris_col, -1, cv2.LINE_AA)

    # Sub-bass pulsating pupil
    effective_pupil_r = int((pupil_radius_base + dilation_extra * 45.0) * scale)
    cv2.circle(frame, (cx, cy), effective_pupil_r, (4, 4, 6), -1, cv2.LINE_AA)

    # Inner eye reflection highlight
    cv2.circle(frame, (cx - int(12 * scale), cy - int(12 * scale)), int(6 * scale), (245, 240, 230), -1, cv2.LINE_AA)

    # Eyelid borders
    cv2.ellipse(frame, (cx, cy), (eye_w, eye_h), 0, 0, 360, (15, 12, 18), int(4 * scale), cv2.LINE_AA)

    return frame
