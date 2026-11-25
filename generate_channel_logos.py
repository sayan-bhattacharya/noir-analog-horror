"""
Generates 3 broadcast-ready Television Channel Logos for Between the Notes:
1. Station Crest (BTN // BETWEEN THE NOTES)
2. 24-Hour News Channel Corner Bug (BTN 24 // বিটুইন দ্য নোটস)
3. Truman-Show Cable Surveillance Channel Logo (CH 07 // LIVE FEED)
"""
import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import sys
sys.path.insert(0, r"e:\betweenthenotes\noir_film_project")
from noir_film import bengali_shaper

ROOT = r"e:\betweenthenotes\noir_film_project"
LOGO_PATH = os.path.join(ROOT, "assets", "logo-circle.png")
EN_FONT = os.path.join(ROOT, "noir_film", "fonts", "IBMPlexMono-Bold.ttf")
BN_FONT = os.path.join(ROOT, "noir_film", "fonts", "NotoSansBengali-Bold.ttf")
OUT_DIR = r"C:\Users\sayan\.gemini\antigravity\brain\b3d17fa9-62a2-4701-acdb-0633a94e4498"
ASSETS_DIR = os.path.join(ROOT, "assets")


def load_emblem(size: int) -> Image.Image:
    if os.path.exists(LOGO_PATH):
        im = Image.open(LOGO_PATH).convert("RGBA")
        return im.resize((size, size), Image.Resampling.LANCZOS)
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, size - 4, size - 4], outline=(245, 205, 55, 255), width=6)
    return im


