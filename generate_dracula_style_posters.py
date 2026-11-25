import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"E:\betweenthenotes\noir_film_project"
ARTIFACT_DIR = r"C:\Users\sayan\.gemini\antigravity\brain\b3d17fa9-62a2-4701-acdb-0633a94e4498"
FLOW_DIR = r"C:\Users\sayan\flow-mcp-out\NoirBillboardCreds"
LOGO_PATH = r"E:\betweenthenotes\remotion_intro\dist\podcast_logo_circle.png"
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = r"E:\betweenthenotes\public\images\logo.jpg"

FONTS_DIR = r"C:\Windows\Fonts"
LOCAL_FONTS = os.path.join(ROOT, "noir_film", "fonts")

def get_font(name_list, size):
    for f in name_list:
        p = os.path.join(FONTS_DIR, f)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
        p_local = os.path.join(LOCAL_FONTS, f)
        if os.path.exists(p_local):
            try:
                return ImageFont.truetype(p_local, size)
            except Exception:
                pass
    return ImageFont.load_default()

# High-resolution fonts (rendered at 2x scale for supreme razor-sharp clarity)
SCALE = 2
font_title = get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 185 * SCALE)
font_title_med = get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 150 * SCALE)
font_bengali = get_font(["NotoSansBengali-Bold.ttf", "kalpurush.ttf"], 36 * SCALE)
font_bug = get_font(["GOTHICB.TTF", "corbelb.ttf", "impact.ttf"], 22 * SCALE)
font_tagline = get_font(["GOTHICB.TTF", "corbelb.ttf", "IBMPlexMono-Bold.ttf"], 18 * SCALE)
font_sub = get_font(["GOTHIC.TTF", "corbel.ttf", "IBMPlexMono-Regular.ttf"], 15 * SCALE)
font_small = get_font(["GOTHICB.TTF", "corbelb.ttf"], 13 * SCALE)
font_box = get_font(["impact.ttf", "GOTHICB.TTF"], 17 * SCALE)

logo_raw = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
if logo_raw is None:
    logo_raw = cv2.imread(r"E:\betweenthenotes\public\images\logo.jpg")

def create_circular_logo(size=140, bw=False):
    if logo_raw is None:
        return None
    resized = cv2.resize(logo_raw, (size, size), interpolation=cv2.INTER_AREA)
    if resized.shape[2] == 3:
        mask = np.zeros((size, size), dtype=np.uint8)
        cv2.circle(mask, (size//2, size//2), size//2 - 2, 255, -1)
        b, g, r = cv2.split(resized)
        if bw:
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            b = g = r = gray
        rgba = cv2.merge([b, g, r, mask])
    else:
        if bw:
            gray = cv2.cvtColor(resized[:, :, :3], cv2.COLOR_BGR2GRAY)
            resized[:, :, 0] = gray
            resized[:, :, 1] = gray
            resized[:, :, 2] = gray
        rgba = resized
    return Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))

