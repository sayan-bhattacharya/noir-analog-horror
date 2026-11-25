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


def _split_script_runs(text: str) -> list:
    """
    Splits mixed Bengali + Latin/ASCII text into contiguous (is_bengali, substring) runs
    so Bengali runs use NotoSansBengali + HarfBuzz and Latin/symbol runs use IBMPlexMono,
    eliminating all square 'tofu' boxes.
    """
    runs = []
    current = []
    curr_bn = None

    for ch in text:
        code = ord(ch)
        is_bn_char = (0x0980 <= code <= 0x09FF)
        if ch in " \t":
            # Keep spaces attached to the active run
            if curr_bn is None:
                curr_bn = False
            current.append(ch)
            continue

        # Punctuation like |, •, :, -, [, ], (, ), ., , work cleanly in Latin font;
        # Bengali danda '।' (0x0964) / '॥' (0x0965) belong to Bengali font.
        if code in (0x0964, 0x0965):
            is_bn_char = True

        if curr_bn is None:
            curr_bn = is_bn_char
            current.append(ch)
        elif is_bn_char == curr_bn:
            current.append(ch)
        else:
            runs.append((curr_bn, "".join(current)))
            current = [ch]
            curr_bn = is_bn_char

    if current:
        runs.append((bool(curr_bn), "".join(current)))
    return runs


def _measure_mixed_width(runs: list, size: int) -> int:
    """Measures total pixel width of mixed-script runs."""
    tmp = Image.new("RGB", (1, 1))
    d = ImageDraw.Draw(tmp)
    f_en = get_english_font(size)
    f_bn = get_bengali_font(size)
    total_w = 0
    for is_bn, seg in runs:
        if is_bn and bengali_shaper.is_shaping_available():
            _, pw, _ = bengali_shaper.render_shaped_patch(seg, BENGALI_FONT_PATH, size)
            total_w += pw
        elif is_bn:
            bbox = d.textbbox((0, 0), seg, font=f_bn)
            total_w += (bbox[2] - bbox[0])
        else:
            bbox = d.textbbox((0, 0), seg, font=f_en)
            total_w += (bbox[2] - bbox[0])
    return total_w


def fit_font(text: str, max_width: int, initial_size: int, min_size: int = 12):
    """Auto-scales font size down until mixed-script text fits within max_width."""
    size = initial_size
    runs = _split_script_runs(text)
    while size > min_size:
        w = _measure_mixed_width(runs, size)
        if w <= max_width:
            break
        size -= 1
    return get_font_for_text(text, size), size