def build_logo_01_station_crest():
    W, H = 1024, 1024
    img = Image.new("RGBA", (W, H), (14, 13, 38, 255))
    draw = ImageDraw.Draw(img)

    # Subtle radial broadcast glow behind emblem
    cx, cy = W // 2, 370
    for r in range(280, 120, -4):
        alpha = int(18 * (1.0 - (r - 120) / 160.0))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 205, 55, alpha))

    # Concentric gold broadcast rings with degree tick marks
    draw.ellipse([cx - 215, cy - 215, cx + 215, cy + 215], outline=(245, 205, 55, 200), width=4)
    draw.ellipse([cx - 236, cy - 236, cx + 236, cy + 236], outline=(212, 175, 55, 90), width=2)
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        r1 = 222
        r2 = 234 if deg % 45 == 0 else 228
        x1, y1 = cx + math.cos(rad) * r1, cy + math.sin(rad) * r1
        x2, y2 = cx + math.cos(rad) * r2, cy + math.sin(rad) * r2
        draw.line([x1, y1, x2, y2], fill=(245, 205, 55, 180), width=3 if deg % 45 == 0 else 1)

    # Paste official Between the Notes emblem
    emblem = load_emblem(390)
    img.paste(emblem, (cx - 195, cy - 195), emblem)

    # Crimson "BTN TV" call-sign pill
    pill_w, pill_h = 260, 64
    px1, py1 = cx - pill_w // 2, 625
    draw.rounded_rectangle([px1, py1, px1 + pill_w, py1 + pill_h], radius=10,
                           fill=(185, 20, 25, 255), outline=(245, 205, 55, 255), width=3)
    f_call = ImageFont.truetype(EN_FONT, 38)
    draw.text((cx, py1 + pill_h // 2), "BTN TV", font=f_call, fill=(255, 255, 255, 255), anchor="mm")

    # Main Title
    f_main = ImageFont.truetype(EN_FONT, 58)
    draw.text((cx, 745), "BETWEEN THE NOTES", font=f_main, fill=(245, 210, 65, 255), anchor="mm")

    # Bengali Network Subtitle using HarfBuzz shaper
    bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)
    pil_bgr = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    bengali_shaper.draw_shaped_text(
        pil_bgr, "বিটুইন দ্য নোটস সম্প্রচার নেটওয়ার্ক",
        (cx, 825), BN_FONT, 36, fill_color=(215, 225, 235), anchor="mm", with_shadow=True
    )
    f_sub = ImageFont.truetype(EN_FONT, 24)
    d2 = ImageDraw.Draw(pil_bgr)
    d2.text((cx, 890), "EST. 1994  •  CALCUTTA  •  CH 03 / CH 07", font=f_sub, fill=(140, 165, 185), anchor="mm")

    out_path = os.path.join(OUT_DIR, "btn_channel_logo_01_station_crest.png")
    pil_bgr.save(out_path)
    pil_bgr.save(os.path.join(ASSETS_DIR, "btn_channel_logo_01_station_crest.png"))
    return out_path


def build_logo_02_news_bug():
    W, H = 1200, 600
    # Solid dark studio slate background for crisp presentation
    img = Image.new("RGBA", (W, H), (10, 12, 18, 255))
    draw = ImageDraw.Draw(img)

    # Angled Crimson + Navy News Shield in center
    bx1, by1 = 140, 130
    bw, bh = 920, 220
    shear = 42

    # Navy main body
    poly_navy = [(bx1, by1), (bx1 + bw, by1), (bx1 + bw - shear, by1 + bh), (bx1 - shear, by1 + bh)]
    draw.polygon(poly_navy, fill=(18, 22, 46, 255), outline=(235, 215, 65, 255))

    # Crimson left accent block
    c_w = 290
    poly_red = [(bx1, by1), (bx1 + c_w, by1), (bx1 + c_w - shear, by1 + bh), (bx1 - shear, by1 + bh)]
    draw.polygon(poly_red, fill=(185, 20, 25, 255))

    # White diagonal broadcast slashes
    draw.line([(bx1 + c_w - 18, by1 + 10), (bx1 + c_w - shear - 18, by1 + bh - 10)], fill=(255, 255, 255, 240), width=6)
    draw.line([(bx1 + c_w - 4, by1 + 10), (bx1 + c_w - shear - 4, by1 + bh - 10)], fill=(245, 210, 60, 240), width=4)

    # Paste official circular logo on left
    emblem = load_emblem(164)
    img.paste(emblem, (bx1 + 38, by1 + 28), emblem)

    # Text on Navy panel
    f_btn = ImageFont.truetype(EN_FONT, 72)
    draw.text((bx1 + 335, by1 + 78), "BTN 24", font=f_btn, fill=(255, 255, 255, 255), anchor="lm")

    f_live = ImageFont.truetype(EN_FONT, 30)
    draw.rounded_rectangle([bx1 + 650, by1 + 46, bx1 + 835, by1 + 104], radius=8, fill=(210, 25, 30, 255))
    draw.ellipse([bx1 + 668, by1 + 64, bx1 + 690, by1 + 86], fill=(255, 255, 255, 255))
    draw.text((bx1 + 704, by1 + 75), "LIVE", font=f_live, fill=(255, 255, 255, 255), anchor="lm")

    f_en_sub = ImageFont.truetype(EN_FONT, 32)
    draw.text((bx1 + 335, by1 + 162), "BETWEEN THE NOTES NEWS", font=f_en_sub, fill=(245, 210, 65, 255), anchor="lm")

    # Lower gold/charcoal Bengali News Bar
    sub_y = by1 + bh + 18
    poly_bar = [(bx1 - shear, sub_y), (bx1 + bw - shear, sub_y), (bx1 + bw - shear * 1.3, sub_y + 78), (bx1 - shear * 1.3, sub_y + 78)]
    draw.polygon(poly_bar, fill=(24, 26, 36, 255), outline=(185, 20, 25, 255))

    rgb_img = img.convert("RGB")
    bengali_shaper.draw_shaped_text(
        rgb_img, "বিটুইন দ্য নোটস ২৪  •  সরাসরি জরুরি সংবাদ",
        (W // 2 - 20, sub_y + 39), BN_FONT, 34, fill_color=(245, 245, 245), anchor="mm", with_shadow=True
    )

    out_path = os.path.join(OUT_DIR, "btn_channel_logo_02_news_bug.png")
    rgb_img.save(out_path)
    rgb_img.save(os.path.join(ASSETS_DIR, "btn_channel_logo_02_news_bug.png"))
    return out_path


def build_logo_03_ch07_cable():
    W, H = 1024, 1024
    img = Image.new("RGB", (W, H), (5, 6, 9))
    draw = ImageDraw.Draw(img)

    # Subtle CRT scanlines
    for y in range(0, H, 4):
        draw.line([(0, y), (W, y)], fill=(10, 14, 12), width=1)

    # Outer CRT Monitor Bezel Frame
    draw.rounded_rectangle([120, 140, 904, 740], radius=56, outline=(90, 235, 120), width=5)
    draw.rounded_rectangle([142, 162, 882, 718], radius=42, outline=(40, 110, 60), width=2)

    # Center Eye/Keyhole/Wave Motif
    cx, cy = W // 2, 410
    # Concentric descending spiral/hole
    for i in range(6):
        r = 145 - i * 20
        col = (240, 60, 60) if i % 2 == 0 else (90, 235, 120)
        draw.ellipse([cx - r, cy - int(r * 0.72), cx + r, cy + int(r * 0.72)], outline=col, width=3)

    # Oscilloscope wave across center
    pts = []
    for x in range(180, 844, 6):
        dist = abs(x - cx)
        env = math.exp(-(dist / 160.0) ** 2)
        y = cy + math.sin(x * 0.08) * 62 * env
        pts.append((x, y))
    draw.line(pts, fill=(90, 235, 120), width=4)

    # Top-left REC dot inside monitor
    draw.ellipse([185, 200, 213, 228], fill=(240, 55, 55))
    f_rec = ImageFont.truetype(EN_FONT, 30)
    draw.text((230, 214), "REC // LIVE FEED", font=f_rec, fill=(240, 55, 55), anchor="lm")

    # Channel Number Badge
    f_ch = ImageFont.truetype(EN_FONT, 42)
    draw.text((840, 214), "CH 07", font=f_ch, fill=(90, 235, 120), anchor="rm")

    # Bottom typography
    f_title = ImageFont.truetype(EN_FONT, 50)
    draw.text((cx, 815), "CH 07 // BETWEEN THE NOTES", font=f_title, fill=(90, 235, 120), anchor="mm")

    bengali_shaper.draw_shaped_text(
        img, "বিটুইন দ্য নোটস  •  অবতরণ নজরদারি চ্যানেল",
        (cx, 890), BN_FONT, 32, fill_color=(230, 235, 230), anchor="mm", with_shadow=True
    )

    out_path = os.path.join(OUT_DIR, "btn_channel_logo_03_ch07_cable.png")
    img.save(out_path)
    img.save(os.path.join(ASSETS_DIR, "btn_channel_logo_03_ch07_cable.png"))
    return out_path


if __name__ == "__main__":
    p1 = build_logo_01_station_crest()
    p2 = build_logo_02_news_bug()
    p3 = build_logo_03_ch07_cable()
    print("Generated logos:")
    print(p1)
    print(p2)
    print(p3)
