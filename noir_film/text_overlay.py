"""
Text and Emergency Typography Overlay System for Project NOIR.
Full dual-engine font rendering for authentic Bengali and English typography.
Auto-fitting safe-area algorithm ensures text never overflows the CRT curvature margins.
"""
import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(_CUR_DIR, "fonts")
BENGALI_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansBengali-Bold.ttf")
ENGLISH_FONT_PATH = os.path.join(FONTS_DIR, "IBMPlexMono-Bold.ttf")

# Fallback paths
if not os.path.exists(BENGALI_FONT_PATH):
    for p in [
        "/content/noir-analog-horror/noir_film/fonts/NotoSansBengali-Bold.ttf",
        "C:/Users/sayan/noir-analog-horror/noir_film/fonts/NotoSansBengali-Bold.ttf",
        "e:/betweenthenotes/noir_film_project/noir_film/fonts/NotoSansBengali-Bold.ttf",
    ]:
        if os.path.exists(p):
            BENGALI_FONT_PATH = p
            break

if not os.path.exists(ENGLISH_FONT_PATH):
    for p in [
        "/content/noir-analog-horror/noir_film/fonts/IBMPlexMono-Bold.ttf",
        "C:/Users/sayan/noir-analog-horror/noir_film/fonts/IBMPlexMono-Bold.ttf",
        "e:/betweenthenotes/noir_film_project/noir_film/fonts/IBMPlexMono-Bold.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]:
        if os.path.exists(p):
            ENGLISH_FONT_PATH = p
            break

_BN_FONT_CACHE = {}
_EN_FONT_CACHE = {}


def get_bengali_font(size: int = 24):
    """Caches TrueType Bengali font."""
    if size not in _BN_FONT_CACHE:
        try:
            _BN_FONT_CACHE[size] = ImageFont.truetype(BENGALI_FONT_PATH, size)
        except Exception:
            _BN_FONT_CACHE[size] = ImageFont.load_default()
    return _BN_FONT_CACHE[size]


def get_english_font(size: int = 18):
    """Caches TrueType Latin Monospaced font."""
    if size not in _EN_FONT_CACHE:
        try:
            _EN_FONT_CACHE[size] = ImageFont.truetype(ENGLISH_FONT_PATH, size)
        except Exception:
            _EN_FONT_CACHE[size] = ImageFont.load_default()
    return _EN_FONT_CACHE[size]


def has_bengali(text: str) -> bool:
    """Checks whether a string contains Bengali Unicode characters (U+0980 to U+09FF)."""
    return any(0x0980 <= ord(c) <= 0x09FF for c in text)


def get_font_for_text(text: str, size: int):
    """Returns the correct TrueType font based on language encoding."""
    if has_bengali(text):
        return get_bengali_font(size)
    return get_english_font(size)


def fit_font(text: str, max_width: int, initial_size: int, min_size: int = 10):
    """Auto-scales font size down until text bounding box fits within max_width."""
    size = initial_size
    fnt = get_font_for_text(text, size)
    # Temporary draw object for measuring
    tmp = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(tmp)
    while size > min_size:
        bbox = d.textbbox((0, 0), text, font=fnt)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            break
        size -= 1
        fnt = get_font_for_text(text, size)
    return fnt, size


def draw_text(img: np.ndarray,
              text: str,
              pos: tuple,
              font_size: int = 24,
              fill_color: tuple = (240, 240, 240),
              anchor: str = None,
              max_width: int = None) -> np.ndarray:
    """Renders crisp text onto an OpenCV uint8 image via PIL with language detection and auto-fit."""
    if not text:
        return img
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)

    if max_width:
        font, _ = fit_font(text, max_width, font_size)
    else:
        font = get_font_for_text(text, font_size)

    draw.text(pos, text, font=font, fill=fill_color, anchor=anchor)
    img[:] = np.array(pil_img)
    return img


