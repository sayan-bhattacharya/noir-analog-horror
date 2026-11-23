"""
Bimal Babu's Kafkaesque Metamorphosis Actor for Project NOIR.
Supports dynamic scale:
- Tiny crawling chitinous arachnid prior to 2:02 mark (t < 122s).
- Massive giant eruption spanning the size of the entire mosquito net at the 2:02 emergency beep swell!
"""
import math
import cv2
import numpy as np


def draw_bimal_metamorphosis(frame: np.ndarray,
                             t: float,
                             cx: int,
                             cy: int,
                             progress: float = 0.0,
                             jitter_hz: float = 32.0,
                             cataract_glow: float = 0.95,
                             scale: float = 1.0) -> np.ndarray:
    """
    Renders the Kafkaesque chitinous creature:
    - scale < 0.4: Tiny scuttling parasite twitching under the cot.
    - scale >= 1.5: Giant room-sized nightmare spanning the mosquito net.
    """
    h, w = frame.shape[:2]
    color = (12, 10, 16)
    highlight_chitin = (42, 38, 52)

    jitter = math.sin(t * jitter_hz) * (3.5 * progress * scale)

    # Torso / Carapace
    torso_w = int((24 + 36 * progress) * scale)
    torso_h = int((55 + 24 * progress) * scale)
    cv2.ellipse(frame, (int(cx + jitter), int(cy)), (torso_w, torso_h),
                int(12 * math.sin(t * 2.5)), 0, 360, color, -1)

    # Chitin ridge segments on carapace
    if progress > 0.2:
        for ridge_i in range(5):
            ry = int(cy - torso_h * 0.6 + ridge_i * (torso_h * 0.30))
            rw = int(torso_w * (0.9 - ridge_i * 0.08))
            cv2.ellipse(frame, (int(cx + jitter), ry), (max(4, rw), max(2, int(5 * scale))),
                        0, 0, 180, highlight_chitin, max(1, int(2 * scale)))

    # Cephalothorax Head
    head_y = int(cy - torso_h - int(16 * scale))
    head_r = int((16 + 8 * progress) * scale)
    cv2.circle(frame, (int(cx + jitter), head_y), head_r, color, -1)

    # 3 Crimson / Sulfur Cataract Eyes burning through the dark
    if progress > 0.25:
        eye_col = (int(30 * cataract_glow), int(35 * cataract_glow), int(245 * cataract_glow))
        pupil_r = max(2, int(3 * scale))
        cv2.circle(frame, (int(cx + jitter), head_y - int(6 * scale)), pupil_r, eye_col, -1)
        cv2.circle(frame, (int(cx + jitter - 8 * scale), head_y + int(2 * scale)), max(1, int(2 * scale)), eye_col, -1)
        cv2.circle(frame, (int(cx + jitter + 8 * scale), head_y + int(2 * scale)), max(1, int(2 * scale)), eye_col, -1)

    # Segmented arachnid / chitinous limbs (8 sprawling legs)
    num_legs = 8 if progress > 0.35 else 4
    for leg_i in range(num_legs):
        side = -1 if (leg_i % 2 == 0) else 1
        leg_row = leg_i // 2
        base_y = int(cy - torso_h * 0.4 + leg_row * (torso_h * 0.32))
        base_x = int(cx + side * (torso_w * 0.8))

        # Twitching motion
        twitch = math.sin(t * jitter_hz + leg_i * 1.8) * (18.0 * max(0.3, progress) * scale)
        knee_x = int(base_x + side * (55 * scale + twitch))
        knee_y = int(base_y - (30 * scale + twitch * 0.4))
        foot_x = int(knee_x + side * (45 * scale - twitch * 0.3))
        foot_y = int(cy + int(60 * scale) + math.cos(t * 14.0 + leg_i) * (12 * scale))

        leg_thick = max(1, int(3.5 * scale))
        cv2.line(frame, (base_x, base_y), (knee_x, knee_y), color, leg_thick, cv2.LINE_AA)
        cv2.line(frame, (knee_x, knee_y), (foot_x, foot_y), color, max(1, int(2.5 * scale)), cv2.LINE_AA)
        cv2.circle(frame, (foot_x, foot_y), max(2, int(3 * scale)), highlight_chitin, -1)

    # If giant size: draw ominous shadow tendrils grasping the walls
    if scale >= 1.5:
        for t_idx in range(6):
            ang = t_idx * (math.pi / 3.0) + math.sin(t * 1.5) * 0.1
            tx_end = int(cx + math.cos(ang) * (380 * scale))
            ty_end = int(cy + math.sin(ang) * (260 * scale))
            cv2.line(frame, (cx, cy), (tx_end, ty_end), (8, 6, 12), int(4 * scale), cv2.LINE_AA)

    return frame
