"""
Authentic Indian & Bengali Analog Horror Character Actors & Graphic Shaders for PROJECT NOIR.
- 1994 Doordarshan Calcutta Emergency Alert (দূরদর্শন কেন্দ্র কলকাতা) in pure authentic Bengali typography.
- Twilight Zone optical illusion spiral abyss with the tumbling falling man.
- Regular bedroom draped in an authentic Moshari (মশারি / mosquito net canopy).
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
    # Draw red rectangle with gold outline on image
    temp = np.array(pil_img)
    cv2.rectangle(temp, (60, banner_y1), (w - 60, banner_y2), (185, 22, 28), -1)
    cv2.rectangle(temp, (60, banner_y1), (w - 60, banner_y2), (245, 205, 55), 2)
    pil_img = Image.fromarray(temp)
    draw = ImageDraw.Draw(pil_img)

    draw.text((w // 2, 198), "দূরদর্শন বিশেষ জরুরি সম্প্রচার — পশ্চিমবঙ্গ বিপর্যয় মোকাবিলা দফতর",
              font=font_banner, fill=(255, 255, 255), anchor="mm")

    # 4. Bureaucratic Sector Notice
    draw.text((95, 248), "বিজ্ঞপ্তি সংখ্যা: ৯৪/বিপর্যয়-নিস্তব্ধপুর", font=font_meta, fill=(65, 235, 125))
    draw.text((95, 280), "অধিক্ষেত্র: নিস্তব্ধপুর ও তৎসংলগ্ন মৌজা (বীরভূম ও পশ্চিম মেদিনীপুর সীমানা)",
              font=font_small, fill=(200, 225, 205))

    # 5. Typewriter Directives in Pure Bengali
    directives = [
        ("জরুরি নির্দেশাবলী (অবিলম্বে পালনীয়):", True),
        ("১. রাত ১২টার পর পরিচিত কণ্ঠে নিশিডাক আসিলে ভুলেও কপাট খুলিবেন না।", False),
        ("২. গৃহের মেঝের উপর খোলস বা পতঙ্গের পদ দৃষ্ট হইলে শান্ত হইয়া মশারি মধ্যে অবস্থান করুন।", False),
        ("৩. বাঁশের বেড়ায় আসীন কৃষ্ণবর্ণ হুলো বেড়ালের চক্ষুর দিকে তাকাইবেন না; ইহা আকাশস্থ নয়নের প্রবেশদ্বার।", False),
        ("৪. আকাশের রক্তিম নয়নের দিকে দৃষ্টিপাত করিবেন না। নয়নটি আপনাকে বহু পূর্বেই প্রত্যক্ষ করিয়াছে।", False),
        ("", False),
        ("সম্প্রচার সমাপ্ত হইবে না (এই জরুরি সম্প্রচার নিরবচ্ছিন্নভাবে চলিবে)", True)
    ]

    # Typewriter progression (all visible after ~7 seconds)
    chars_to_show = int(t * 32)
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

    # Corner broadcast tag
    draw.text((w - 180, 52), "ডিডি-১ বাংলা", font=font_small, fill=(65, 235, 125))

    frame[:] = np.array(pil_img)


def draw_subtle_banana_frond(frame, t, cx=1180, cy=720, scale=0.7):
    """
    Subtle, non-cluttering silhouette of a distant rural Bengal banana frond
    swaying gently in the night mist at the edge of the frame.
    """
    color = (14, 12, 18)
    # Just 2-3 delicate fronds gently curving in from the corner
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


def draw_moshari_net(frame, t, bed_rect=(260, 240, 740, 420)):
    """
    Renders an authentic Bengali Moshari (মশারি / mosquito net canopy)
    draped over a regular home bedroom bed.
    Features:
      - 4 corner suspension strings tied to ceiling points.
      - Translucent sheer white/cream gauze netting.
      - Subtle cross-hatching grid texture.
      - Silhouette of a person tossing restlessly beneath the net.
    """
    x, y, bw, bh = bed_rect
    h, w = frame.shape[:2]

    # 4 top canopy corners
    p1 = (x + int(bw * 0.12), y)                   # back-left
    p2 = (x + int(bw * 0.88), y)                   # back-right
    p3 = (x + bw, y + int(bh * 0.20))              # front-right
    p4 = (x, y + int(bh * 0.20))                   # front-left

    # 4 bottom corners reaching the mattress/bed level
    p1_b = (p1[0], y + int(bh * 0.85))
    p2_b = (p2[0], y + int(bh * 0.85))
    p3_b = (p3[0], y + bh)
    p4_b = (p4[0], y + bh)

    # 1. Suspension cords to wall/ceiling
    cord_col = (135, 130, 125)
    cv2.line(frame, p1, (p1[0] - 60, 40), cord_col, 1, cv2.LINE_AA)
    cv2.line(frame, p2, (p2[0] + 60, 40), cord_col, 1, cv2.LINE_AA)
    cv2.line(frame, p3, (p3[0] + 70, 70), cord_col, 1, cv2.LINE_AA)
    cv2.line(frame, p4, (p4[0] - 70, 70), cord_col, 1, cv2.LINE_AA)

    # 2. Person tossing inside under the net (semi-dark silhouette inside)
    toss_x = int(x + bw * 0.48 + math.sin(t * 1.8) * 8)
    toss_y = int(y + bh * 0.62)
    # Head and torso lying down
    cv2.ellipse(frame, (toss_x, toss_y), (42, 16), int(math.sin(t * 1.2) * 5), 0, 360, (22, 18, 26), -1)
    cv2.circle(frame, (toss_x - 52, toss_y - 2), 12, (22, 18, 26), -1)

    # 3. Translucent gauze canopy overlay
    overlay = frame.copy()
    pts_top = np.array([p1, p2, p3, p4], np.int32)
    pts_front = np.array([p4, p3, p3_b, p4_b], np.int32)
    pts_side = np.array([p3, p2, p2_b, p3_b], np.int32)

    net_color = (215, 210, 202)  # Sheer cotton gauze
    cv2.fillPoly(overlay, [pts_top, pts_front, pts_side], net_color)

    # Delicate cross-hatch netting grid
    for gy in range(p4[1], p4_b[1], 15):
        cv2.line(overlay, (p4[0], gy), (p3[0], gy), (230, 226, 218), 1)
    for gx in range(p4[0], p3[0], 16):
        cv2.line(overlay, (gx, p4[1]), (gx, p4_b[1]), (230, 226, 218), 1)

    # Alpha blend net (26% opacity for realistic sheer gauze transparency)
    cv2.addWeighted(overlay, 0.26, frame, 0.74, 0, frame)

    # Edge pipings / border tapes (মশারির ধার)
    border_col = (225, 220, 212)
    cv2.polylines(frame, [pts_top], True, border_col, 2, cv2.LINE_AA)
    cv2.line(frame, p4, p4_b, border_col, 2, cv2.LINE_AA)
    cv2.line(frame, p3, p3_b, border_col, 2, cv2.LINE_AA)
    cv2.line(frame, p4_b, p3_b, border_col, 2, cv2.LINE_AA)


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
    speed = 2.6 + 1.2 * sub_bass
    spiral_phase = arms * theta + twist * np.sqrt(r) * 16.0 - t * speed
    val = np.sin(spiral_phase)

    # High-contrast bone-white / amber CRT phosphor & deep void black
    bone_white = np.array([218, 212, 202], dtype=np.uint8)
    deep_void = np.array([12, 10, 16], dtype=np.uint8)

    mask = (val > 0).astype(np.float32)[:, :, None]
    # Center infinite black hole singularity
    core_void = np.clip((r - 30.0) / 260.0, 0.0, 1.0)
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
    tumble_ang = t * 1.85
    drift_radius = 80.0 * (0.8 + 0.2 * math.sin(t * 0.8))
    man_x = int(cx + math.cos(t * 0.85) * drift_radius)
    man_y = int(cy + math.sin(t * 0.85) * drift_radius * 0.65)
    man_scale = 0.95 + 0.15 * math.sin(t * 1.4)

    # Ghost vertigo echo trails behind the falling figure
    draw_tumbler(frame,
                 int(cx + math.cos((t - 0.25) * 0.85) * (drift_radius + 18)),
                 int(cy + math.sin((t - 0.25) * 0.85) * (drift_radius + 18) * 0.65),
                 (t - 0.25) * 1.85, man_scale * 1.2, alpha=0.32)
    draw_tumbler(frame,
                 int(cx + math.cos((t - 0.12) * 0.85) * (drift_radius + 8)),
                 int(cy + math.sin((t - 0.12) * 0.85) * (drift_radius + 8) * 0.65),
                 (t - 0.12) * 1.85, man_scale * 1.1, alpha=0.55)
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