def draw_dracula_title(draw, text, x_center, y_top, font, fill_color, drop_shadow_color=None):
    """
    Renders the title with sharp gothic fang accents characteristic of the Dracula logo.
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = x_center - tw // 2
    
    if drop_shadow_color:
        draw.text((tx + 3 * SCALE, y_top + 3 * SCALE), text, font=font, fill=drop_shadow_color)
    
    draw.text((tx, y_top), text, font=font, fill=fill_color)
    
    # Add subtle sharp razor-fang spurs on N and R terminals if ONYX font
    # Draw tiny sharp triangles to accentuate the vampire/gothic aesthetic
    th = bbox[3] - bbox[1]
    fang_h = 10 * SCALE
    fang_w = 4 * SCALE
    
    # Left serif peak of N
    draw.polygon([(tx + 4*SCALE, y_top), (tx + 4*SCALE + fang_w, y_top), (tx + 4*SCALE + fang_w//2, y_top - fang_h)], fill=fill_color)
    # Right serif peak of R
    draw.polygon([(tx + tw - 8*SCALE, y_top), (tx + tw - 8*SCALE + fang_w, y_top), (tx + tw - 8*SCALE + fang_w//2, y_top - fang_h)], fill=fill_color)

# =============================================================================
# VARIATION 1: B&W CLASSIC FILM NOIR BILLBOARD (Dracula Stake Shadow)
# =============================================================================
def render_var1():
    base = Image.open(os.path.join(FLOW_DIR, "scene-01.jpeg")).convert("RGBA")
    w, h = base.size
    # 2x hi-res canvas
    hi = base.resize((w * SCALE, h * SCALE), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(hi)
    
    # Billboard clean right section center
    tx = int(980 * SCALE)
    
    # 1. BBC style Bug: "BETWEEN THE NOTES"
    bug_txt = "BETWEEN THE NOTES"
    bb = draw.textbbox((0, 0), bug_txt, font=font_bug)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    bx, by = tx - bw // 2, int(210 * SCALE)
    draw.rounded_rectangle([bx - 18*SCALE, by - 8*SCALE, bx + bw + 18*SCALE, by + bh + 10*SCALE], radius=6*SCALE, fill=(10, 10, 12, 245))
    draw.text((bx, by), bug_txt, font=font_bug, fill=(245, 245, 245))
    
    # 2. Main Title: NOIR (Stark Jet Black)
    draw_dracula_title(draw, "NOIR", tx, int(260 * SCALE), font_title, (12, 12, 15, 255), (140, 140, 145, 120))
    
    # 3. Bengali Title: নি শি ডা ক
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=font_bengali)
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, int(460 * SCALE)), ben, font=font_bengali, fill=(25, 25, 28, 240))
    
    # 4. Tagline: FROM THE CREATORS OF AFTER MIDNIGHT
    sub1 = "FROM THE CREATORS OF AFTER MIDNIGHT"
    bb_s1 = draw.textbbox((0, 0), sub1, font=font_tagline)
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, int(525 * SCALE)), sub1, font=font_tagline, fill=(35, 35, 40, 255))
    
    # 5. Air Date / Description (matching "Starts New Year's Day")
    sub2 = "A BENGALI COSMIC HORROR TRANSMISSION"
    bb_s2 = draw.textbbox((0, 0), sub2, font=font_sub)
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, int(560 * SCALE)), sub2, font=font_sub, fill=(65, 65, 70, 255))
    
    # 6. Bottom platform row: circular logo + "BHARAT DARPAN  |  1994 ARCHIVE"
    btn_logo = create_circular_logo(size=int(46 * SCALE), bw=True)
    if btn_logo:
        hi.paste(btn_logo, (tx - int(135 * SCALE), int(595 * SCALE)), btn_logo)
    
    cred_txt = "ORIGINAL TUNE BY ATANDRA & SAYAN\nBHARAT DARPAN 1994 BROADCAST ARCHIVE"
    draw.text((tx - int(95 * SCALE), int(598 * SCALE)), cred_txt, font=font_small, fill=(45, 45, 50, 255), spacing=4*SCALE)
    
    # 7. Environmental Box on Fence below: "IN CASE OF NISHIDAK"
    box_x, box_y = int(585 * SCALE), int(838 * SCALE)
    draw.rectangle([box_x, box_y, box_x + int(210 * SCALE), box_y + int(48 * SCALE)], fill=(12, 12, 15), outline=(90, 90, 95), width=2*SCALE)
    draw.text((box_x + int(16 * SCALE), box_y + int(13 * SCALE)), "IN CASE OF NISHIDAK", font=font_box, fill=(235, 235, 240))
    
    return hi.resize((w, h), Image.Resampling.LANCZOS).convert("RGB")

# =============================================================================
# VARIATION 2: CRIMSON COLOR EDITION (Dracula Blood-Red on White Board)
# =============================================================================
def render_var2():
    base = Image.open(os.path.join(FLOW_DIR, "scene-02.jpeg")).convert("RGBA")
    w, h = base.size
    hi = base.resize((w * SCALE, h * SCALE), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(hi)
    
    # Billboard clean right section center
    tx = int(985 * SCALE)
    
    # 1. Bug: "BETWEEN THE NOTES"
    bug_txt = "BETWEEN THE NOTES"
    bb = draw.textbbox((0, 0), bug_txt, font=font_bug)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    bx, by = tx - bw // 2, int(290 * SCALE)
    draw.rounded_rectangle([bx - 18*SCALE, by - 8*SCALE, bx + bw + 18*SCALE, by + bh + 10*SCALE], radius=6*SCALE, fill=(14, 14, 18, 250))
    draw.text((bx, by), bug_txt, font=font_bug, fill=(245, 245, 245))
    
    # 2. Main Title: NOIR in Saturated Dracula Blood-Red (#C01A20)
    draw_dracula_title(draw, "NOIR", tx, int(340 * SCALE), font_title, (195, 26, 32, 255), (60, 10, 14, 200))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=font_bengali)
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, int(540 * SCALE)), ben, font=font_bengali, fill=(28, 24, 26, 240))
    
    # 4. Taglines
    sub1 = "FROM THE CREATORS OF AFTER MIDNIGHT"
    bb_s1 = draw.textbbox((0, 0), sub1, font=font_tagline)
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, int(600 * SCALE)), sub1, font=font_tagline, fill=(30, 28, 32, 255))
    
    sub2 = "AN EXPERIMENTAL ANALOG HORROR TRANSMISSION"
    bb_s2 = draw.textbbox((0, 0), sub2, font=font_sub)
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, int(635 * SCALE)), sub2, font=font_sub, fill=(65, 35, 38, 255))
    
    # 5. Bottom platform row: Color circular logo + metadata
    btn_logo = create_circular_logo(size=int(48 * SCALE), bw=False)
    if btn_logo:
        hi.paste(btn_logo, (tx - int(140 * SCALE), int(670 * SCALE)), btn_logo)
    
    cred_txt = "ORIGINAL TUNE BY ATANDRA & SAYAN\nBROADCAST CODE: 94/NISHIDAK  •  SECTOR WB"
    draw.text((tx - int(98 * SCALE), int(672 * SCALE)), cred_txt, font=font_small, fill=(40, 32, 35, 255), spacing=4*SCALE)
    
    # 6. Red Emergency Box on Roadside with glass glare
    box_x, box_y = int(580 * SCALE), int(855 * SCALE)
    draw.rectangle([box_x, box_y, box_x + int(225 * SCALE), box_y + int(50 * SCALE)], fill=(168, 20, 26), outline=(245, 240, 240), width=2*SCALE)
    draw.text((box_x + int(16 * SCALE), box_y + int(14 * SCALE)), "IN CASE OF NISHIDAK", font=font_box, fill=(255, 255, 255))
    
    return hi.resize((w, h), Image.Resampling.LANCZOS).convert("RGB")

# =============================================================================
# VARIATION 3: ACOUSTIC PINS & THE UNCANNY FELINE (B&W Studio Horror)
# =============================================================================
def render_var3():
    base = Image.open(os.path.join(FLOW_DIR, "scene-03.jpeg")).convert("RGBA")
    w, h = base.size
    hi = base.resize((w * SCALE, h * SCALE), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(hi)
    
    # Right night space
    tx = int(980 * SCALE)
    
    # 1. White bug pill
    bug_txt = "BETWEEN THE NOTES"
    bb = draw.textbbox((0, 0), bug_txt, font=font_bug)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    bx, by = tx - bw // 2, int(220 * SCALE)
    draw.rounded_rectangle([bx - 18*SCALE, by - 8*SCALE, bx + bw + 18*SCALE, by + bh + 10*SCALE], radius=6*SCALE, fill=(240, 240, 245, 240))
    draw.text((bx, by), bug_txt, font=font_bug, fill=(15, 15, 18))
    
    # 2. Main Title: NOIR in Glowing Silver / Ivory
    draw_dracula_title(draw, "NOIR", tx, int(270 * SCALE), font_title, (245, 245, 240, 255), (15, 15, 18, 220))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=font_bengali)
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, int(470 * SCALE)), ben, font=font_bengali, fill=(215, 215, 210, 240))
    
    # 4. Taglines
    sub1 = "THE UNCANNY FELINE TRANSMISSION"
    bb_s1 = draw.textbbox((0, 0), sub1, font=font_tagline)
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, int(535 * SCALE)), sub1, font=font_tagline, fill=(210, 210, 205, 255))
    
    sub2 = "ACOUSTIC COMPOSITION: ATANDRA  •  VISUAL ENGINE: SAYAN"
    bb_s2 = draw.textbbox((0, 0), sub2, font=font_sub)
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, int(570 * SCALE)), sub2, font=font_sub, fill=(165, 165, 160, 255))
    
    # 5. Silver Hallmark
    btn_logo = create_circular_logo(size=int(46 * SCALE), bw=True)
    if btn_logo:
        hi.paste(btn_logo, (tx - int(135 * SCALE), int(605 * SCALE)), btn_logo)
    
    cred_txt = "AFTER MIDNIGHT, SOMEWHERE ELSE\nA STREAMING ANALOG BROADCAST"
    draw.text((tx - int(95 * SCALE), int(608 * SCALE)), cred_txt, font=font_small, fill=(180, 180, 175, 255), spacing=4*SCALE)
    
    return hi.resize((w, h), Image.Resampling.LANCZOS).convert("RGB")

# =============================================================================
# VARIATION 4: DAMODAR HIGHWAY METAMORPHOSIS (Stormy Palms Color)
# =============================================================================
def render_var4():
    base = Image.open(os.path.join(FLOW_DIR, "scene-04.jpeg")).convert("RGBA")
    w, h = base.size
    hi = base.resize((w * SCALE, h * SCALE), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(hi)
    
    # Right board section
    tx = int(1005 * SCALE)
    
    # 1. Dark pill
    bug_txt = "BETWEEN THE NOTES"
    bb = draw.textbbox((0, 0), bug_txt, font=font_bug)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    bx, by = tx - bw // 2, int(220 * SCALE)
    draw.rounded_rectangle([bx - 18*SCALE, by - 8*SCALE, bx + bw + 18*SCALE, by + bh + 10*SCALE], radius=6*SCALE, fill=(18, 20, 26, 240))
    draw.text((bx, by), bug_txt, font=font_bug, fill=(245, 245, 245))
    
    # 2. Main Title: NOIR in Dark Crimson (#B41A22)
    draw_dracula_title(draw, "NOIR", tx, int(270 * SCALE), font_title, (188, 28, 35, 255), (45, 15, 20, 180))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=font_bengali)
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, int(470 * SCALE)), ben, font=font_bengali, fill=(35, 28, 30, 240))
    
    # 4. Taglines
    sub1 = "DO NOT ANSWER THE CALLING"
    bb_s1 = draw.textbbox((0, 0), sub1, font=font_tagline)
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, int(535 * SCALE)), sub1, font=font_tagline, fill=(38, 32, 34, 255))
    
    sub2 = "A 1994 RURAL BENGAL EMERGENCY BROADCAST"
    bb_s2 = draw.textbbox((0, 0), sub2, font=font_sub)
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, int(570 * SCALE)), sub2, font=font_sub, fill=(70, 52, 55, 255))
    
    # 5. Color Medallion Logo
    btn_logo = create_circular_logo(size=int(46 * SCALE), bw=False)
    if btn_logo:
        hi.paste(btn_logo, (tx - int(135 * SCALE), int(605 * SCALE)), btn_logo)
    
    cred_txt = "DIRECTED BY BETWEEN THE NOTES\nMUSIC: ATANDRA  •  VISUAL ENGINE: SAYAN"
    draw.text((tx - int(95 * SCALE), int(608 * SCALE)), cred_txt, font=font_small, fill=(45, 36, 38, 255), spacing=4*SCALE)
    
    return hi.resize((w, h), Image.Resampling.LANCZOS).convert("RGB")

# =============================================================================
# VARIATION 5: THE FALLING MAN ABYSS (End Credits Epilogue in B&W)
# =============================================================================
def render_var5():
    base = Image.open(os.path.join(FLOW_DIR, "scene-05.jpeg")).convert("RGBA")
    w, h = base.size
    hi = base.resize((w * SCALE, h * SCALE), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(hi)
    
    # Center of right open paper section
    tx = int(995 * SCALE)
    
    # 1. Bug: "BETWEEN THE NOTES"
    bug_txt = "BETWEEN THE NOTES"
    bb = draw.textbbox((0, 0), bug_txt, font=font_bug)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    bx, by = tx - bw // 2, int(210 * SCALE)
    draw.rounded_rectangle([bx - 18*SCALE, by - 8*SCALE, bx + bw + 18*SCALE, by + bh + 10*SCALE], radius=6*SCALE, fill=(12, 12, 15, 245))
    draw.text((bx, by), bug_txt, font=font_bug, fill=(245, 245, 245))
    
    # 2. Main Title: NOIR
    draw_dracula_title(draw, "NOIR", tx, int(260 * SCALE), font_title, (14, 14, 18, 255), (140, 140, 145, 120))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=font_bengali)
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, int(460 * SCALE)), ben, font=font_bengali, fill=(25, 25, 28, 240))
    
    # 4. Formal End Credits Block (Matching theatrical poster billing block)
    lines = [
        ("END TRANSMISSION", font_tagline, (35, 35, 40)),
        ("COMPOSED & PERFORMED BY ATANDRA", font_sub, (55, 55, 60)),
        ("DIRECTED & VISUAL ENGINE BY SAYAN", font_sub, (55, 55, 60)),
        ("AFTER MIDNIGHT, SOMEWHERE ELSE  •  1994", font_small, (85, 85, 90)),
        ("ALL RIGHTS RESERVED  •  BETWEEN THE NOTES", font_small, (105, 105, 110))
    ]
    cur_y = int(515 * SCALE)
    for text, fnt, col in lines:
        b = draw.textbbox((0, 0), text, font=fnt)
        w_t = b[2] - b[0]
        draw.text((tx - w_t // 2, cur_y), text, font=fnt, fill=col)
        cur_y += int(28 * SCALE)
    
    # 5. Production Hallmark Seal
    btn_logo = create_circular_logo(size=int(50 * SCALE), bw=True)
    if btn_logo:
        hi.paste(btn_logo, (tx - int(25 * SCALE), cur_y + int(10 * SCALE)), btn_logo)
    
    return hi.resize((w, h), Image.Resampling.LANCZOS).convert("RGB")

variations = [
    ("poster_var1_bw_classic.png", render_var1),
    ("poster_var2_crimson_color.png", render_var2),
    ("poster_var3_acoustic_feline.png", render_var3),
    ("poster_var4_highway_metamorphosis.png", render_var4),
    ("poster_var5_abyss_end_credits.png", render_var5),
]

os.makedirs(os.path.join(ROOT, "assets", "posters"), exist_ok=True)

for fname, renderer in variations:
    res = renderer()
    local_out = os.path.join(ROOT, "assets", "posters", fname)
    art_out = os.path.join(ARTIFACT_DIR, fname)
    res.save(local_out, quality=98)
    res.save(art_out, quality=98)
    print(f"Rendered refined Dracula poster: {fname} -> {local_out}")
