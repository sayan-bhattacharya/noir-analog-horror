"""
Text and Emergency Typography Overlay System for Project NOIR.
Upgraded to Broadcast Readability Standard matching 'Improve Broadcast Readability.png':
- Large, bold, crystal-clear typography with high contrast.
- Zero jitter / zero shimmer on text to guarantee effortless audience readability.
- Sleek CRT monitor bezel with extreme-edge RGB chromatic fringes (Cyan left, Amber/Red right).
- Full dual-engine font rendering for authentic Bengali and English typography.
"""
import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from . import bengali_shaper

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


def fit_font(text: str, max_width: int, initial_size: int, min_size: int = 12):
    """Auto-scales font size down until text bounding box fits within max_width."""
    size = initial_size
    fnt = get_font_for_text(text, size)
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
              max_width: int = None,
              with_shadow: bool = True) -> np.ndarray:
    """Renders crisp text onto an OpenCV uint8 image via PIL with language detection and clean contrast."""
    if not text:
        return img

    if has_bengali(text) and bengali_shaper.is_shaping_available():
        size = font_size
        if max_width:
            _, size = fit_font(text, max_width, font_size)
        pil_img = Image.fromarray(img)
        if bengali_shaper.draw_shaped_text(pil_img, text, pos, BENGALI_FONT_PATH, size,
                                           fill_color=fill_color, anchor=anchor, with_shadow=with_shadow):
            img[:] = np.array(pil_img)
            return img

    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)

    if max_width:
        font, _ = fit_font(text, max_width, font_size)
    else:
        font = get_font_for_text(text, font_size)

    # Clean drop shadow for maximum separation
    if with_shadow:
        px, py = pos
        for dx, dy in [(0, 1), (1, 1), (-1, 1)]:
            draw.text((px + dx, py + dy), text, font=font, fill=(5, 5, 5), anchor=anchor)

    draw.text(pos, text, font=font, fill=fill_color, anchor=anchor)
    img[:] = np.array(pil_img)
    return img


