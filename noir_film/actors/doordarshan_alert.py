"""
Between the Notes Station ID, Emblem & Emergency Interruption Actor.
Proportional layout and auto-fitted text margins ensure pristine rendering at any resolution.
Features official Between the Notes circular branding with authentic analog CRT phosphor glow.
"""
import math
import os
import cv2
import numpy as np
from .. import text_overlay

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(ROOT, "assets", "logo-circle.png")
_CACHED_LOGO = None


def get_logo_image():
    global _CACHED_LOGO
    if _CACHED_LOGO is None and os.path.exists(LOGO_PATH):
        try:
            _CACHED_LOGO = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
        except Exception:
            _CACHED_LOGO = None
    return _CACHED_LOGO


def draw_between_the_notes_logo(frame: np.ndarray,
                               cx: int,
                               cy: int,
                               radius: int = 50,
                               t: float = 0.0,
                               rotation_speed: float = 0.35,
                               pupil_twitch: bool = False,
                               red_scanlines: float = 0.0) -> np.ndarray:
    """Renders the official Between the Notes circular emblem with phosphor CRT glow."""
    pulse = 1.0 + 0.04 * math.sin(t * 4.0)
    if pupil_twitch:
        pulse += 0.10 * math.sin(t * 32.0)
    r = int(radius * pulse)

    logo_img = get_logo_image()
    if logo_img is not None and r > 10:
        # Resize cached Between the Notes circular logo
        target_size = r * 2
        resized = cv2.resize(logo_img, (target_size, target_size), interpolation=cv2.INTER_AREA)

        # Alpha blend into frame
        x1 = cx - r
        y1 = cy - r
        x2 = x1 + target_size
        y2 = y1 + target_size

        h, w = frame.shape[:2]
        if x1 >= 0 and y1 >= 0 and x2 <= w and y2 <= h:
            if resized.shape[2] == 4:
                alpha = (resized[:, :, 3] / 255.0)[:, :, np.newaxis]
                bgr = resized[:, :, :3]
                if red_scanlines > 0.3:
                    # Tint red during emergency horror pulse
                    bgr = bgr.copy()
                    bgr[:, :, 0] = (bgr[:, :, 0] * 0.4).astype(np.uint8)
                    bgr[:, :, 1] = (bgr[:, :, 1] * 0.4).astype(np.uint8)
                    bgr[:, :, 2] = np.clip(bgr[:, :, 2].astype(int) + 60, 0, 255).astype(np.uint8)
                roi = frame[y1:y2, x1:x2]
                frame[y1:y2, x1:x2] = (roi * (1.0 - alpha) + bgr * alpha).astype(np.uint8)
            else:
                frame[y1:y2, x1:x2] = resized

            # Outer luminous phosphor ring
            ring_color = (240, 60, 45) if red_scanlines > 0.3 else (245, 205, 55)
            cv2.circle(frame, (cx, cy), r + 2, ring_color, 2, cv2.LINE_AA)
            cv2.circle(frame, (cx, cy), r + 5, (int(ring_color[0] * 0.4), int(ring_color[1] * 0.4), int(ring_color[2] * 0.4)), 1, cv2.LINE_AA)
            return frame

    # Procedural Fallback Emblem if file not loaded
    color_gold = (240, 60, 45) if red_scanlines > 0.3 else (245, 205, 55)
    color_dark = (25, 18, 15)

    cv2.circle(frame, (cx, cy), r, color_gold, 2, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), int(13 * (radius / 50.0) * pulse), color_gold, -1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), int(6 * (radius / 50.0) * pulse), color_dark, -1, cv2.LINE_AA)

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


# Backward compatibility aliases
draw_bharat_darpan_logo = draw_between_the_notes_logo
draw_doordarshan_logo = draw_between_the_notes_logo


def render_scene_01(frame: np.ndarray, t: float, params: dict) -> np.ndarray:
    """Renders Scene 1: ACT_01_SIGNAL_INTERRUPT (00:00 - 00:15)."""
    h, w = frame.shape[:2]
    frame[:, :] = [18, 15, 48]

    rot_speed = params.get("spiral_rotation_speed", 0.35)
    pupil_twitch_time = params.get("pupil_twitch_time", 5.0)
    is_twitching = bool(t >= pupil_twitch_time)

    red_scan = params.get("red_scanline_intensity", 0.28) if t > pupil_twitch_time else 0.0

    logo_cy = int(h * 0.22)
    logo_r = int(h * 0.10)

    # 1. Between the Notes Official Logo Emblem
    draw_between_the_notes_logo(frame, w // 2, logo_cy, radius=logo_r, t=t,
                                rotation_speed=rot_speed,
                                pupil_twitch=is_twitching,
                                red_scanlines=red_scan)

    # Station Header & Promotional Identity
    hdr_y = logo_cy + logo_r + int(h * 0.050)
    text_overlay.draw_text(frame, "বিটুইন দ্য নোটস সম্প্রচার কেন্দ্র কলকাতা", (w // 2, hdr_y),
                           font_size=int(h * 0.036), fill_color=(245, 205, 55), anchor="mm")

    motto_y = hdr_y + int(h * 0.046)
    text_overlay.draw_text(frame, "BETWEEN THE NOTES BROADCAST NETWORK • মাঝরাতের বিশেষ সম্প্রচার", (w // 2, motto_y),
                           font_size=int(h * 0.024), fill_color=(212, 175, 55), anchor="mm")

    # 2. Emergency Banner cuts across screen at t >= 5.0
    if t >= 5.0:
        banner_y = int(h * 0.44)
        text_overlay.draw_emergency_banner(
            frame,
            "বিটুইন দ্য নোটস বিশেষ জরুরি সম্প্রচার: পশ্চিমবঙ্গ বিপর্যয় মোকাবিলা",
            "[ CODE: 94/ALERT-NISHIDAK  •  NETWORK: BETWEEN THE NOTES ]",
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
            "এলাকা: নিস্তব্ধপুর ও আশেপাশের ফাঁকা মাঠ",
            (safe_margin_x, sec_y1), font_size=int(h * 0.034), fill_color=(94, 220, 120),
            max_width=max_body_w
        )
        text_overlay.draw_text(
            frame,
            "[ JURISDICTION: NISTOBDHOPUR  •  PRESENTED BY BETWEEN THE NOTES ]",
            (safe_margin_x, sec_y2), font_size=int(h * 0.024), fill_color=(190, 215, 190),
            max_width=max_body_w
        )

    # 4. Directive Rule 1 preview (t >= 9.0)
    if t >= 9.0:
        rule_y = int(h * 0.72)
        text_overlay.draw_text(
            frame,
            "১. রাত ১২টার পর পরিচিত কণ্ঠে ডাক শুনলেও ভুলেও দরজা খুলবেন না।",
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
