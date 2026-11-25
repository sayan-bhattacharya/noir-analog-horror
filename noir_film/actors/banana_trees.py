"""
Procedural Rural Bengal Banana Trees & Creaking Handpump Actor for Project NOIR.
"""
import math
import cv2
import numpy as np


def draw_banana_tree(frame: np.ndarray, cx: int, cy: int, t: float, scale: float = 1.0, wind_strength: float = 0.65):
    """Renders silhouetted organic banana plant with broad ragged curved leaves."""
    color = (12, 10, 16)
    trunk_w = int(18 * scale)
    trunk_h = int(190 * scale)
    cv2.rectangle(frame, (cx - trunk_w // 2, cy - trunk_h), (cx + trunk_w // 2, cy), color, -1)

    top_y = cy - trunk_h
    fronds = [(-65, 160, 0.3), (-35, 200, 0.8), (10, 190, 0.4), (50, 180, 0.9), (80, 140, 0.2)]
    for angle_deg, length, wind_phase in fronds:
        sway = math.sin(t * 1.5 * wind_strength + wind_phase) * (8.0 * wind_strength)
        rad = math.radians(angle_deg + sway)
        end_x = int(cx + math.sin(rad) * length * scale)
        end_y = int(top_y - math.cos(rad) * length * scale * 0.45 + (length * 0.35 * scale))

        ctrl_x = int((cx + end_x) * 0.5 + (20 if angle_deg > 0 else -20) * scale)
        ctrl_y = int(top_y - 45 * scale)

        leaf_pts = [
            [cx, top_y],
            [ctrl_x - int(18 * scale), ctrl_y],
            [end_x, end_y],
            [ctrl_x + int(18 * scale), ctrl_y + int(10 * scale)]
        ]
        cv2.fillPoly(frame, [np.array(leaf_pts, np.int32)], color)


def draw_creaking_handpump(frame: np.ndarray, cx: int, cy: int, t: float, scale: float = 1.0, drip_interval: float = 1.2):
    """Renders rural cast-iron handpump with self-moving handle and dark water drip."""
    color = (12, 10, 16)
    # Pump cylinder
    cv2.rectangle(frame, (cx - int(10 * scale), cy - int(95 * scale)),
                  (cx + int(10 * scale), cy), color, -1)
    # Moving handle
    handle_sway = int(math.sin(t * (2.0 * math.pi / drip_interval)) * 8 * scale)
    cv2.line(frame, (cx, cy - int(80 * scale)),
             (cx - int(60 * scale), cy - int(55 * scale) + handle_sway), color, int(4 * scale), cv2.LINE_AA)
    # Spout
    spout_end = (cx + int(32 * scale), cy - int(45 * scale))
    cv2.line(frame, (cx, cy - int(45 * scale)), spout_end, color, int(4 * scale), cv2.LINE_AA)

    # Thick black water drip into red earth
    drip_phase = (t % drip_interval) / drip_interval
    drip_y = int(spout_end[1] + drip_phase * 45 * scale)
    cv2.circle(frame, (spout_end[0], drip_y), int(3 * scale), (8, 6, 12), -1)
