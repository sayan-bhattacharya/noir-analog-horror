"""
The Shadowy Hyper-Object Figure Actor for Project NOIR.
Replaces the literal cat with an uncanny, faceless hyper-object silhouette
perched on the split-bamboo fence whose shadowy column stretches 30 feet into monsoon clouds.
"""
import math
import cv2
import numpy as np


def draw_shadowy_figure(frame: np.ndarray,
                        t: float,
                        cx: int = 980,
                        cy: int = 600,
                        stretch_factor: float = 0.0,
                        eye_color: tuple = (245, 235, 55),
                        scale: float = 1.0) -> np.ndarray:
    """
    Renders the Shadowy Hyper-Object:
    A menacing, faceless, slender shadow silhouette perched on the bamboo rail.
    Its shadowy neck/torso stretches upward into the heavens as stretch_factor increases.
    """
    h, w = frame.shape[:2]
    shadow_col = (6, 5, 8)

    # 1. Split-Bamboo Fence (বাঁশের বেড়া)
    for fx in range(cx - int(100 * scale), cx + int(120 * scale), int(30 * scale)):
        cv2.line(frame, (fx, cy), (fx, cy + int(140 * scale)), (38, 32, 24), int(5 * scale), cv2.LINE_AA)
    cv2.line(frame, (cx - int(110 * scale), cy + int(35 * scale)),
             (cx + int(130 * scale), cy + int(35 * scale)), (48, 40, 28), int(4 * scale), cv2.LINE_AA)
    cv2.line(frame, (cx - int(110 * scale), cy + int(85 * scale)),
             (cx + int(130 * scale), cy + int(85 * scale)), (48, 40, 28), int(4 * scale), cv2.LINE_AA)

    # 2. Crouching Lower Body / Shadowy Mass on rail
    body_y = int(cy + 15 * scale)
    # Undulating dark void mass
    pts_torso = []
    num_pts = 16
    for i in range(num_pts):
        angle = 2.0 * math.pi * i / num_pts
        rx = int((26 + 3.0 * math.sin(t * 3.0 + i)) * scale)
        ry = int((20 + 2.0 * math.cos(t * 2.5 + i)) * scale)
        px = int(cx + rx * math.cos(angle))
        py = int(body_y + ry * math.sin(angle))
        pts_torso.append([px, py])
    cv2.fillPoly(frame, [np.array(pts_torso, np.int32)], shadow_col)

    # Slender shadow tendrils draped over the rail
    for d_off in [-18, 0, 18]:
        tx1 = cx + int(d_off * scale)
        ty1 = body_y + int(10 * scale)
        tx2 = tx1 + int(math.sin(t * 2.0 + d_off) * 4 * scale)
        ty2 = ty1 + int(28 * scale)
        cv2.line(frame, (tx1, ty1), (tx2, ty2), shadow_col, int(3 * scale), cv2.LINE_AA)

    # 3. Slender Elongating Column / Neck extending into the heavens
    max_stretch_px = int(360 * scale)
    curr_stretch = stretch_factor * max_stretch_px
    head_y = int(body_y - 30 * scale - curr_stretch)

    # Draw undulating shadowy column connecting base to head
    neck_steps = 24
    neck_pts_l = []
    neck_pts_r = []
    half_w = max(3, int((12 - stretch_factor * 6) * scale))

    for s in range(neck_steps + 1):
        frac = s / float(neck_steps)
        curr_y = int(body_y - 10 * scale - frac * (curr_stretch + 20 * scale))
        sway = math.sin(t * 3.0 + frac * 5.0) * (4.0 * scale * (1.0 + stretch_factor * 2.0))
        center_x = cx + int(sway)
        neck_pts_l.append([center_x - half_w, curr_y])
        neck_pts_r.append([center_x + half_w, curr_y])

    polygon = neck_pts_l + neck_pts_r[::-1]
    if len(polygon) > 2:
        cv2.fillPoly(frame, [np.array(polygon, np.int32)], shadow_col)

    # 4. Faceless Humanoid / Slender Void Head
    head_cx = cx + int(math.sin(t * 3.0 + 5.0) * (4.0 * scale * (1.0 + stretch_factor * 2.0)))
    head_rx = int(14 * scale)
    head_ry = int(22 * scale)
    cv2.ellipse(frame, (head_cx, head_y), (head_rx, head_ry), 0, 0, 360, shadow_col, -1)

    # 5. Cold, unblinking void eyes (piercing horizontal slits that evoke cosmic dread)
    eye_offset_y = int(head_y - 2 * scale)
    eye_w = max(2, int(4 * scale))
    eye_h = max(1, int(2 * scale))

    cv2.ellipse(frame, (head_cx - int(5 * scale), eye_offset_y), (eye_w, eye_h), 0, 0, 360, eye_color, -1)
    cv2.ellipse(frame, (head_cx + int(5 * scale), eye_offset_y), (eye_w, eye_h), 0, 0, 360, eye_color, -1)

    # Subtle ambient dark aura radiating from the entity
    aura_overlay = frame.copy()
    cv2.circle(aura_overlay, (head_cx, head_y), int(35 * scale), (2, 2, 4), -1)
    cv2.addWeighted(aura_overlay, 0.40, frame, 0.60, 0, frame)

    return frame


def draw_hulo_cat(*args, **kwargs):
    """Backward-compatible alias routing directly to draw_shadowy_figure."""
    return draw_shadowy_figure(*args, **kwargs)