def draw_text(img: np.ndarray,
              text: str,
              pos: tuple,
              font_size: int = 24,
              fill_color: tuple = (240, 240, 240),
              anchor: str = None,
              max_width: int = None,
              with_shadow: bool = True) -> np.ndarray:
    """Renders crisp mixed-script text onto an OpenCV uint8 image with zero tofu boxes."""
    if not text:
        return img

    size = font_size
    if max_width:
        _, size = fit_font(text, max_width, font_size)

    runs = _split_script_runs(text)
    pil_img = Image.fromarray(img)

    # Pure single-script fast path
    if len(runs) == 1:
        is_bn, seg = runs[0]
        if is_bn and bengali_shaper.is_shaping_available():
            if bengali_shaper.draw_shaped_text(pil_img, seg, pos, BENGALI_FONT_PATH, size,
                                               fill_color=fill_color, anchor=anchor, with_shadow=with_shadow):
                img[:] = np.array(pil_img)
                return img

    # Mixed-script (or pure Latin) segmented rendering: zero tofu glyphs guaranteed
    total_w = _measure_mixed_width(runs, size)
    px, py = pos
    anchor_str = anchor or "la"
    h_align = anchor_str[0] if len(anchor_str) >= 1 else "l"
    v_align = anchor_str[1] if len(anchor_str) >= 2 else "a"

    if h_align == "m":
        cur_x = int(px - total_w / 2.0)
    elif h_align == "r":
        cur_x = int(px - total_w)
    else:
        cur_x = int(px)

    draw = ImageDraw.Draw(pil_img)
    f_en = get_english_font(size)
    f_bn = get_bengali_font(size)

    for is_bn, seg in runs:
        if not seg:
            continue
        if is_bn and bengali_shaper.is_shaping_available():
            _, pw, _ = bengali_shaper.render_shaped_patch(seg, BENGALI_FONT_PATH, size)
            bengali_shaper.draw_shaped_text(pil_img, seg, (cur_x, py), BENGALI_FONT_PATH, size,
                                            fill_color=fill_color, anchor=f"l{v_align}", with_shadow=with_shadow)
            cur_x += pw
        else:
            fnt = f_bn if is_bn else f_en
            if with_shadow:
                for dx, dy in [(0, 1), (1, 1), (-1, 1)]:
                    draw.text((cur_x + dx, py + dy), seg, font=fnt, fill=(5, 5, 5), anchor=f"l{v_align}")
            draw.text((cur_x, py), seg, font=fnt, fill=fill_color, anchor=f"l{v_align}")
            bbox = draw.textbbox((0, 0), seg, font=fnt)
            cur_x += max(int(draw.textlength(seg, font=fnt)), bbox[2] - bbox[0])

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
    """
    Renders a vintage 1994 Doordarshan / broadcast archival advisory rule card:
    - Double-bevel archival brass/amber outer border + deep crimson top header bar
    - Warm CRT ivory Bengali typography (auto-wrapped to 2 lines if long, hyper-visible)
    - Vintage amber IBMPlexMono-Bold English subtitle
    """
    h, w = frame.shape[:2]
    if y_start is None:
        y_start = int(h * 0.61)
    else:
        y_start = min(y_start, int(h * 0.62))

    safe_w = int(w * 0.90)
    x1 = (w - safe_w) // 2
    x2 = (w + safe_w) // 2
    card_h = h - y_start - int(h * 0.03)
    y2 = y_start + card_h

    # Solid 95% dark vintage slate backdrop for hyper-visibility
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y_start), (x2, y2), (10, 11, 14), -1)
    cv2.addWeighted(overlay, 0.95, frame, 0.05, 0, frame)

    # Vintage crimson broadcast header strip inside card
    hdr_h = int(h * 0.052)
    cv2.rectangle(frame, (x1, y_start), (x2, y_start + hdr_h), (142, 22, 24), -1)

    # Archival double-bevel brass/gold frame
    cv2.rectangle(frame, (x1, y_start), (x2, y2), (212, 175, 72), 2)
    cv2.rectangle(frame, (x1 + 4, y_start + 4), (x2 - 4, y2 - 4), (96, 82, 46), 1)

    # Header bar text: Rule ID on left, Vintage Advisory Tag on right
    draw_text(
        frame, rule_id, (x1 + 20, y_start + hdr_h // 2),
        font_size=int(h * 0.028), fill_color=(255, 232, 145), anchor="lm", with_shadow=True
    )
    draw_text(
        frame, "CIVIL DEFENSE ADVISORY // জরুরি নির্দেশিকা", (x2 - 20, y_start + hdr_h // 2),
        font_size=int(h * 0.021), fill_color=(248, 242, 225), anchor="rm", with_shadow=True
    )

    content_max_w = safe_w - 44
    # Wrap long Bengali rule into 2 balanced lines if needed so font stays large & hyper-visible
    bn_lines = [text_bengali]
    if len(text_bengali) > 42 and " " in text_bengali:
        words = text_bengali.split(" ")
        mid = len(words) // 2
        bn_lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    bn_y_top = y_start + hdr_h + int(card_h * 0.14)
    if len(bn_lines) == 1:
        draw_text(
            frame, bn_lines[0], (w // 2, bn_y_top + int(h * 0.022)),
            font_size=int(h * 0.044), fill_color=(252, 248, 234),
            anchor="mm", max_width=content_max_w, with_shadow=True
        )
        en_y = y2 - int(card_h * 0.17)
    else:
        draw_text(
            frame, bn_lines[0], (w // 2, bn_y_top + int(h * 0.010)),
            font_size=int(h * 0.041), fill_color=(252, 248, 234),
            anchor="mm", max_width=content_max_w, with_shadow=True
        )
        draw_text(
            frame, bn_lines[1], (w // 2, bn_y_top + int(h * 0.062)),
            font_size=int(h * 0.041), fill_color=(252, 248, 234),
            anchor="mm", max_width=content_max_w, with_shadow=True
        )
        en_y = y2 - int(card_h * 0.12)

    if text_english:
        draw_text(
            frame, text_english, (w // 2, en_y),
            font_size=int(h * 0.024), fill_color=(242, 204, 96),
            anchor="mm", max_width=content_max_w, with_shadow=True
        )

    return frame


def draw_intercepted_question_signal(frame: np.ndarray, t: float) -> np.ndarray:
    """A single crimson question mark carried by a clean Morse-style signal."""
    h, w = frame.shape[:2]
    frame[:] = (4, 4, 10)
    # Quiet scanline field and signal baseline.
    for y in range(0, h, max(4, h // 90)):
        cv2.line(frame, (int(w * .12), y), (int(w * .88), y), (12, 8, 18), 1)
    red = (235, 35, 28)  # RGB crimson in the rendered frame buffer
    glow = frame.copy()
    cy = int(h * .44)
    text_overlay_size = int(h * .42)
    draw_text(frame, "?", (w // 2, cy), font_size=text_overlay_size,
              fill_color=red, anchor="mm", with_shadow=False)

    # Morse question mark: ..--.. Each pulse sits on one shared carrier line.
    unit = max(5, int(w * .012))
    gap = max(4, unit)
    pulse_units = [1, 1, 3, 3, 1, 1]
    total = sum(pulse_units) * unit + (len(pulse_units) - 1) * gap
    x = (w - total) // 2
    baseline = int(h * .76)
    cv2.line(frame, (int(w * .18), baseline), (int(w * .82), baseline), (45, 18, 38), 1, cv2.LINE_AA)
    pulse = .72 + .28 * math.sin(t * 2 * math.pi * 1.6)
    for length in pulse_units:
        width = length * unit
        y_top = baseline - (int(h * .11) if length == 3 else int(h * .06))
        cv2.rectangle(frame, (x, y_top), (x + width, baseline), red, -1)
        x += width + gap
    cv2.addWeighted(frame, pulse, glow, 1.0 - pulse, 0, frame)
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


_MEL_BG_CACHE = None


def _get_mel_spectrogram_bg(w: int, h: int) -> np.ndarray:
    global _MEL_BG_CACHE
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mel_path = os.path.join(root_dir, "assets", "noir_mel_spectrogram_bg.png")
    if _MEL_BG_CACHE is None and os.path.exists(mel_path):
        bgr = cv2.imread(mel_path)
        if bgr is not None:
            _MEL_BG_CACHE = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    if _MEL_BG_CACHE is not None:
        if _MEL_BG_CACHE.shape[1] != w or _MEL_BG_CACHE.shape[0] != h:
            return cv2.resize(_MEL_BG_CACHE, (w, h), interpolation=cv2.INTER_AREA)
        return _MEL_BG_CACHE.copy()
    return None


def draw_minimal_end_credits(frame: np.ndarray, t: float = 0.0) -> np.ndarray:
    """
    Renders pure, minimalist, elegant end credits for Project NOIR // NISHIDAK
    layered over the live Mel Spectrogram of Noir.wav + crimson laser-pointer playhead.
    """
    h, w = frame.shape[:2]
    mel_bg = _get_mel_spectrogram_bg(w, h)
    if mel_bg is not None:
        frame[:] = mel_bg
        # Crimson laser-pointer playhead sweeping smoothly across the spectrogram
        lx = int(((t / 13.0) % 1.0) * w)
        cv2.line(frame, (lx, 0), (lx, h), (185, 25, 30), 2)
        cv2.circle(frame, (lx, int(h * 0.80)), 6, (255, 70, 70), -1, cv2.LINE_AA)
        cv2.circle(frame, (lx, int(h * 0.80)), 2, (255, 235, 235), -1, cv2.LINE_AA)
    else:
        frame[:, :] = [6, 6, 8]

    # Subtle vignette border
    cv2.rectangle(frame, (20, 20), (w - 20, h - 20), (45, 35, 40), 1)

    # All OpenCV vector shapes drawn BEFORE converting to PIL once
    cx = w // 2
    cy_logo = int(h * 0.16)
    cv2.circle(frame, (cx, cy_logo), int(h * 0.05), (212, 175, 55), 2, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy_logo), int(h * 0.042), (120, 95, 35), 1, cv2.LINE_AA)

    rule_y = int(h * 0.48)
    cv2.line(frame, (cx - int(w * 0.18), rule_y), (cx + int(w * 0.18), rule_y), (140, 110, 120), 1)

    warn_y = int(h * 0.86)
    box_w = int(w * 0.44)
    cv2.rectangle(frame, (cx - box_w // 2, warn_y - 16), (cx + box_w // 2, warn_y + 18), (18, 6, 8), -1)
    cv2.rectangle(frame, (cx - box_w // 2, warn_y - 16), (cx + box_w // 2, warn_y + 18), (215, 45, 45), 1)

    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    f_pres = get_english_font(int(h * 0.024))
    f_brand = get_english_font(int(h * 0.054))
    f_sub = get_english_font(int(h * 0.026))
    f_role = get_english_font(int(h * 0.022))
    f_name = get_english_font(int(h * 0.038))
    f_warn = get_english_font(int(h * 0.026))

    def _txt_shadow(pos, s, font, fill):
        draw.text((pos[0] + 2, pos[1] + 2), s, font=font, fill=(4, 4, 6), anchor="mm")
        draw.text(pos, s, font=font, fill=fill, anchor="mm")

    _txt_shadow((cx, int(h * 0.26)), "PRESENTED BY", f_pres, (205, 205, 210))
    _txt_shadow((cx, int(h * 0.33)), "BETWEEN THE NOTES", f_brand, (250, 245, 235))
    _txt_shadow((cx, int(h * 0.42)), "NOIR // NISHIDAK  •  AN ANALOG HORROR FILM", f_sub, (240, 75, 75))
    _txt_shadow((cx, int(h * 0.55)), "ORIGINAL SCORE & SOUND DESIGN", f_role, (195, 195, 205))
    _txt_shadow((cx, int(h * 0.60)), "ATANDRA", f_name, (245, 245, 250))
    _txt_shadow((cx, int(h * 0.69)), "VISUAL ENGINE & DIRECTION", f_role, (195, 195, 205))
    _txt_shadow((cx, int(h * 0.74)), "SAYAN", f_name, (245, 245, 250))
    _txt_shadow((cx, warn_y), "IN CASE OF NISHIDAK: DO NOT ANSWER", f_warn, (250, 75, 75))

    frame[:] = np.array(pil_img)
    return frame
