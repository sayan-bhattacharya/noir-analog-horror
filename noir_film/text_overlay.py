"""
Text and Emergency Typography Overlay System for Project NOIR.
Full support for authentic Bengali and English text with typewriter reveal,
emergency banner styling, and vintage silent film intertitles.
"""
import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(_CUR_DIR, "fonts")
BENGALI_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansBengali-Bold.ttf")

if not os.path.exists(BENGALI_FONT_PATH):
    alt_paths = [
        "/content/noir-analog-horror/noir_film/fonts/NotoSansBengali-Bold.ttf",
        "C:/Users/sayan/noir-analog-horror/noir_film/fonts/NotoSansBengali-Bold.ttf",
        "e:/betweenthenotes/noir_film_project/noir_film/fonts/NotoSansBengali-Bold.ttf",
    ]
    for p in alt_paths:
        if os.path.exists(p):
            BENGALI_FONT_PATH = p
            break

_FONT_CACHE = {}


def get_font(size: int = 24):
    """Caches TrueType fonts for smooth high-fps rendering."""
    if size not in _FONT_CACHE:
        try:
            _FONT_CACHE[size] = ImageFont.truetype(BENGALI_FONT_PATH, size)
        except Exception:
            _FONT_CACHE[size] = ImageFont.load_default()
    return _FONT_CACHE[size]


def draw_text(img: np.ndarray,
              text: str,
              pos: tuple,
              font_size: int = 24,
              fill_color: tuple = (240, 240, 240),
              anchor: str = None) -> np.ndarray:
    """Renders crisp Bengali / English text onto an OpenCV uint8 image via PIL."""
    if not text:
        return img
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    font = get_font(font_size)
    draw.text(pos, text, font=font, fill=fill_color, anchor=anchor)
    img[:] = np.array(pil_img)
    return img


def draw_emergency_banner(frame: np.ndarray,
                          text_bengali: str,
                          text_english: str = "",
                          y_center: int = 200,
                          banner_color: tuple = (178, 24, 24),
                          border_color: tuple = (212, 175, 55)) -> np.ndarray:
    """Renders the official Doordarshan emergency banner."""
    h, w = frame.shape[:2]
    b_h = 65
    y1 = y_center - b_h // 2
    y2 = y_center + b_h // 2

    cv2.rectangle(frame, (50, y1), (w - 50, y2), banner_color, -1)
    cv2.rectangle(frame, (50, y1), (w - 50, y2), border_color, 2)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)
    f_bn = get_font(26)
    f_en = get_font(16)

    if text_english:
        draw.text((w // 2, y_center - 12), text_bengali, font=f_bn, fill=(255, 255, 255), anchor="mm")
        draw.text((w // 2, y_center + 16), text_english, font=f_en, fill=(245, 205, 55), anchor="mm")
    else:
        draw.text((w // 2, y_center), text_bengali, font=f_bn, fill=(255, 255, 255), anchor="mm")

    frame[:] = np.array(pil_img)
    return frame


def draw_rule_card(frame: np.ndarray,
                   rule_id: str,
                   text_bengali: str,
                   text_english: str = "",
                   y_start: int = 540) -> np.ndarray:
    """Renders a mandatory Doordarshan emergency rule at the bottom of the screen."""
    h, w = frame.shape[:2]
    # Dark translucent letterbox background
    overlay = frame.copy()
    cv2.rectangle(overlay, (40, y_start - 20), (w - 40, h - 30), (8, 12, 18), -1)
    cv2.addWeighted(overlay, 0.78, frame, 0.22, 0, frame)
    cv2.rectangle(frame, (40, y_start - 20), (w - 40, h - 30), (178, 24, 24), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    draw.text((65, y_start), rule_id, font=get_font(20), fill=(94, 220, 120))
    draw.text((65, y_start + 30), text_bengali, font=get_font(21), fill=(245, 245, 245))
    if text_english:
        draw.text((65, y_start + 64), text_english, font=get_font(16), fill=(200, 215, 200))

    frame[:] = np.array(pil_img)
    return frame


def draw_silent_film_intertitle(frame: np.ndarray,
                                main_text: str,
                                sub_text: str = "",
                                t: float = 0.0) -> np.ndarray:
    """Renders an authentic vintage Silent Film / Alex Kister analog horror dialogue card."""
    h, w = frame.shape[:2]
    frame[:, :] = [12, 10, 14]

    jitter_y = int(math.sin(t * 19.0) * 1.5)
    jitter_x = int(math.cos(t * 13.0) * 1.2)

    pad = 52
    cv2.rectangle(frame, (pad + jitter_x, pad + jitter_y),
                  (w - pad + jitter_x, h - pad + jitter_y), (210, 205, 195), 2)
    cv2.rectangle(frame, (pad + 12 + jitter_x, pad + 12 + jitter_y),
                  (w - pad - 12 + jitter_x, h - pad - 12 + jitter_y), (130, 125, 120), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)
    cy = h // 2 + jitter_y - (22 if sub_text else 0)
    draw.text((w // 2 + jitter_x, cy), main_text, font=get_font(34), fill=(245, 242, 235), anchor="mm")
    if sub_text:
        draw.text((w // 2 + jitter_x, cy + 50), sub_text, font=get_font(21), fill=(180, 175, 165), anchor="mm")
    frame[:] = np.array(pil_img)
    return frame