def draw_broadcast_readability_card(frame: np.ndarray,
                                    main_text: str,
                                    sub_text: str = "",
                                    t: float = 0.0) -> np.ndarray:
    """
    Renders an upgraded high-readability television dialogue card matching
    the exact aesthetic of 'Copy of Improve Broadcast Readability.png':
    - Sleek dark horizontal CRT screen container with metallic/gold bezel.
    - Subtle RGB chromatic aberration fringes strictly confined to outer left/right edges.
    - Large, bold, crystal-clear white Bengali typography without jitter or shimmer.
    - Crisp monospaced English subtitle inside brackets.
    """
    h, w = frame.shape[:2]

    # Background ambient: deep dark matte void
    frame[:, :] = [8, 8, 10]

    # CRT Monitor Screen container dimensions
    bw = int(w * 0.94)
    bh = int(h * 0.58)
    bx1 = (w - bw) // 2
    by1 = (h - bh) // 2
    bx2 = bx1 + bw
    by2 = by1 + bh

    # Outer Bezel: layered dark wood/metallic frame
    cv2.rectangle(frame, (bx1 - 8, by1 - 8), (bx2 + 8, by2 + 8), (20, 16, 14), -1)
    cv2.rectangle(frame, (bx1 - 8, by1 - 8), (bx2 + 8, by2 + 8), (45, 38, 30), 2)
    cv2.rectangle(frame, (bx1 - 4, by1 - 4), (bx2 + 4, by2 + 4), (12, 10, 8), 2)

    # Curved glass screen plate (dark charcoal with very subtle horizontal raster)
    screen = np.full((bh, bw, 3), 14, dtype=np.uint8)
    for y in range(0, bh, 2):
        screen[y, :] = np.clip(screen[y, :].astype(int) - 3, 0, 255)

    frame[by1:by2, bx1:bx2] = screen

    # Extreme edge chromatic fringes (Cyan on left, Red/Amber on right) - exactly as reference!
    for col in range(8):
        alpha = (8 - col) / 8.0
        # Left edge: Cyan/Blue phosphor fringe
        frame[by1:by2, bx1 + col, 0] = np.clip(frame[by1:by2, bx1 + col, 0] + int(180 * alpha), 0, 255)
        frame[by1:by2, bx1 + col, 1] = np.clip(frame[by1:by2, bx1 + col, 1] + int(140 * alpha), 0, 255)
        # Right edge: Red/Amber phosphor fringe
        frame[by1:by2, bx2 - 1 - col, 2] = np.clip(frame[by1:by2, bx2 - 1 - col, 2] + int(200 * alpha), 0, 255)
        frame[by1:by2, bx2 - 1 - col, 1] = np.clip(frame[by1:by2, bx2 - 1 - col, 1] + int(80 * alpha), 0, 255)

    # Inner screen border
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (36, 36, 44), 2)

    # Crisp typography via PIL
    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    content_max_w = bw - 80

    # Split main_text if it contains newline or split long quotes into two lines
    if "\n" in main_text:
        lines = main_text.split("\n")
    elif len(main_text) > 28 and "..." in main_text:
        parts = main_text.split("...")
        lines = [parts[0] + "...", parts[1].strip()]
    elif len(main_text) > 32 and " " in main_text:
        words = main_text.split(" ")
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        lines = [main_text]

    # Dynamic positioning based on 1 vs 2 lines
    if len(lines) >= 2:
        target_size = int(h * 0.072)  # ~52px on 720p
        f_main, size = fit_font(lines[0], content_max_w, target_size, min_size=32)
        y_l1 = by1 + int(bh * 0.28)
        y_l2 = by1 + int(bh * 0.54)
        y_sub = by1 + int(bh * 0.82)

        shaped_1 = False
        shaped_2 = False
        if bengali_shaper.is_shaping_available() and has_bengali(lines[0]):
            shaped_1 = bengali_shaper.draw_shaped_text(pil_img, lines[0], (w // 2, y_l1), BENGALI_FONT_PATH, size, fill_color=(255, 255, 255), anchor="mm")
            shaped_2 = bengali_shaper.draw_shaped_text(pil_img, lines[1], (w // 2, y_l2), BENGALI_FONT_PATH, size, fill_color=(255, 255, 255), anchor="mm")

        if not (shaped_1 and shaped_2):
            # Drop shadow for line 1 and 2
            for dx, dy in [(0, 2), (1, 1), (-1, 1), (0, -1)]:
                draw.text((w // 2 + dx, y_l1 + dy), lines[0], font=f_main, fill=(4, 4, 6), anchor="mm")
                draw.text((w // 2 + dx, y_l2 + dy), lines[1], font=f_main, fill=(4, 4, 6), anchor="mm")
            draw.text((w // 2, y_l1), lines[0], font=f_main, fill=(255, 255, 255), anchor="mm")
            draw.text((w // 2, y_l2), lines[1], font=f_main, fill=(255, 255, 255), anchor="mm")
    else:
        target_size = int(h * 0.078)  # ~56px on 720p
        f_main, size = fit_font(lines[0], content_max_w, target_size, min_size=34)
        y_main = by1 + int(bh * 0.42) if sub_text else (by1 + bh // 2)
        y_sub = by1 + int(bh * 0.78)

        shaped = False
        if bengali_shaper.is_shaping_available() and has_bengali(lines[0]):
            shaped = bengali_shaper.draw_shaped_text(pil_img, lines[0], (w // 2, y_main), BENGALI_FONT_PATH, size, fill_color=(255, 255, 255), anchor="mm")

        if not shaped:
            for dx, dy in [(0, 2), (1, 1), (-1, 1), (0, -1)]:
                draw.text((w // 2 + dx, y_main + dy), lines[0], font=f_main, fill=(4, 4, 6), anchor="mm")
            draw.text((w // 2, y_main), lines[0], font=f_main, fill=(255, 255, 255), anchor="mm")

    # Monospaced English Subtitle in brackets
    if sub_text:
        formatted_sub = sub_text if sub_text.startswith("[") else f"[ {sub_text} ]"
        f_sub, _ = fit_font(formatted_sub, content_max_w, int(h * 0.035), min_size=18)
        for dx, dy in [(0, 1), (1, 1)]:
            draw.text((w // 2 + dx, y_sub + dy), formatted_sub, font=f_sub, fill=(4, 4, 6), anchor="mm")
        draw.text((w // 2, y_sub), formatted_sub, font=f_sub, fill=(235, 235, 240), anchor="mm")

    frame[:] = np.array(pil_img)
    return frame


def draw_silent_film_intertitle(frame: np.ndarray,
                                main_text: str,
                                sub_text: str = "",
                                t: float = 0.0) -> np.ndarray:
    """Direct alias to draw_broadcast_readability_card for seamless 100% readability across the film."""
    return draw_broadcast_readability_card(frame, main_text, sub_text, t=t)


def draw_rule_card(frame: np.ndarray,
                   rule_id: str,
                   text_bengali: str,
                   text_english: str = "",
                   y_start: int = None) -> np.ndarray:
    """Renders a high-contrast, large-typography emergency rule card at bottom with zero jitter."""
    h, w = frame.shape[:2]
    if y_start is None:
        y_start = int(h * 0.70)

    safe_w = int(w * 0.88)
    x1 = (w - safe_w) // 2
    x2 = (w + safe_w) // 2
    card_h = h - y_start - int(h * 0.03)

    # Dark high-contrast background with deep red/amber border
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y_start), (x2, y_start + card_h), (8, 10, 14), -1)
    cv2.addWeighted(overlay, 0.90, frame, 0.10, 0, frame)
    cv2.rectangle(frame, (x1, y_start), (x2, y_start + card_h), (185, 24, 24), 2)
    cv2.rectangle(frame, (x1 + 3, y_start + 3), (x2 - 3, y_start + card_h - 3), (40, 40, 48), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    content_max_w = safe_w - int(w * 0.04)
    id_size = int(h * 0.034)
    f_bn, bn_size = fit_font(text_bengali, content_max_w, int(h * 0.040), min_size=20)

    # Draw Rule ID: cleanly split Bengali and Latin parts so zero tofu boxes occur
    if "(" in rule_id and ")" in rule_id and has_bengali(rule_id):
        parts = rule_id.split("(")
        bn_part = parts[0].strip()
        en_part = "(" + parts[1].strip()
        offset_x = 0
        if bengali_shaper.is_shaping_available():
            bengali_shaper.draw_shaped_text(pil_img, bn_part, (x1 + 20, y_start + 6), BENGALI_FONT_PATH, id_size, fill_color=(90, 235, 120), anchor="la", with_shadow=False)
            _, pw, _ = bengali_shaper.render_shaped_patch(bn_part, BENGALI_FONT_PATH, id_size)
            offset_x = pw + 12
        else:
            f_bn_id = get_bengali_font(id_size)
            draw.text((x1 + 20, y_start + 6), bn_part, font=f_bn_id, fill=(90, 235, 120))
            offset_x = int(draw.textlength(bn_part, font=f_bn_id)) + 12

        f_en_id = get_english_font(id_size)
        draw.text((x1 + 20 + offset_x, y_start + 6), en_part, font=f_en_id, fill=(90, 235, 120))
    else:
        if has_bengali(rule_id) and bengali_shaper.is_shaping_available():
            bengali_shaper.draw_shaped_text(pil_img, rule_id, (x1 + 20, y_start + 6), BENGALI_FONT_PATH, id_size, fill_color=(90, 235, 120), anchor="la", with_shadow=False)
        else:
            f_id, _ = fit_font(rule_id, content_max_w, id_size, min_size=18)
            draw.text((x1 + 20, y_start + 6), rule_id, font=f_id, fill=(90, 235, 120))
    # Draw Bengali Rule Text in bold white with drop shadow
    shaped_rule = False
    if bengali_shaper.is_shaping_available() and has_bengali(text_bengali):
        shaped_rule = bengali_shaper.draw_shaped_text(pil_img, text_bengali, (x1 + 20, y_start + int(h * 0.050)), BENGALI_FONT_PATH, bn_size, fill_color=(255, 255, 255), anchor="la", with_shadow=True)

    if not shaped_rule:
        draw.text((x1 + 21, y_start + int(h * 0.050) + 1), text_bengali, font=f_bn, fill=(4, 4, 6))
        draw.text((x1 + 20, y_start + int(h * 0.050)), text_bengali, font=f_bn, fill=(255, 255, 255))

    if text_english:
        f_en, _ = fit_font(text_english, content_max_w, int(h * 0.026), min_size=14)
        draw.text((x1 + 21, y_start + int(h * 0.108) + 1), text_english, font=f_en, fill=(4, 4, 6))
        draw.text((x1 + 20, y_start + int(h * 0.108)), text_english, font=f_en, fill=(215, 230, 215))

    frame[:] = np.array(pil_img)
    return frame


def draw_emergency_banner(frame: np.ndarray,
                          text_bengali: str,
                          text_symbolic: str = "",
                          y_center: int = None,
                          banner_color: tuple = (178, 24, 24),
                          border_color: tuple = (212, 175, 55)) -> np.ndarray:
    """Renders the official Doordarshan emergency banner with safe-area auto-fit."""
    h, w = frame.shape[:2]
    if y_center is None:
        y_center = int(h * 0.32)

    safe_w = int(w * 0.84)
    b_h = int(h * 0.14)
    y1 = y_center - b_h // 2
    y2 = y_center + b_h // 2
    x1 = (w - safe_w) // 2
    x2 = (w + safe_w) // 2

    cv2.rectangle(frame, (x1, y1), (x2, y2), banner_color, -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), border_color, 2)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    content_max_w = safe_w - int(w * 0.05)
    target_bn_size = max(18, int(h * 0.048))
    font_bn, actual_bn_size = fit_font(text_bengali, content_max_w, target_bn_size, min_size=14)

    target_sub_size = max(12, int(actual_bn_size * 0.65))
    if text_symbolic:
        font_sub, _ = fit_font(text_symbolic, content_max_w, target_sub_size, min_size=10)
        line1_y = y_center - int(b_h * 0.20)
        line2_y = y_center + int(b_h * 0.22)
        draw.text((w // 2, line1_y), text_bengali, font=font_bn, fill=(255, 255, 255), anchor="mm")
        draw.text((w // 2, line2_y), text_symbolic, font=font_sub, fill=(245, 205, 55), anchor="mm")
    else:
        draw.text((w // 2, y_center), text_bengali, font=font_bn, fill=(255, 255, 255), anchor="mm")

    frame[:] = np.array(pil_img)
    return frame


def draw_minimal_end_credits(frame: np.ndarray, t: float = 0.0) -> np.ndarray:
    """
    Renders pure, minimalist, elegant end credits for Project NOIR:
    PRESENTED BY BETWEEN THE NOTES
    AN ANALOG HORROR FILM
    ORIGINAL SCORE & SOUND DESIGN: ATANDRA
    VISUAL ENGINE & DIRECTION: SAYAN
    IN CASE OF NISHIDAK: DO NOT ANSWER
    """
    h, w = frame.shape[:2]
    frame[:, :] = [6, 6, 8]

    # Subtle vignette shadow
    cv2.rectangle(frame, (20, 20), (w - 20, h - 20), (18, 16, 20), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    f_pres = get_english_font(int(h * 0.024))
    f_brand = get_english_font(int(h * 0.054))
    f_sub = get_english_font(int(h * 0.026))
    f_role = get_english_font(int(h * 0.022))
    f_name = get_english_font(int(h * 0.038))
    f_warn = get_english_font(int(h * 0.026))

    # Medallion graphic in gold/silver
    cx = w // 2
    cy_logo = int(h * 0.16)
    cv2.circle(frame, (cx, cy_logo), int(h * 0.05), (190, 160, 50), 2)
    cv2.circle(frame, (cx, cy_logo), int(h * 0.042), (90, 80, 30), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    # 1. Header: PRESENTED BY BETWEEN THE NOTES
    draw.text((cx, int(h * 0.26)), "PRESENTED BY", font=f_pres, fill=(160, 160, 165), anchor="mm")
    draw.text((cx, int(h * 0.33)), "BETWEEN THE NOTES", font=f_brand, fill=(245, 245, 250), anchor="mm")

    # 2. Subtitle: AN ANALOG HORROR FILM
    draw.text((cx, int(h * 0.42)), "AN ANALOG HORROR FILM", font=f_sub, fill=(185, 40, 40), anchor="mm")

    # Thin dividing rule
    rule_y = int(h * 0.48)
    cv2.line(frame, (cx - int(w * 0.18), rule_y), (cx + int(w * 0.18), rule_y), (60, 55, 65), 1)
    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    # 3. Credits
    draw.text((cx, int(h * 0.55)), "ORIGINAL SCORE & SOUND DESIGN", font=f_role, fill=(140, 140, 145), anchor="mm")
    draw.text((cx, int(h * 0.60)), "ATANDRA", font=f_name, fill=(240, 240, 245), anchor="mm")

    draw.text((cx, int(h * 0.69)), "VISUAL ENGINE & DIRECTION", font=f_role, fill=(140, 140, 145), anchor="mm")
    draw.text((cx, int(h * 0.74)), "SAYAN", font=f_name, fill=(240, 240, 245), anchor="mm")

    # 4. Terminal Warning Box
    warn_y = int(h * 0.86)
    box_w = int(w * 0.42)
    cv2.rectangle(frame, (cx - box_w // 2, warn_y - 14), (cx + box_w // 2, warn_y + 16), (25, 10, 10), -1)
    cv2.rectangle(frame, (cx - box_w // 2, warn_y - 14), (cx + box_w // 2, warn_y + 16), (195, 25, 25), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)
    draw.text((cx, warn_y), "IN CASE OF NISHIDAK: DO NOT ANSWER", font=f_warn, fill=(245, 60, 60), anchor="mm")

    frame[:] = np.array(pil_img)
    return frame
