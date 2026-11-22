"""
The Uncanny Black Tomcat (কালো হুলো বেড়াল) Actor for Project NOIR.
Perched on split-bamboo fence with an elastically extendable neck rising into monsoon clouds.
"""
import math
import cv2
import numpy as np


def draw_hulo_cat(frame: np.ndarray,
                  t: float,
                  cx: int = 980,
                  cy: int = 600,
                  stretch_factor: float = 0.0,
                  eye_color: tuple = (245, 225, 45),
                  scale: float = 1.0) -> np.ndarray:
    """Renders the black tomcat serving as the transmitting aperture."""
    color = (12, 10, 16)

    # Split-Bamboo Fence (বাঁশের বেড়া)
    for fx in range(cx - int(90 * scale), cx + int(110 * scale), int(30 * scale)):
        cv2.line(frame, (fx, cy), (fx, cy + int(140 * scale)), (45, 38, 28), int(5 * scale), cv2.LINE_AA)
    cv2.line(frame, (cx - int(100 * scale), cy + int(35 * scale)),
             (cx + int(120 * scale), cy + int(35 * scale)), (55, 45, 32), int(4 * scale), cv2.LINE_AA)
    cv2.line(frame, (cx - int(100 * scale), cy + int(85 * scale)),
             (cx + int(120 * scale), cy + int(85 * scale)), (55, 45, 32), int(4 * scale), cv2.LINE_AA)

    # Cat body on rail
    body_y = int(cy + 18 * scale)
    cv2.ellipse(frame, (cx, body_y), (int(24 * scale), int(16 * scale)), -8, 0, 360, color, -1)

    # Serpentine coiling tail
    tail_pts = []
    for i in range(14):
        tx = int(cx - 24 * scale - i * 3 * scale + math.sin(t * 4.5 + i * 0.25) * 5)
        ty = int(body_y - i * 2 * scale + math.cos(t * 3.5 + i * 0.2) * 4)
        tail_pts.append([tx, ty])
    if len(tail_pts) > 1:
        cv2.polylines(frame, [np.array(tail_pts, np.int32)], False, color, int(3 * scale), cv2.LINE_AA)

    # Elastic Elongated Neck rising into the sky
    head_y = int(body_y - 28 * scale - stretch_factor * 340 * scale)
    neck_w = int(max(4, (15 - stretch_factor * 9) * scale))
    cv2.line(frame, (cx, body_y - int(10 * scale)), (cx, head_y + int(10 * scale)), color, neck_w, cv2.LINE_AA)

    # Cat Head & Pointed Ears
    cv2.circle(frame, (cx, head_y), int(18 * scale), color, -1)
    ear_l = np.array([[cx - int(14 * scale), head_y - int(4 * scale)],
                      [cx - int(6 * scale), head_y - int(24 * scale)],
                      [cx - int(2 * scale), head_y - int(10 * scale)]], np.int32)
    ear_r = np.array([[cx + int(14 * scale), head_y - int(4 * scale)],
                      [cx + int(6 * scale), head_y - int(24 * scale)],
                      [cx + int(2 * scale), head_y - int(10 * scale)]], np.int32)
    cv2.fillPoly(frame, [ear_l, ear_r], color)

    # Sulfur-yellow eyes
    cv2.ellipse(frame, (cx - int(6 * scale), head_y - int(2 * scale)), (int(4 * scale), int(7 * scale)), 10, 0, 360, eye_color, -1)
    cv2.ellipse(frame, (cx + int(6 * scale), head_y - int(2 * scale)), (int(4 * scale), int(7 * scale)), -10, 0, 360, eye_color, -1)
    cv2.line(frame, (cx - int(6 * scale), head_y - int(7 * scale)), (cx - int(6 * scale), head_y + int(3 * scale)), (10, 10, 10), 2)
    cv2.line(frame, (cx + int(6 * scale), head_y - int(7 * scale)), (cx + int(6 * scale), head_y + int(3 * scale)), (10, 10, 10), 2)

    return frame
