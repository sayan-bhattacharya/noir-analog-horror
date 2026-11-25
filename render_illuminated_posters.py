import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = r"E:\betweenthenotes\noir_film_project"
ARTIFACT_DIR = r"C:\Users\sayan\.gemini\antigravity\brain\b3d17fa9-62a2-4701-acdb-0633a94e4498"
FLOW_DIR = r"C:\Users\sayan\flow-mcp-out\NoirBillboardCreds"
LOGO_PATH = r"E:\betweenthenotes\remotion_intro\dist\podcast_logo_circle.png"

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

# Bold, highly legible font sizes
fonts = {
    "dracula_huge": get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 145),
    "dracula_large": get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 120),
    "bengali_title": get_font(["NotoSansBengali-Bold.ttf", "kalpurush.ttf"], 34),
    "tag_bold": get_font(["GOTHICB.TTF", "corbelb.ttf", "impact.ttf"], 18),
    "sub_regular": get_font(["GOTHICB.TTF", "corbelb.ttf", "IBMPlexMono-Bold.ttf"], 15),
    "cred_bold": get_font(["GOTHICB.TTF", "corbelb.ttf", "IBMPlexMono-Bold.ttf"], 14),
    "meta_regular": get_font(["GOTHICB.TTF", "corbelb.ttf", "IBMPlexMono-Bold.ttf"], 13),
    "emergency": get_font(["impact.ttf", "GOTHICB.TTF"], 18)
}

logo_img = Image.open(LOGO_PATH).convert("RGBA")

def illuminate_board_zone(img_np, x_min, x_max, y_min, y_max, intensity=1.55, warm=True):
    """
    Simulates a powerful overhead billboard floodlight shining down on the text zone.
    Raises luminance to clean white/cream paper levels while preserving board textures.
    """
    h, w = img_np.shape[:2]
    # Create smooth elliptical/conical light mask
    mask = np.zeros((h, w), dtype=np.float32)
    cx = (x_min + x_max) // 2
    cy = (y_min + y_max) // 2
    rx = (x_max - x_min) // 2
    ry = (y_max - y_min) // 2
    
    cv2.ellipse(mask, (cx, cy), (int(rx * 1.15), int(ry * 1.1)), 0, 0, 360, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (101, 101), 0)
    
    # Apply soft light boost
    out = img_np.astype(np.float32)
    for c in range(3):
        # Boost luminance towards clean paper white
        boost = 1.0 + (intensity - 1.0) * mask
        if warm and c == 0: # Red channel slightly warmer
            boost *= (1.0 + 0.05 * mask)
        out[:, :, c] = np.clip(out[:, :, c] * boost + mask * 55, 0, 255)
    return out.astype(np.uint8)

def get_styled_logo(size=125, bw=False):
    resized = logo_img.resize((size, size), Image.Resampling.LANCZOS)
    if bw:
        r, g, b, a = resized.split()
        gray = resized.convert("L")
        lut = [int(np.clip((i - 128) * 1.4 + 145, 0, 255)) for i in range(256)]
        gray_contrasted = gray.point(lut)
        resized = Image.merge("RGBA", (gray_contrasted, gray_contrasted, gray_contrasted, a))
        
    pad = 16
    shadow_canvas = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_canvas)
    s_draw.ellipse([pad + 2, pad + 4, pad + size + 2, pad + size + 4], fill=(0, 0, 0, 170))
    shadow_blurred = shadow_canvas.filter(ImageFilter.GaussianBlur(6))
    shadow_blurred.paste(resized, (pad, pad), resized)
    return shadow_blurred

def draw_dracula_title(draw, text, x_center, y_top, font, fill_color, shadow_color=None):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = x_center - tw // 2
    if shadow_color:
        draw.text((tx + 2, y_top + 3), text, font=font, fill=shadow_color)
    draw.text((tx, y_top), text, font=font, fill=fill_color)
    # Razor fangs
    draw.polygon([(tx + 3, y_top), (tx + 7, y_top), (tx + 5, y_top - 8)], fill=fill_color)
    draw.polygon([(tx + tw - 8, y_top), (tx + tw - 4, y_top), (tx + tw - 6, y_top - 8)], fill=fill_color)

