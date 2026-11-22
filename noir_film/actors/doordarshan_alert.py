"""
Procedural Bharat Darpan Spiral Eye Emblem & Emergency Interruption Actor.
Proportional layout and auto-fitted text margins ensure pristine rendering at any resolution.
"""
import math
import cv2
import numpy as np
from .. import text_overlay


def draw_bharat_darpan_logo(frame: np.ndarray,
                            cx: int,
                            cy: int,
                            radius: int = 50,
                            t: float = 0.0,
                            rotation_speed: float = 0.35,
                            pupil_twitch: bool = False,
                            red_scanlines: float = 0.0) -> np.ndarray:
    """Renders the Bharat Darpan spiral emblem with phosphor glow."""
    pulse = 1.0 + 0.05 * math.sin(t * 4.0)
    if pupil_twitch:
        pulse += 0.12 * math.sin(t * 32.0)
    r = int(radius * pulse)

    color_gold = (245, 205, 55)
    color_dark = (25, 18, 15)
    if red_scanlines > 0.3:
        color_gold = (240, 60, 45)

    # Core pupil
    cv2.circle(frame, (cx, cy), int(13 * (radius / 50.0) * pulse), color_gold, -1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), int(6 * (radius / 50.0) * pulse), color_dark, -1, cv2.LINE_AA)

    # Symmetrical spiral arms
    for angle_offset in [0.0, math.pi]:
        pts = []
        for a in np.linspace(0, 1.38 * math.pi, 30):
            ang = a + angle_offset + t * rotation_speed
            dist = 12 * (radius / 50.0) + (a / (1.38 * math.pi)) * (r - 12 * (radius / 50.0))
            px = int(cx + math.cos(ang) * dist)
            py = int(cy + math.sin(ang) * dist * 0.82)
            pts.append([px, py])
        if len(pts) > 1:
            line_w = max(2, int(4 * (radius / 50.0)))
            cv2.polylines(frame, [np.array(pts, np.int32)], False, color_gold, line_w, cv2.LINE_AA)

    return frame

# Backward compatibility alias
draw_doordarshan_logo = draw_bharat_darpan_logo


def render_scene_01(frame: np.ndarray, t: float, params: dict) -> np.ndarray:
    """Renders Scene 1: ACT_01_SIGNAL_INTERRUPT (00:00 - 00:15)."""
    h, w = frame.shape[:2]
    frame[:, :] = [18, 15, 48]

    rot_speed = params.get("spiral_rotation_speed", 0.35)
    pupil_twitch_time = params.get("pupil_twitch_time", 5.0)
    is_twitching = bool(t >= pupil_twitch_time)

    red_scan = params.get("red_scanline_intensity", 0.28) if t > pupil_twitch_time else 0.0

    logo_cy = int(h * 0.18)
    logo_r = int(h * 0.085)

    # 1. Bharat Darpan Logo
    draw_bharat_darpan_logo(frame, w // 2, logo_cy, radius=logo_r, t=t,
                            rotation_speed=rot_speed,
                            pupil_twitch=is_twitching,
                            red_scanlines=red_scan)

    # Motto
    motto_y = logo_cy + logo_r + int(h * 0.045)
    text_overlay.draw_text(frame, "সত্যম শিবম সুন্দরম", (w // 2, motto_y),
                           font_size=int(h * 0.032), fill_color=(245, 205, 55), anchor="mm")

    # 2. Emergency Banner cuts across screen at t >= 5.0
    if t >= 5.0:
        banner_y = int(h * 0.44)
        text_overlay.draw_emergency_banner(
            frame,
            "ভারত দর্পণ বিশেষ জরুরি সম্প্রচার — পশ্চিমবঙ্গ বিপর্যয় মোকাবিলা",
            "[ CODE: 94/ALERT-NISHIDAK  •  SECTOR: BHARAT DARPAN WB ]",
            y_center=banner_y
        )

    # Safe margin for body text
    safe_margin_x = int(w * 0.10)
    max_body_w = int(w * 0.80)

    # 3. Teleprompter Jurisdiction Text (t >= 7.0)
    if t >= 7.0:
        sec_y1 = int(h * 0.58)
        sec_y2 = sec_y1 + int(h * 0.048)
        text_overlay.draw_text(
            frame,
            "অধিক্ষেত্র: নিস্তব্ধপুর ও তৎসংলগ্ন জনহীন প্রান্তর",
            (safe_margin_x, sec_y1), font_size=int(h * 0.034), fill_color=(94, 220, 120),
            max_width=max_body_w
        )
        text_overlay.draw_text(
            frame,
            "[ JURISDICTION: NISTOBDHOPUR  •  THREAT LEVEL: IV ]",
            (safe_margin_x, sec_y2), font_size=int(h * 0.024), fill_color=(190, 215, 190),
            max_width=max_body_w
        )

    # 4. Directive Rule 1 preview (t >= 9.0)
    if t >= 9.0:
        rule_y = int(h * 0.72)
        text_overlay.draw_text(
            frame,
            "১. রাত ১২টার পর পরিচিত কণ্ঠে নিশিডাক আসিলে ভুলেও কপাট খুলিবেন না।",
            (safe_margin_x, rule_y), font_size=int(h * 0.032), fill_color=(240, 240, 240),
            max_width=max_body_w
        )
        text_overlay.draw_text(
            frame,
            "[ MANDATORY: DO NOT ANSWER FAMILIAR VOICES IN MONSOON NIGHT ]",
            (safe_margin_x, rule_y + int(h * 0.046)), font_size=int(h * 0.022), fill_color=(185, 205, 185),
            max_width=max_body_w
        )

    # 5. Flashes and Dropout (11.0s - 14.2s)
    if 11.2 <= t < 11.4 or 11.8 <= t < 12.0:
        frame[:] = [240, 240, 235]  # White flash

    if t >= 14.2:
        frame[:, :] = [4, 4, 6]  # Cut to black

    return frame

