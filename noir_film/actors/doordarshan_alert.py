"""
Procedural Doordarshan Spiral Eye Emblem & Emergency Interruption Actor.
"""
import math
import cv2
import numpy as np
from .. import text_overlay


def draw_doordarshan_logo(frame: np.ndarray,
                          cx: int,
                          cy: int,
                          radius: int = 50,
                          t: float = 0.0,
                          rotation_speed: float = 0.35,
                          pupil_twitch: bool = False,
                          red_scanlines: float = 0.0) -> np.ndarray:
    """Renders the iconic Doordarshan spiral eye emblem with phosphor glow."""
    pulse = 1.0 + 0.05 * math.sin(t * 4.0)
    if pupil_twitch:
        pulse += 0.12 * math.sin(t * 32.0)
    r = int(radius * pulse)

    color_gold = (245, 205, 55)
    color_dark = (25, 18, 15)
    if red_scanlines > 0.3:
        color_gold = (240, 60, 45)

    # Core pupil
    cv2.circle(frame, (cx, cy), int(13 * pulse), color_gold, -1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), int(6 * pulse), color_dark, -1, cv2.LINE_AA)

    # Symmetrical spiral arms
    for angle_offset in [0.0, math.pi]:
        pts = []
        for a in np.linspace(0, 1.38 * math.pi, 30):
            ang = a + angle_offset + t * rotation_speed
            dist = 14 + (a / (1.38 * math.pi)) * (r - 14)
            px = int(cx + math.cos(ang) * dist)
            py = int(cy + math.sin(ang) * dist * 0.82)
            pts.append([px, py])
        if len(pts) > 1:
            cv2.polylines(frame, [np.array(pts, np.int32)], False, color_gold, 4, cv2.LINE_AA)

    return frame


def render_scene_01(frame: np.ndarray, t: float, params: dict) -> np.ndarray:
    """Renders Scene 1: ACT_01_DD_INTERRUPT (00:00 - 00:15)."""
    h, w = frame.shape[:2]
    frame[:, :] = [18, 15, 48]

    rot_speed = params.get("spiral_rotation_speed", 0.35)
    pupil_twitch_time = params.get("pupil_twitch_time", 5.0)
    is_twitching = bool(t >= pupil_twitch_time)

    red_scan = params.get("red_scanline_intensity", 0.28) if t > pupil_twitch_time else 0.0

    # 1. Doordarshan Logo
    draw_doordarshan_logo(frame, w // 2, 90, radius=46, t=t,
                          rotation_speed=rot_speed,
                          pupil_twitch=is_twitching,
                          red_scanlines=red_scan)

    # Motto
    text_overlay.draw_text(frame, "সত্যম শিবম সুন্দরম", (w // 2, 142), font_size=18,
                           fill_color=(245, 205, 55), anchor="mm")

    # 2. Emergency Banner cuts across screen at t >= 5.0
    if t >= 5.0:
        text_overlay.draw_emergency_banner(
            frame,
            "দূরদর্শন বিশেষ জরুরি সম্প্রচার — পশ্চিমবঙ্গ বিপর্যয় মোকাবিলা",
            "DOORDARSHAN EMERGENCY BROADCAST — WEST BENGAL SECTOR",
            y_center=195
        )

    # 3. Teleprompter Jurisdiction Text (t >= 7.0)
    if t >= 7.0:
        text_overlay.draw_text(
            frame,
            "অধিক্ষেত্র: নিস্তব্ধপুর ও পার্শ্ববর্তী জনহীন প্রান্তর",
            (80, 245), font_size=21, fill_color=(94, 220, 120)
        )
        text_overlay.draw_text(
            frame,
            "JURISDICTION: NISTOBDHOPUR & ADJACENT UNINHABITED PADDY WASTELANDS",
            (80, 275), font_size=15, fill_color=(190, 215, 190)
        )

    # 4. Directive Rule 1 preview
    if t >= 9.0:
        text_overlay.draw_text(
            frame,
            "১. রাত ১২টার পর কলাবাগান থেকে চেনা কণ্ঠে নিশিডাক শুনলে দরজা খুলবেন না।",
            (80, 320), font_size=20, fill_color=(240, 240, 240)
        )

    # 5. Flashes and Dropout (11.0s - 14.2s)
    if 11.2 <= t < 11.4 or 11.8 <= t < 12.0:
        frame[:] = [240, 240, 235]  # White flash

    if t >= 14.2:
        frame[:, :] = [4, 4, 6]  # Cut to black

    return frame