# =============================================================================
# VARIATION 1: B&W CLASSIC FILM NOIR BILLBOARD (Dracula Stake Shadow)
# =============================================================================
def render_var1():
    base_bgr = cv2.imread(os.path.join(FLOW_DIR, "scene-01.jpeg"))
    # Broad, powerful overhead floodlight illumination on billboard face
    lit_bgr = illuminate_board_zone(base_bgr, 760, 1160, 120, 620, intensity=2.05, warm=False)
    base = Image.fromarray(cv2.cvtColor(lit_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(base)
    
    tx = 945
    
    # 1. Prominent Between the Notes Logo Medallion
    logo_size = 115
    logo = get_styled_logo(size=logo_size, bw=True)
    base.paste(logo, (tx - (logo_size + 32) // 2, 145), logo)
    
    # 2. Main Title: NOIR (Pitch Black on Illuminated White Paper)
    draw_dracula_title(draw, "NOIR", tx, 275, fonts["dracula_huge"], (0, 0, 0, 255), (170, 170, 175, 140))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_title"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 405), ben, font=fonts["bengali_title"], fill=(0, 0, 0, 255))
    
    # 4. Taglines
    sub1 = "A BETWEEN THE NOTES ORIGINAL"
    bb_s1 = draw.textbbox((0, 0), sub1, font=fonts["tag_bold"])
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, 452), sub1, font=fonts["tag_bold"], fill=(0, 0, 0, 255))
    
    sub2 = "A BENGALI ANALOG HORROR TRANSMISSION"
    bb_s2 = draw.textbbox((0, 0), sub2, font=fonts["sub_regular"])
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, 482), sub2, font=fonts["sub_regular"], fill=(0, 0, 0, 255))
    
    # 5. Clear, Bold Credits
    cred1 = "ORIGINAL SCORE BY ATANDRA  •  VISUAL ENGINE BY SAYAN"
    bb_c1 = draw.textbbox((0, 0), cred1, font=fonts["cred_bold"])
    draw.text((tx - (bb_c1[2]-bb_c1[0]) // 2, 512), cred1, font=fonts["cred_bold"], fill=(0, 0, 0, 255))
    
    cred2 = "BHARAT DARPAN 1994 BROADCAST ARCHIVE"
    bb_c2 = draw.textbbox((0, 0), cred2, font=fonts["meta_regular"])
    draw.text((tx - (bb_c2[2]-bb_c2[0]) // 2, 538), cred2, font=fonts["meta_regular"], fill=(15, 15, 20, 255))
    
    # 6. Environmental Box on Fence below: "IN CASE OF NISHIDAK"
    box_x, box_y = 585, 838
    draw.rectangle([box_x, box_y, box_x + 215, box_y + 45], fill=(10, 10, 12), outline=(140, 140, 145), width=2)
    draw.text((box_x + 16, box_y + 11), "IN CASE OF NISHIDAK", font=fonts["emergency"], fill=(255, 255, 255))
    
    return base

# =============================================================================
# VARIATION 2: CRIMSON COLOR EDITION (Dracula Blood-Red on White Board)
# =============================================================================
def render_var2():
    base_bgr = cv2.imread(os.path.join(FLOW_DIR, "scene-02.jpeg"))
    # Broad floodlight covering the whole perspective billboard face
    lit_bgr = illuminate_board_zone(base_bgr, 720, 1000, 180, 580, intensity=2.0, warm=True)
    base = Image.fromarray(cv2.cvtColor(lit_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(base)
    
    tx = 865
    
    # 1. Color Logo Medallion
    logo_size = 95
    logo = get_styled_logo(size=logo_size, bw=False)
    base.paste(logo, (tx - (logo_size + 32) // 2, 205), logo)
    
    # 2. Main Title: NOIR in Saturated Dracula Blood-Red
    draw_dracula_title(draw, "NOIR", tx, 310, fonts["dracula_large"], (218, 18, 26, 255), (70, 6, 10, 220))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_title"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 420), ben, font=fonts["bengali_title"], fill=(0, 0, 0, 255))
    
    # 4. Taglines (Stark Black on Bright White Paper)
    sub1 = "A BETWEEN THE NOTES ORIGINAL"
    bb_s1 = draw.textbbox((0, 0), sub1, font=fonts["sub_regular"])
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, 462), sub1, font=fonts["sub_regular"], fill=(0, 0, 0, 255))
    
    sub2 = "AN EXPERIMENTAL ANALOG HORROR TRANSMISSION"
    bb_s2 = draw.textbbox((0, 0), sub2, font=fonts["meta_regular"])
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, 488), sub2, font=fonts["meta_regular"], fill=(0, 0, 0, 255))
    
    # 5. Clear Credits
    cred = "ORIGINAL TUNE: ATANDRA & SAYAN  •  SECTOR WB"
    bb_c = draw.textbbox((0, 0), cred, font=fonts["meta_regular"])
    draw.text((tx - (bb_c[2]-bb_c[0]) // 2, 514), cred, font=fonts["meta_regular"], fill=(0, 0, 0, 255))
    
    # 6. Red Emergency Box on Roadside
    box_x, box_y = 580, 855
    draw.rectangle([box_x, box_y, box_x + 225, box_y + 48], fill=(195, 18, 25), outline=(255, 255, 255), width=2)
    draw.text((box_x + 16, box_y + 13), "IN CASE OF NISHIDAK", font=fonts["emergency"], fill=(255, 255, 255))
    
    return base

# =============================================================================
# VARIATION 3: ACOUSTIC PINS & THE UNCANNY FELINE (Studio B&W Illumination)
# =============================================================================
def render_var3():
    base_bgr = cv2.imread(os.path.join(FLOW_DIR, "scene-03.jpeg"))
    # Spotlight illumination on text area
    lit_bgr = illuminate_board_zone(base_bgr, 880, 1280, 150, 620, intensity=1.85, warm=False)
    base = Image.fromarray(cv2.cvtColor(lit_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(base)
    
    tx = 1070
    
    # 1. Silver Logo Medallion
    logo_size = 120
    logo = get_styled_logo(size=logo_size, bw=True)
    base.paste(logo, (tx - (logo_size + 32) // 2, 160), logo)
    
    # 2. Main Title: NOIR in Pure White with deep black shadow
    draw_dracula_title(draw, "NOIR", tx, 290, fonts["dracula_huge"], (255, 255, 255, 255), (0, 0, 0, 240))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_title"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2 + 1, 425 + 1), ben, font=fonts["bengali_title"], fill=(0, 0, 0, 220))
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 425), ben, font=fonts["bengali_title"], fill=(250, 250, 245, 255))
    
    # 4. Taglines
    sub1 = "THE UNCANNY FELINE TRANSMISSION"
    bb_s1 = draw.textbbox((0, 0), sub1, font=fonts["tag_bold"])
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2 + 1, 475 + 1), sub1, font=fonts["tag_bold"], fill=(0, 0, 0, 220))
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, 475), sub1, font=fonts["tag_bold"], fill=(245, 245, 240, 255))
    
    # 5. Clear Credits
    cred1 = "ACOUSTIC COMPOSITION: ATANDRA  •  VISUAL ENGINE: SAYAN"
    bb_c1 = draw.textbbox((0, 0), cred1, font=fonts["cred_bold"])
    draw.text((tx - (bb_c1[2]-bb_c1[0]) // 2 + 1, 510 + 1), cred1, font=fonts["cred_bold"], fill=(0, 0, 0, 220))
    draw.text((tx - (bb_c1[2]-bb_c1[0]) // 2, 510), cred1, font=fonts["cred_bold"], fill=(235, 235, 230, 255))
    
    cred2 = "AFTER MIDNIGHT, SOMEWHERE ELSE  •  STREAMING ON ALL PLATFORMS"
    bb_c2 = draw.textbbox((0, 0), cred2, font=fonts["meta_regular"])
    draw.text((tx - (bb_c2[2]-bb_c2[0]) // 2 + 1, 540 + 1), cred2, font=fonts["meta_regular"], fill=(0, 0, 0, 220))
    draw.text((tx - (bb_c2[2]-bb_c2[0]) // 2, 540), cred2, font=fonts["meta_regular"], fill=(215, 215, 210, 255))
    
    return base

# =============================================================================
# VARIATION 4: DAMODAR HIGHWAY METAMORPHOSIS (Illuminated Highway Board)
# =============================================================================
def render_var4():
    base_bgr = cv2.imread(os.path.join(FLOW_DIR, "scene-04.jpeg"))
    # Highway floodlight illumination on board: x [800, 1160], y [180, 600]
    lit_bgr = illuminate_board_zone(base_bgr, 800, 1160, 180, 600, intensity=1.80, warm=True)
    base = Image.fromarray(cv2.cvtColor(lit_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(base)
    
    tx = 980
    
    # 1. Color Medallion Logo
    logo_size = 115
    logo = get_styled_logo(size=logo_size, bw=False)
    base.paste(logo, (tx - (logo_size + 32) // 2, 190), logo)
    
    # 2. Main Title: NOIR in High-Contrast Dracula Burgundy
    draw_dracula_title(draw, "NOIR", tx, 310, fonts["dracula_huge"], (205, 20, 28, 255), (70, 8, 12, 200))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_title"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 435), ben, font=fonts["bengali_title"], fill=(0, 0, 0, 255))
    
    # 4. Taglines
    sub1 = "A BETWEEN THE NOTES ORIGINAL"
    bb_s1 = draw.textbbox((0, 0), sub1, font=fonts["tag_bold"])
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, 480), sub1, font=fonts["tag_bold"], fill=(0, 0, 0, 255))
    
    sub2 = "A 1994 Rural Bengal Emergency Broadcast"
    bb_s2 = draw.textbbox((0, 0), sub2, font=fonts["sub_regular"])
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, 510), sub2, font=fonts["sub_regular"], fill=(25, 15, 18, 255))
    
    # 5. Clear Credits
    cred = "MUSIC & SOUND: ATANDRA  •  VISUAL ENGINE: SAYAN  •  BETWEEN THE NOTES"
    bb_c = draw.textbbox((0, 0), cred, font=fonts["cred_bold"])
    draw.text((tx - (bb_c[2]-bb_c[0]) // 2, 540), cred, font=fonts["cred_bold"], fill=(0, 0, 0, 255))
    
    return base

# =============================================================================
# VARIATION 5: THE FALLING MAN ABYSS (Illuminated End Credits Board)
# =============================================================================
def render_var5():
    base_bgr = cv2.imread(os.path.join(FLOW_DIR, "scene-05.jpeg"))
    # Overhead floodlight on credits zone: x [720, 1160], y [160, 680]
    lit_bgr = illuminate_board_zone(base_bgr, 720, 1160, 160, 680, intensity=1.90, warm=False)
    base = Image.fromarray(cv2.cvtColor(lit_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(base)
    
    tx = 940
    
    # 1. Prominent Between the Notes Hallmark Logo
    logo_size = 120
    logo = get_styled_logo(size=logo_size, bw=True)
    base.paste(logo, (tx - (logo_size + 32) // 2, 175), logo)
    
    # 2. Main Title: NOIR
    draw_dracula_title(draw, "NOIR", tx, 300, fonts["dracula_large"], (0, 0, 0, 255), (170, 170, 175, 160))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_title"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 420), ben, font=fonts["bengali_title"], fill=(0, 0, 0, 255))
    
    # 4. Formal Theatrical End Credits Block (High Contrast Black)
    lines = [
        ("A BETWEEN THE NOTES PRESENTATION", fonts["tag_bold"], (0, 0, 0)),
        ("ORIGINAL SCORE & SOUND DESIGN: ATANDRA", fonts["cred_bold"], (0, 0, 0)),
        ("DIRECTED & VISUAL ENGINE BY SAYAN", fonts["cred_bold"], (0, 0, 0)),
        ("ANALOG HORROR BROADCAST ARCHIVE  •  1994", fonts["meta_regular"], (15, 15, 20)),
        ("ALL RIGHTS RESERVED  •  BETWEEN THE NOTES", fonts["meta_regular"], (25, 25, 30))
    ]
    cur_y = 465
    for text, fnt, col in lines:
        b = draw.textbbox((0, 0), text, font=fnt)
        w_t = b[2] - b[0]
        draw.text((tx - w_t // 2, cur_y), text, font=fnt, fill=col)
        cur_y += 28
        
    return base

variations = [
    ("poster_var1_bw_classic.png", render_var1),
    ("poster_var2_crimson_color.png", render_var2),
    ("poster_var3_acoustic_feline.png", render_var3),
    ("poster_var4_highway_metamorphosis.png", render_var4),
    ("poster_var5_abyss_end_credits.png", render_var5),
]

for fname, renderer in variations:
    res = renderer()
    local_out = os.path.join(ROOT, "assets", "posters", fname)
    art_out = os.path.join(ARTIFACT_DIR, fname)
    res.save(local_out, quality=98)
    res.save(art_out, quality=98)
    print(f"Rendered illuminated high-readability poster: {fname} -> {local_out}")
