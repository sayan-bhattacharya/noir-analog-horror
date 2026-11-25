"""
Authentic Indian & Bengali Analog Horror Character Actors & Graphic Shaders for PROJECT NOIR.
- 1994 Doordarshan Calcutta Emergency Alert (দূরদর্শন কেন্দ্র কলকাতা) in pure authentic Bengali typography.
- Silent film / Alex Kister style dialogue intertitle cards with film grain, scratches, gate weave, and tape dropouts.
- Twilight Zone optical illusion spiral abyss with the tumbling falling man in freefall vertigo.
- Subtle, delicate rural Bengal banana fronds (non-cluttering).
- Black Tomcat on rustic bamboo fence (বাঁশের বেড়া).
"""
import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Font configuration
_CUR_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(_CUR_DIR, "fonts")
BENGALI_FONT_PATH = os.path.join(FONTS_DIR, "NotoSansBengali-Bold.ttf")

# Fallback paths
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


def get_bengali_font(size):
    """Caches TrueType fonts for smooth rendering."""
    if size not in _FONT_CACHE:
        try:
            _FONT_CACHE[size] = ImageFont.truetype(BENGALI_FONT_PATH, size)
        except Exception:
            _FONT_CACHE[size] = ImageFont.load_default()
    return _FONT_CACHE[size]


def draw_bengali_text(img, text, pos, font_size=24, fill_color=(240, 240, 240), anchor=None):
    """
    Renders crisp Bengali Unicode text onto an OpenCV uint8 image via PIL.
    Color format: (R, G, B).
    """
    if not text:
        return
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    font = get_bengali_font(font_size)
    draw.text(pos, text, font=font, fill=fill_color, anchor=anchor)
    img[:] = np.array(pil_img)


