import uharfbuzz as hb
import freetype
import numpy as np
from PIL import Image

_SHAPED_CACHE = {}
_FT_FACE_CACHE = {}
_HB_FACE_CACHE = {}

def get_ft_face(font_path):
    if font_path not in _FT_FACE_CACHE:
        _FT_FACE_CACHE[font_path] = freetype.Face(font_path)
    return _FT_FACE_CACHE[font_path]

def get_hb_face(font_path):
    if font_path not in _HB_FACE_CACHE:
        with open(font_path, "rb") as f:
            _HB_FACE_CACHE[font_path] = hb.Face(f.read())
    return _HB_FACE_CACHE[font_path]

def render_shaped_patch(text, font_path, font_size, fill_color=(255, 255, 255)):
    key = (text, font_path, font_size, fill_color)
    if key in _SHAPED_CACHE:
        return _SHAPED_CACHE[key]

    ft_face = get_ft_face(font_path)
    ft_face.set_char_size(font_size * 64)

    hb_face = get_hb_face(font_path)
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
    height = int(font_size * 1.6)
    ascent = int(font_size * 1.25)
    width = max(total_w + 30, 20)

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

    pil_res = Image.fromarray(arr, mode="RGBA")
    _SHAPED_CACHE[key] = (pil_res, arr.shape[1], arr.shape[0])
    return _SHAPED_CACHE[key]

if __name__ == "__main__":
    p = "e:/betweenthenotes/noir_film_project/noir_film/fonts/NotoSansBengali-Bold.ttf"
    img, w, h = render_shaped_patch("“দরজা খুলবেন না। ওটা আপনার মা নয়।”", p, 52)
    print("Rendered patch width:", w, "height:", h)
    img.save("C:/Users/sayan/.gemini/antigravity/brain/b3d17fa9-62a2-4701-acdb-0633a94e4498/test_patch_shot_07.png")
