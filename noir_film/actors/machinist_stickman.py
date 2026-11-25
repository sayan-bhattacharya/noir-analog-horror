"""
Minimalist Animated Character Actor — 'Atandra / The Machinist' Stick-Man Figure.
Emaciated, gaunt, Christian Bale (The Machinist) inspired minimalist 2D stick-man
silhouette with hunched shoulders, subtle ribcage lines, and hollow pale eyes.
"""
import math
import cv2
import numpy as np


def draw_machinist_stickman(frame: np.ndarray,
                            cx: int,
                            cy: int,
                            t: float,
                            scale: float = 1.0,
                            walk_phase: float = 0.0,
                            is_alert: bool = False,
                            smoking: bool = False) -> np.ndarray:
    """
    Draws the minimalist gaunt stick-man figure (Atandra / Machinist silhouette)
    standing or creeping near the tube-well / courtyard.
    """
    s = scale
    # Subtle jerky analog animation (12fps stepped tremble)
    step_t = int(t * 12.0) / 12.0
    tremble_x = int(math.sin(step_t * 19.0) * 2.0 * s)
    tremble_y = int(math.cos(step_t * 15.0) * 1.5 * s)

    bx = cx + tremble_x
    by = cy + tremble_y

    ink = (10, 10, 14)
    rim = (140, 150, 165) if not is_alert else (235, 70, 70)

    # Hunched gaunt posture
    neck_x = bx + int(6 * s)
    neck_y = by - int(72 * s)
    hip_x = bx
    hip_y = by - int(18 * s)

    # Gaunt head (slightly tilted, sunken cheek silhouette)
    head_cx = neck_x + int(5 * s)
    head_cy = neck_y - int(16 * s)
    cv2.ellipse(frame, (head_cx, head_cy), (max(3, int(11 * s)), max(4, int(14 * s))),
                12, 0, 360, ink, -1, cv2.LINE_AA)
    cv2.ellipse(frame, (head_cx, head_cy), (max(3, int(11 * s)), max(4, int(14 * s))),
                12, 0, 360, rim, 1, cv2.LINE_AA)

    # Hollow Machinist eyes
    eye_col = (245, 75, 75) if is_alert else (210, 220, 225)
    cv2.circle(frame, (head_cx + int(3 * s), head_cy - int(2 * s)), max(1, int(2 * s)), eye_col, -1, cv2.LINE_AA)
    cv2.circle(frame, (head_cx - int(3 * s), head_cy - int(1 * s)), max(1, int(1.5 * s)), eye_col, -1, cv2.LINE_AA)

    # Curved emaciated spine & thin ribcage strokes
    spine_mid_x = bx - int(4 * s)
    spine_mid_y = (neck_y + hip_y) // 2
    pts_spine = np.array([[neck_x, neck_y], [spine_mid_x, spine_mid_y], [hip_x, hip_y]], np.int32)
    cv2.polylines(frame, [pts_spine], False, ink, max(2, int(6 * s)), cv2.LINE_AA)
    cv2.polylines(frame, [pts_spine], False, rim, 1, cv2.LINE_AA)

    # Minimalist rib notches (Machinist skeletal detail)
    for r_i in range(3):
        ry = neck_y + int((14 + r_i * 10) * s)
        rx = neck_x - int((2 + r_i * 2) * s)
        cv2.line(frame, (rx - int(8 * s), ry), (rx + int(7 * s), ry + int(2 * s)), rim, 1, cv2.LINE_AA)

    # Long gaunt dangling stick-arms
    sway = math.sin(step_t * 2.4 + walk_phase) * 8.0 * s
    # Left arm
    l_elbow = (neck_x - int(14 * s), neck_y + int(24 * s))
    l_hand = (neck_x - int(18 * s - sway * 0.5), neck_y + int(52 * s))
    cv2.line(frame, (neck_x, neck_y + int(4 * s)), l_elbow, ink, max(2, int(4 * s)), cv2.LINE_AA)
    cv2.line(frame, l_elbow, l_hand, ink, max(1, int(3 * s)), cv2.LINE_AA)

    # Right arm (reaching/twitching or raising cigarette to mouth)
    if smoking:
        puff_cycle = 0.5 + 0.5 * math.sin(t * 2.2)
        r_elbow = (neck_x + int(15 * s), neck_y + int(16 * s - puff_cycle * 8 * s))
        r_hand = (head_cx + int((14 - puff_cycle * 6) * s), head_cy + int((14 - puff_cycle * 10) * s))
    else:
        r_elbow = (neck_x + int(16 * s), neck_y + int(20 * s))
        r_hand = (neck_x + int(22 * s + sway * 0.6), neck_y + int(48 * s))
    cv2.line(frame, (neck_x, neck_y + int(4 * s)), r_elbow, ink, max(2, int(4 * s)), cv2.LINE_AA)
    cv2.line(frame, r_elbow, r_hand, ink, max(1, int(3 * s)), cv2.LINE_AA)

    if smoking:
        # Lit cigarette + glowing orange ember + rising smoke wisps
        cig_tip = (r_hand[0] + int(12 * s), r_hand[1] - int(3 * s))
        cv2.line(frame, r_hand, cig_tip, (230, 230, 225), max(1, int(2 * s)), cv2.LINE_AA)
        ember_pulse = 0.65 + 0.35 * math.sin(t * 9.0)
        cv2.circle(frame, cig_tip, max(2, int(3 * s)), (int(255 * ember_pulse), int(95 * ember_pulse), 20), -1, cv2.LINE_AA)
        smoke_overlay = frame.copy()
        for k in range(5):
            age = ((t * 1.4 + k * 0.28) % 1.4) / 1.4
            sx = int(cig_tip[0] + math.sin(t * 3.0 + k) * (10 + age * 16) * s)
            sy = int(cig_tip[1] - (8 + age * 54) * s)
            sr = max(2, int((3 + age * 11) * s))
            cv2.circle(smoke_overlay, (sx, sy), sr, (185, 190, 195), -1, cv2.LINE_AA)
        cv2.addWeighted(smoke_overlay, 0.28, frame, 0.72, 0, frame)

    # Thin stick legs
    stride = math.sin(walk_phase) * 10.0 * s
    l_knee = (hip_x - int(8 * s + stride * 0.4), hip_y + int(24 * s))
    l_foot = (hip_x - int(10 * s + stride), by + int(28 * s))
    cv2.line(frame, (hip_x, hip_y), l_knee, ink, max(2, int(4 * s)), cv2.LINE_AA)
    cv2.line(frame, l_knee, l_foot, ink, max(1, int(3 * s)), cv2.LINE_AA)

    r_knee = (hip_x + int(8 * s - stride * 0.4), hip_y + int(24 * s))
    r_foot = (hip_x + int(10 * s - stride), by + int(28 * s))
    cv2.line(frame, (hip_x, hip_y), r_knee, ink, max(2, int(4 * s)), cv2.LINE_AA)
    cv2.line(frame, r_knee, r_foot, ink, max(1, int(3 * s)), cv2.LINE_AA)

    return frame
