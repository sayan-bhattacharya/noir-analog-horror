"""
High-Precision TrueType OpenType Text Shaper for Project NOIR.
Uses uharfbuzz + freetype-py to render 100% authentic Bengali conjuncts, ligatures,
and matra reordering (e.g. 'খুলবেন', 'ধাক্কা', 'দিচ্ছে') with pixel-perfect accuracy
on any operating system (Windows, Linux, macOS).
"""
import os
import numpy as np
from PIL import Image

try:
    import freetype
    import uharfbuzz as hb
    _HAS_HARFBUZZ = True
except ImportError:
    _HAS_HARFBUZZ = False

_SHAPED_CACHE = {}
_FT_FACE_CACHE = {}
_HB_FACE_CACHE = {}


def is_shaping_available() -> bool:
    """Returns True if uharfbuzz and freetype-py are installed."""
    return _HAS_HARFBUZZ


def _get_ft_face(font_path: str):
    if font_path not in _FT_FACE_CACHE:
        _FT_FACE_CACHE[font_path] = freetype.Face(font_path)
    return _FT_FACE_CACHE[font_path]


def _get_hb_face(font_path: str):
    if font_path not in _HB_FACE_CACHE:
        with open(font_path, "rb") as f:
            _HB_FACE_CACHE[font_path] = hb.Face(f.read())
    return _HB_FACE_CACHE[font_path]


def render_shaped_patch(text: str,
                        font_path: str,
                        font_size: int,
                        fill_color: tuple = (255, 255, 255)):
    """
    Renders shaped OpenType text into an RGBA PIL Image using HarfBuzz + FreeType.
    Returns: (pil_rgba_image, width, height)
    """
    if not _HAS_HARFBUZZ or not os.path.exists(font_path) or not text:
        return None, 0, 0

    key = (text, font_path, font_size, fill_color)
    if key in _SHAPED_CACHE:
        return _SHAPED_CACHE[key]

    try:
        ft_face = _get_ft_face(font_path)
        ft_face.set_char_size(font_size * 64)

        hb_face = _get_hb_face(font_path)
        hb_font = hb.Font(hb_face)
        scale = int(font_size * 64)
        hb_font.scale = (scale, scale)

        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hb_font, buf)

        infos = buf.glyph_infos
        positions = buf.glyph_positions

        total_w = sum(pos.x_advance for pos in positions) >> 6
        height = max(10, int(font_size * 1.6))
        ascent = int(font_size * 1.25)
        width = max(total_w + 40, 20)

        arr = np.zeros((height, width, 4), dtype=np.uint8)

        x = 4
        for info, pos in zip(infos, positions):
            gid = info.codepoint
            ft_face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
            bitmap = ft_face.glyph.bitmap
            bx = x + (pos.x_offset >> 6) + ft_face.glyph.bitmap_left
            by = ascent - ft_face.glyph.bitmap_top - (pos.y_offset >> 6)

            bm_w = bitmap.width
            bm_h = bitmap.rows
            if bm_w > 0 and bm_h > 0:
                bm_arr = np.array(bitmap.buffer, dtype=np.uint8).reshape((bm_h, bm_w))
                y1, y2 = max(0, by), min(height, by + bm_h)
                x1, x2 = max(0, bx), min(width, bx + bm_w)
                sy1, sy2 = y1 - by, y1 - by + (y2 - y1)
                sx1, sx2 = x1 - bx, x1 - bx + (x2 - x1)
                if y2 > y1 and x2 > x1:
                    patch = bm_arr[sy1:sy2, sx1:sx2]
                    mask = patch > arr[y1:y2, x1:x2, 3]
                    for c in range(3):
                        arr[y1:y2, x1:x2, c] = np.where(mask, fill_color[c], arr[y1:y2, x1:x2, c])
                    arr[y1:y2, x1:x2, 3] = np.maximum(arr[y1:y2, x1:x2, 3], patch)

            x += (pos.x_advance >> 6)

        alpha_cols = np.where(arr[:, :, 3] > 0)[1]
        if len(alpha_cols) > 0:
            min_x = max(0, alpha_cols.min() - 2)
            max_x = min(width, alpha_cols.max() + 3)
            arr = arr[:, min_x:max_x]

        pil_res = Image.fromarray(arr)
        _SHAPED_CACHE[key] = (pil_res, arr.shape[1], arr.shape[0])
        return _SHAPED_CACHE[key]
    except Exception as e:
        return None, 0, 0


def draw_shaped_text(pil_img: Image.Image,
                     text: str,
                     pos: tuple,
                     font_path: str,
                     font_size: int,
                     fill_color: tuple = (255, 255, 255),
                     anchor: str = "mm",
                     with_shadow: bool = True,
                     shadow_color: tuple = (4, 4, 6)) -> bool:
    """
    Renders shaped text with optional drop shadow onto a PIL Image.
    Returns True if shaped text was drawn, False if fallback should be used.
    """
    patch, pw, ph = render_shaped_patch(text, font_path, font_size, fill_color)
    if patch is None or pw == 0 or ph == 0:
        return False

    px, py = pos

    # Anchor calculation
    if anchor == "mm":
        paste_x = px - pw // 2
        paste_y = py - ph // 2
    elif anchor in ("ma", "mt"):
        paste_x = px - pw // 2
        paste_y = py
    elif anchor in ("mb", "ms"):
        paste_x = px - pw // 2
        paste_y = py - ph
    elif anchor in ("la", "lt", None):
        paste_x = px
        paste_y = py
    elif anchor in ("lm",):
        paste_x = px
        paste_y = py - ph // 2
    elif anchor in ("ra", "rt"):
        paste_x = px - pw
        paste_y = py
    elif anchor in ("rm",):
        paste_x = px - pw
        paste_y = py - ph // 2
    else:
        paste_x = px - pw // 2
        paste_y = py - ph // 2

    # Draw shadow first
    if with_shadow:
        shadow_patch, sw, sh = render_shaped_patch(text, font_path, font_size, shadow_color)
        if shadow_patch is not None:
            for dx, dy in [(0, 2), (1, 1), (-1, 1), (0, -1)]:
                pil_img.paste(shadow_patch, (paste_x + dx, paste_y + dy), shadow_patch)

    pil_img.paste(patch, (paste_x, paste_y), patch)
    return True