def draw_emergency_banner(frame: np.ndarray,
                          text_bengali: str,
                          text_symbolic: str = "",
                          y_center: int = None,
                          banner_color: tuple = (178, 24, 24),
                          border_color: tuple = (212, 175, 55)) -> np.ndarray:
    """
    Renders the official Doordarshan emergency banner with safe-area auto-fit.
    Never clips across CRT curvature edges.
    """
    h, w = frame.shape[:2]
    if y_center is None:
        y_center = int(h * 0.32)

    # CRT Safe margin: 82% of screen width
    safe_w = int(w * 0.82)
    b_h = int(h * 0.12)
    y1 = y_center - b_h // 2
    y2 = y_center + b_h // 2

    x1 = (w - safe_w) // 2
    x2 = (w + safe_w) // 2

    # Draw banner background and gold border
    cv2.rectangle(frame, (x1, y1), (x2, y2), banner_color, -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, max(1, int(w / 640)))

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    # 1. Main Bengali Line (Auto-scaled to fit inside banner padding)
    content_max_w = safe_w - int(w * 0.05)
    target_bn_size = max(14, int(h * 0.042))
    font_bn, actual_bn_size = fit_font(text_bengali, content_max_w, target_bn_size, min_size=11)

    # 2. Symbolic / English Bureaucratic Sub-line
    target_sub_size = max(10, int(actual_bn_size * 0.65))
    if text_symbolic:
        font_sub, _ = fit_font(text_symbolic, content_max_w, target_sub_size, min_size=9)
        # Position with two lines
        line1_y = y_center - int(b_h * 0.20)
        line2_y = y_center + int(b_h * 0.22)
        draw.text((w // 2, line1_y), text_bengali, font=font_bn, fill=(255, 255, 255), anchor="mm")
        draw.text((w // 2, line2_y), text_symbolic, font=font_sub, fill=(245, 205, 55), anchor="mm")
    else:
        draw.text((w // 2, y_center), text_bengali, font=font_bn, fill=(255, 255, 255), anchor="mm")

    frame[:] = np.array(pil_img)
    return frame


def draw_rule_card(frame: np.ndarray,
                   rule_id: str,
                   text_bengali: str,
                   text_english: str = "",
                   y_start: int = None) -> np.ndarray:
    """Renders a mandatory Doordarshan emergency rule card at bottom with auto-fit."""
    h, w = frame.shape[:2]
    if y_start is None:
        y_start = int(h * 0.74)

    safe_w = int(w * 0.84)
    x1 = (w - safe_w) // 2
    x2 = (w + safe_w) // 2
    card_h = h - y_start - int(h * 0.04)

    # Dark translucent letterbox background
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y_start - 10), (x2, y_start + card_h), (8, 12, 18), -1)
    cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)
    cv2.rectangle(frame, (x1, y_start - 10), (x2, y_start + card_h), (178, 24, 24), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    content_max_w = safe_w - int(w * 0.04)
    f_id, _ = fit_font(rule_id, content_max_w, int(h * 0.032))
    f_bn, _ = fit_font(text_bengali, content_max_w, int(h * 0.034))

    draw.text((x1 + 16, y_start + 4), rule_id, font=f_id, fill=(94, 220, 120))
    draw.text((x1 + 16, y_start + int(h * 0.048)), text_bengali, font=f_bn, fill=(245, 245, 245))

    if text_english:
        f_en, _ = fit_font(text_english, content_max_w, int(h * 0.024))
        draw.text((x1 + 16, y_start + int(h * 0.098)), text_english, font=f_en, fill=(200, 220, 200))

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

    pad = int(w * 0.06)
    cv2.rectangle(frame, (pad + jitter_x, pad + jitter_y),
                  (w - pad + jitter_x, h - pad + jitter_y), (210, 205, 195), 2)
    cv2.rectangle(frame, (pad + 10 + jitter_x, pad + 10 + jitter_y),
                  (w - pad - 10 + jitter_x, h - pad - 10 + jitter_y), (130, 125, 120), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)
    content_max_w = w - 2 * pad - 40

    f_main, _ = fit_font(main_text, content_max_w, int(h * 0.052))
    cy = h // 2 + jitter_y - (int(h * 0.035) if sub_text else 0)
    draw.text((w // 2 + jitter_x, cy), main_text, font=f_main, fill=(245, 242, 235), anchor="mm")

    if sub_text:
        f_sub, _ = fit_font(sub_text, content_max_w, int(h * 0.032))
        draw.text((w // 2 + jitter_x, cy + int(h * 0.075)), sub_text, font=f_sub, fill=(185, 180, 170), anchor="mm")

    frame[:] = np.array(pil_img)
    return frame