def draw_silent_film_intertitle(frame, main_text, sub_text="", t=0.0):
    """
    Renders an authentic vintage Silent Film / Alex Kister analog horror dialogue card.
    Features:
      - Deep charcoal black background.
      - Double-line ornate art-deco border.
      - Gate weave (organic vertical/horizontal jitter).
      - Authentic high-contrast Bengali dialogue typography.
      - Film grain, dust specks, and thin vertical scratches.
    """
    h, w = frame.shape[:2]
    frame[:, :] = [12, 10, 14]

    # Gate weave jitter
    jitter_y = int(math.sin(t * 19.0) * 1.5)
    jitter_x = int(math.cos(t * 13.0) * 1.2)

    # Ornate double border
    pad = 52
    b1_col = (210, 205, 195)
    b2_col = (130, 125, 120)

    cv2.rectangle(frame, (pad + jitter_x, pad + jitter_y),
                  (w - pad + jitter_x, h - pad + jitter_y), b1_col, 2)
    cv2.rectangle(frame, (pad + 12 + jitter_x, pad + 12 + jitter_y),
                  (w - pad - 12 + jitter_x, h - pad - 12 + jitter_y), b2_col, 1)

    # Corner diamond rivets
    for cx_b, cy_b in [
        (pad + 12 + jitter_x, pad + 12 + jitter_y),
        (w - pad - 12 + jitter_x, pad + 12 + jitter_y),
        (pad + 12 + jitter_x, h - pad - 12 + jitter_y),
        (w - pad - 12 + jitter_x, h - pad - 12 + jitter_y)
    ]:
        cv2.circle(frame, (cx_b, cy_b), 4, b1_col, -1)

    # Render Bengali Dialogue Text via PIL
    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)
    font_main = get_bengali_font(34)
    font_sub = get_bengali_font(21)

    cy = h // 2 + jitter_y - (22 if sub_text else 0)
    draw.text((w // 2 + jitter_x, cy), main_text, font=font_main, fill=(245, 242, 235), anchor="mm")

    if sub_text:
        draw.text((w // 2 + jitter_x, cy + 50), sub_text, font=font_sub, fill=(180, 175, 165), anchor="mm")

    frame[:] = np.array(pil_img)

    # Vintage film vertical scratches (periodic flickering scratch)
    if int(t * 8) % 2 == 0:
        scratch_x = int((math.sin(t * 5.3) * 0.4 + 0.5) * (w - 140) + 70)
        cv2.line(frame, (scratch_x, 0), (scratch_x, h), (85, 80, 75), 1)

    # Dust specks
    rng = np.random.RandomState(int(t * 24))
    for _ in range(12):
        rx = rng.randint(pad + 15, w - pad - 15)
        ry = rng.randint(pad + 15, h - pad - 15)
        frame[ry, rx] = [170, 165, 160]


def draw_doordarshan_logo(frame, cx, cy, radius=52, t=0.0):
    """
    Renders the iconic Doordarshan swirling spiral eye emblem,
    subtly pulsating with CRT phosphor amber glow.
    """
    pulse = 1.0 + 0.06 * math.sin(t * 4.5)
    r = int(radius * pulse)
    
    color_gold = (245, 205, 55)   # Phosphor amber gold (RGB)
    color_dark = (25, 18, 15)

    # Central eye pupil
    cv2.circle(frame, (cx, cy), int(13 * pulse), color_gold, -1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), int(6 * pulse), color_dark, -1, cv2.LINE_AA)

    # Symmetrical spiral arms
    for angle_offset in [0.0, math.pi]:
        pts = []
        for a in np.linspace(0, 1.38 * math.pi, 30):
            ang = a + angle_offset + t * 0.35
            dist = 14 + (a / (1.38 * math.pi)) * (r - 14)
            px = int(cx + math.cos(ang) * dist)
            py = int(cy + math.sin(ang) * dist * 0.82)
            pts.append([px, py])
        if len(pts) > 1:
            cv2.polylines(frame, [np.array(pts, np.int32)], False, color_gold, 4, cv2.LINE_AA)


def draw_doordarshan_alert(frame, t):
    """
    Renders an authentic 1994 Doordarshan Kendra Calcutta (দূরদর্শন কেন্দ্র কলকাতা)
    Emergency Interruption in 100% authentic Bengali script and bureaucratic tone.
    """
    h, w = frame.shape[:2]
    # Deep Doordarshan CRT navy blue raster
    frame[:, :] = [18, 15, 48]

    # 1. Doordarshan Logo at top center
    draw_doordarshan_logo(frame, w // 2, 88, radius=44, t=t)

    # 2. Convert to PIL for authentic Bengali typography
    pil_img = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_img)

    font_banner = get_bengali_font(28)
    font_slogan = get_bengali_font(20)
    font_meta = get_bengali_font(20)
    font_small = get_bengali_font(18)
    font_body = get_bengali_font(21)
    font_urgent = get_bengali_font(22)

    # Doordarshan Motto underneath logo
    draw.text((w // 2, 142), "সত্যম শিবম সুন্দরম", font=font_slogan, fill=(245, 215, 60), anchor="mm")

    # 3. Emergency Banner (লাল সতর্কবার্তা পটভূমি)
    banner_y1, banner_y2 = 168, 228
    temp = np.array(pil_img)
    cv2.rectangle(temp, (60, banner_y1), (w - 60, banner_y2), (185, 22, 28), -1)
    cv2.rectangle(temp, (60, banner_y1), (w - 60, banner_y2), (245, 205, 55), 2)
    pil_img = Image.fromarray(temp)
    draw = ImageDraw.Draw(pil_img)

    draw.text((w // 2, 198), "ভারত দর্পণ বিশেষ জরুরি সম্প্রচার | পশ্চিমবঙ্গ বিপর্যয় মোকাবিলা দফতর",
              font=font_banner, fill=(255, 255, 255), anchor="mm")

    # 4. Bureaucratic Sector Notice
    draw.text((95, 248), "বিজ্ঞপ্তি সংখ্যা: ৯৪/বিপর্যয়-নিস্তব্ধপুর", font=font_meta, fill=(65, 235, 125))
    draw.text((95, 280), "অধিক্ষেত্র: নিস্তব্ধপুর ও তৎসংলগ্ন মৌজা (বীরভূম ও পশ্চিম মেদিনীপুর সীমানা)",
              font=font_small, fill=(200, 225, 205))

    # 5. Directives
    directives = [
        ("জরুরি নির্দেশাবলী (অবিলম্বে পালনীয়):", True),
        ("১. রাত ১২টার পর পরিচিত কণ্ঠে ডাক শুনলেও ভুলেও দরজা খুলবেন না।", False),
        ("২. ঘরের মেঝেতে পোকার পা বেরোতে দেখলে শান্ত হয়ে মশারির ভেতর থাকুন।", False),
        ("৩. বাঁশের বেড়ায় বসা কালো বেড়ালটার চোখের দিকে তাকাবেন না, ওটা আকাশের চোখের প্রবেশদ্বার।", False),
        ("৪. আকাশের লাল চোখের দিকে তাকাবেন না। ও অনেক আগেই আপনাকে দেখে ফেলেছে।", False),
        ("", False),
        ("সম্প্রচার বন্ধ হবে না (এই জরুরি সম্প্রচার একটানা চলবে)", True)
    ]

    chars_to_show = int(t * 36)
    accumulated_chars = 0
    y_pos = 325

    for line_text, is_highlight in directives:
        if not line_text:
            y_pos += 14
            continue

        line_len = len(line_text)
        if accumulated_chars + line_len <= chars_to_show:
            disp_text = line_text
            accumulated_chars += line_len
        elif accumulated_chars < chars_to_show:
            disp_text = line_text[:chars_to_show - accumulated_chars]
            accumulated_chars = chars_to_show
        else:
            disp_text = ""

        if disp_text:
            if "সমাপ্ত" in disp_text:
                col = (255, 195, 55) if int(t * 3) % 2 == 0 else (240, 70, 70)
                fnt = font_urgent
            elif is_highlight:
                col = (65, 235, 125)
                fnt = font_urgent
            else:
                col = (235, 235, 235)
                fnt = font_body
            draw.text((95, y_pos), disp_text, font=fnt, fill=col)

        y_pos += 42

    draw.text((w - 180, 52), "ডিডি-১ বাংলা", font=font_small, fill=(65, 235, 125))
    frame[:] = np.array(pil_img)


def draw_subtle_banana_frond(frame, t, cx=1180, cy=720, scale=0.7):
    """
    Subtle, non-cluttering silhouette of a distant rural Bengal banana frond
    swaying gently in the night mist at the edge of the frame.
    """
    color = (14, 12, 18)
    for angle_deg, length, wind_phase in [(-42, 170, 0.4), (-20, 190, 0.8), (12, 150, 0.2)]:
        sway = math.sin(t * 1.4 + wind_phase) * 5.0
        rad = math.radians(angle_deg + sway)
        end_x = int(cx + math.sin(rad) * length * scale)
        end_y = int(cy - 120 * scale - math.cos(rad) * length * scale * 0.45)
        ctrl_x = int((cx + end_x) * 0.5 - 15 * scale)
        ctrl_y = int(cy - 120 * scale - 35 * scale)

        leaf_pts = [
            [cx, int(cy - 100 * scale)],
            [ctrl_x - int(12 * scale), ctrl_y],
            [end_x, end_y],
            [ctrl_x + int(12 * scale), ctrl_y + int(8 * scale)]
        ]
        cv2.fillPoly(frame, [np.array(leaf_pts, np.int32)], color)


# Cache coordinate grid for the Twilight Zone spiral abyss
_ABYSS_GRID_CACHE = {}


def draw_twilight_zone_abyss(frame, t, sub_bass=0.1):
    """
    Renders an intense, hypnotic 'Twilight Zone' spinning optical illusion spiral abyss
    with the silhouette of the man tumbling and falling into the endless vortex.
    """
    h, w = frame.shape[:2]
    key = (h, w)
    if key not in _ABYSS_GRID_CACHE:
        cy, cx = h // 2, w // 2
        ys, xs = np.indices((h, w), dtype=np.float32)
        dx = xs - cx
        dy = ys - cy
        r = np.sqrt(dx**2 + dy**2)
        theta = np.arctan2(dy, dx)
        _ABYSS_GRID_CACHE[key] = (cx, cy, r, theta)

    cx, cy, r, theta = _ABYSS_GRID_CACHE[key]

    # 1. Hypnotic Spiral Illusion Mathematics
    arms = 6.0
    twist = 0.088
    speed = 2.8 + 1.6 * sub_bass
    spiral_phase = arms * theta + twist * np.sqrt(r) * 16.0 - t * speed
    val = np.sin(spiral_phase)

    # High-contrast bone-white / amber CRT phosphor & deep void black
    bone_white = np.array([220, 214, 202], dtype=np.uint8)
    deep_void = np.array([12, 10, 16], dtype=np.uint8)

    mask = (val > 0).astype(np.float32)[:, :, None]
    core_void = np.clip((r - 28.0) / 250.0, 0.0, 1.0)
    outer_vignette = np.clip(1.25 - r / (w * 0.58), 0.0, 1.0)
    depth_falloff = (core_void * outer_vignette)[:, :, None]

    base_spiral = (mask * bone_white + (1.0 - mask) * deep_void) * depth_falloff
    frame[:] = np.clip(base_spiral, 0, 255).astype(np.uint8)

    # 2. The Falling Man Silhouette Tumbling in Freefall
    def draw_tumbler(canvas, px, py, angle_rad, scale, alpha=1.0):
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        def tf(lx, ly):
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            return int(px + rx * scale), int(py + ry * scale)

        col = (int(8 * alpha), int(6 * alpha), int(10 * alpha))
        target = canvas if alpha >= 0.99 else canvas.copy()

        # Head
        hx, hy = tf(0, -32)
        cv2.circle(target, (hx, hy), int(11 * scale), col, -1, cv2.LINE_AA)

        # Torso
        cv2.line(target, tf(0, -20), tf(0, 18), col, int(15 * scale), cv2.LINE_AA)

        # Arms in freefall flail
        cv2.line(target, tf(-6, -18), tf(-24, -36), col, int(6 * scale), cv2.LINE_AA)
        cv2.line(target, tf(-24, -36), tf(-38, -52), col, int(5 * scale), cv2.LINE_AA)
        cv2.line(target, tf(6, -18), tf(26, -26), col, int(6 * scale), cv2.LINE_AA)
        cv2.line(target, tf(26, -26), tf(42, -38), col, int(5 * scale), cv2.LINE_AA)

        # Legs kicking / curled
        cv2.line(target, tf(-5, 16), tf(-18, 48), col, int(7 * scale), cv2.LINE_AA)
        cv2.line(target, tf(-18, 48), tf(-30, 76), col, int(6 * scale), cv2.LINE_AA)
        cv2.line(target, tf(5, 16), tf(20, 42), col, int(7 * scale), cv2.LINE_AA)
        cv2.line(target, tf(20, 42), tf(36, 68), col, int(6 * scale), cv2.LINE_AA)

        if alpha < 0.99:
            cv2.addWeighted(target, alpha, canvas, 1.0 - alpha, 0, canvas)

    # Tumbling dynamics: rotating, drifting inward towards the singularity
    tumble_ang = t * 2.1
    drift_radius = 85.0 * (0.75 + 0.25 * math.sin(t * 1.1))
    man_x = int(cx + math.cos(t * 0.95) * drift_radius)
    man_y = int(cy + math.sin(t * 0.95) * drift_radius * 0.68)
    man_scale = 1.0 + 0.20 * math.sin(t * 1.5)

    # Ghost vertigo echo trails behind the falling figure
    draw_tumbler(frame,
                 int(cx + math.cos((t - 0.25) * 0.95) * (drift_radius + 20)),
                 int(cy + math.sin((t - 0.25) * 0.95) * (drift_radius + 20) * 0.68),
                 (t - 0.25) * 2.1, man_scale * 1.25, alpha=0.30)
    draw_tumbler(frame,
                 int(cx + math.cos((t - 0.12) * 0.95) * (drift_radius + 10)),
                 int(cy + math.sin((t - 0.12) * 0.95) * (drift_radius + 10) * 0.68),
                 (t - 0.12) * 2.1, man_scale * 1.12, alpha=0.55)
    # Solid falling man
    draw_tumbler(frame, man_x, man_y, tumble_ang, man_scale, alpha=1.0)


def draw_bengal_hulo_cat(frame, t, cx=980, cy=600, stretch=0.0):
    """
    Renders the rural Bengal Black Tomcat (কালো হুলো বেড়াল)
    perched on a rustic bamboo fence (বাঁশের বেড়া).
    Its neck stretches unnaturally into the purple night sky.
    """
    color = (12, 10, 16)

    # Rural Bamboo Fence (বাঁশের বেড়া)
    for fx in range(cx - 90, cx + 110, 30):
        cv2.line(frame, (fx, cy), (fx, cy + 140), (45, 38, 28), 5, cv2.LINE_AA)
    cv2.line(frame, (cx - 100, cy + 35), (cx + 120, cy + 35), (55, 45, 32), 4, cv2.LINE_AA)
    cv2.line(frame, (cx - 100, cy + 85), (cx + 120, cy + 85), (55, 45, 32), 4, cv2.LINE_AA)

    # Cat body on the bamboo rail
    body_y = int(cy + 18)
    cv2.ellipse(frame, (cx, body_y), (24, 16), -8, 0, 360, color, -1)

    # Curled feline tail
    tail_pts = []
    for i in range(14):
        tx = int(cx - 24 - i * 3 + math.sin(t * 4.5 + i * 0.25) * 5)
        ty = int(body_y - i * 2 + math.cos(t * 3.5 + i * 0.2) * 4)
        tail_pts.append([tx, ty])
    if len(tail_pts) > 1:
        cv2.polylines(frame, [np.array(tail_pts, np.int32)], False, color, 3, cv2.LINE_AA)

    # Elastic Elongated Neck rising into the sky
    head_y = int(body_y - 28 - stretch * 340)
    neck_w = int(max(4, 15 - stretch * 9))
    cv2.line(frame, (cx, body_y - 10), (cx, head_y + 10), color, neck_w, cv2.LINE_AA)

    # Cat Head & Pointed Ears
    cv2.circle(frame, (cx, head_y), 18, color, -1)
    ear_l = np.array([[cx - 14, head_y - 4], [cx - 6, head_y - 24], [cx - 2, head_y - 10]], np.int32)
    ear_r = np.array([[cx + 14, head_y - 4], [cx + 6, head_y - 24], [cx + 2, head_y - 10]], np.int32)
    cv2.fillPoly(frame, [ear_l, ear_r], color)

    # Glowing Toxic Amber Cat Eyes
    eye_glow = (245, 225, 45)  # Phosphorescent amber yellow (RGB)
    cv2.ellipse(frame, (cx - 6, head_y - 2), (4, 7), 10, 0, 360, eye_glow, -1)
    cv2.ellipse(frame, (cx + 6, head_y - 2), (4, 7), -10, 0, 360, eye_glow, -1)
    # Slit pupils
    cv2.line(frame, (cx - 6, head_y - 7), (cx - 6, head_y + 3), (10, 10, 10), 2)
    cv2.line(frame, (cx + 6, head_y - 7), (cx + 6, head_y + 3), (10, 10, 10), 2)
