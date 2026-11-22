"""
Bimal Babu's Kafkaesque Metamorphosis Actor for Project NOIR.
Stop-motion 32 Hz segmented chitinous limbs, ribbed carapace, and burning cataracts.
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
                             cataract_glow: float = 0.95) -> np.ndarray:
    """Renders Bimal Babu undergoing biological segmentation on the red-oxide floor."""
    color = (16, 12, 20)
    jitter = math.sin(t * jitter_hz) * (3.5 * progress)

    # Torso swelling into segmented carapace
    torso_w = int(24 + 36 * progress)
    torso_h = int(55 + 24 * progress)
    cv2.ellipse(frame, (int(cx + jitter), int(cy)), (torso_w, torso_h),
                int(12 * math.sin(t * 2.5)), 0, 360, color, -1)

    # Chitin ridge segments
    if progress > 0.25:
        for ridge_i in range(4):
            ry = int(cy - torso_h * 0.6 + ridge_i * (torso_h * 0.35))
            cv2.ellipse(frame, (int(cx + jitter), ry), (int(torso_w * 0.85), 4), 0, 0, 180, (40, 35, 50), 2)

    # Head
    head_y = int(cy - torso_h - 16)
    cv2.circle(frame, (int(cx + jitter), head_y), int(16 + 5 * progress), color, -1)

    # 3 Crimson Cataracts burning through darkness
    if progress > 0.3:
        eye_col = (int(40 * cataract_glow), int(30 * cataract_glow), int(245 * cataract_glow))
        cv2.circle(frame, (int(cx + jitter), head_y - 6), 3, eye_col, -1)
        cv2.circle(frame, (int(cx + jitter - 6), head_y + 1), 2, eye_col, -1)
        cv2.circle(frame, (int(cx + jitter + 6), head_y + 1), 2, eye_col, -1)

    # Segmented cockroach/scorpion limbs (8 limbs)
    num_legs = 8 if progress > 0.5 else 4
    for leg_i in range(num_legs):
        side = -1 if (leg_i % 2 == 0) else 1
        leg_row = leg_i // 2
        base_y = int(cy - torso_h * 0.4 + leg_row * (torso_h * 0.38))
        base_x = int(cx + side * (torso_w * 0.75))

        twitch = math.sin(t * jitter_hz + leg_i * 1.8) * (18.0 * max(0.3, progress))
        knee_x = int(base_x + side * (55 + twitch))
        knee_y = int(base_y - (30 + twitch * 0.4))
        foot_x = int(knee_x + side * (32 - twitch * 0.4))
        foot_y = int(cy + 52 + math.cos(t * 14.0 + leg_i) * 12)

        cv2.line(frame, (base_x, base_y), (knee_x, knee_y), color, 3, cv2.LINE_AA)
        cv2.line(frame, (knee_x, knee_y), (foot_x, foot_y), color, 2, cv2.LINE_AA)
        cv2.circle(frame, (foot_x, foot_y), 2, (30, 25, 40), -1)

    return frame
