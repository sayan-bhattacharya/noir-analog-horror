"""
The Colossal Celestial Third Eye (Trinetra / ত্রিনেত্র) Actor for Project NOIR.
Upgraded with Sinister Blood-Crimson Iris, ocular hyperemia capillaries,
and occult mandala striations for the 4:11 mark (251s).
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
                      dilation_extra: float = 0.0,
                      sinister_red: float = 1.0) -> np.ndarray:
    """
    Renders the colossal third-eye aperture in the heavens:
    - Sinister blood-red glowing iris with radiating solar/mandala striations.
    - Branching crimson capillaries spidering across the bruised sclera.
    - Pulsating cosmic pupil swallowing the heavens.
    """
    h, w = frame.shape[:2]
    eye_w = int(240 * scale)
    eye_h = int(120 * scale)

    # 1. Sinister Ambient Red Glow / Aura in the surrounding void
    if sinister_red > 0.1:
        aura_r_x = int(eye_w * (1.3 + 0.1 * math.sin(t * 3.0)))
        aura_r_y = int(eye_h * (1.3 + 0.1 * math.sin(t * 3.0)))
        aura_overlay = frame.copy()
        # RGB format: Red is index 0!
        cv2.ellipse(aura_overlay, (cx, cy), (aura_r_x, aura_r_y), 0, 0, 360, (int(140 * sinister_red), 15, 15), -1)
        cv2.addWeighted(aura_overlay, 0.45 * sinister_red, frame, 1.0 - 0.45 * sinister_red, 0, frame)

    # 2. Sclera: Bruised, cold off-white with sinister pinkish/blood tint
    # RGB format: R=220, G=190, B=190
    sclera_col = (
        int(195 + 45 * sinister_red),
        int(205 - 65 * sinister_red),
        int(215 - 45 * sinister_red)
    )
    cv2.ellipse(frame, (cx, cy), (eye_w, eye_h), 0, 0, 360, sclera_col, -1, cv2.LINE_AA)

    # 3. Dense Branching Crimson Capillaries across the sclera (RGB: [235, 15, 15])
    rng = np.random.RandomState(42)
    capillary_col = (int(235 * max(0.6, sinister_red)), 15, 15)
    for branch_i in range(20):
        ang = branch_i * (2.0 * math.pi / 20.0)
        px, py = cx, cy
        dist_step = (eye_w * 0.72) / 6.0
        for step in range(6):
            nx = int(px + math.cos(ang) * dist_step + rng.randint(-7, 8))
            ny = int(py + math.sin(ang) * (dist_step * 0.42) + rng.randint(-4, 5))
            thick = 2 if (step < 2 and branch_i % 3 == 0) else 1
            cv2.line(frame, (px, py), (nx, ny), capillary_col, thick, cv2.LINE_AA)
            px, py = nx, ny

    # 4. Sinister Blood-Red Iris with Radiating Striations & Mandala Rings
    iris_r = int(72 * scale)
    # RGB format: Blood Red is R=235, G=20, B=20!
    iris_col = (
        int(235 * sinister_red + 80 * (1.0 - sinister_red)),
        int(15 * (1.0 - sinister_red) + 15 * sinister_red),
        int(25 * (1.0 - sinister_red) + 15 * sinister_red)
    )
    cv2.circle(frame, (cx, cy), iris_r, iris_col, -1, cv2.LINE_AA)

    # Radiating ocular striations (Bright Crimson RGB: [255, 25, 20])
    for stri_i in range(32):
        s_ang = stri_i * (2.0 * math.pi / 32.0)
        sx1 = int(cx + math.cos(s_ang) * (iris_r * 0.4))
        sy1 = int(cy + math.sin(s_ang) * (iris_r * 0.4))
        sx2 = int(cx + math.cos(s_ang) * (iris_r * 0.95))
        sy2 = int(cy + math.sin(s_ang) * (iris_r * 0.95))
        stri_col = (255, 25, 20) if (stri_i % 2 == 0) else (160, 10, 10)
        cv2.line(frame, (sx1, sy1), (sx2, sy2), stri_col, 1, cv2.LINE_AA)

    # Concentric Occult / Mandala Rings
    cv2.circle(frame, (cx, cy), int(iris_r * 0.75), (210, 20, 20), 1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), int(iris_r * 0.50), (160, 15, 15), 1, cv2.LINE_AA)

    # 5. Pulsating Cosmic Void Pupil
    effective_pupil_r = int((pupil_radius_base + dilation_extra * 48.0) * scale)
    cv2.circle(frame, (cx, cy), effective_pupil_r, (4, 4, 6), -1, cv2.LINE_AA)

    # 6. Eerie Specular Reflection
    cv2.circle(frame, (cx - int(12 * scale), cy - int(12 * scale)), max(2, int(5 * scale)), (245, 240, 235), -1, cv2.LINE_AA)
    cv2.circle(frame, (cx + int(8 * scale), cy + int(10 * scale)), max(1, int(3 * scale)), (210, 205, 200), -1, cv2.LINE_AA)

    # 7. Heavy Eyelid Bezel
    cv2.ellipse(frame, (cx, cy), (eye_w, eye_h), 0, 0, 360, (12, 10, 16), int(5 * scale), cv2.LINE_AA)

    return frame
