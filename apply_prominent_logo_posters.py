import os
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

# Distinct fonts for varied sizes
fonts = {
    "dracula_130": get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 130),
    "dracula_115": get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 115),
    "dracula_95": get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 95),
    "bengali_32": get_font(["NotoSansBengali-Bold.ttf", "kalpurush.ttf"], 32),
    "bengali_26": get_font(["NotoSansBengali-Bold.ttf", "kalpurush.ttf"], 26),
    "tag_18": get_font(["GOTHICB.TTF", "corbelb.ttf", "impact.ttf"], 18),
    "tag_15": get_font(["GOTHICB.TTF", "corbelb.ttf", "impact.ttf"], 15),
    "tag_13": get_font(["GOTHICB.TTF", "corbelb.ttf", "impact.ttf"], 13),
    "sub_14": get_font(["GOTHIC.TTF", "corbel.ttf", "IBMPlexMono-Regular.ttf"], 14),
    "sub_12": get_font(["GOTHIC.TTF", "corbel.ttf", "IBMPlexMono-Regular.ttf"], 12),
    "meta_12": get_font(["GOTHICB.TTF", "corbelb.ttf", "IBMPlexMono-Bold.ttf"], 12),
    "meta_10": get_font(["GOTHICB.TTF", "corbelb.ttf", "IBMPlexMono-Bold.ttf"], 10),
    "emergency": get_font(["impact.ttf", "GOTHICB.TTF"], 18)
}

logo_img = Image.open(LOGO_PATH).convert("RGBA")

def get_styled_logo(size=120, bw=False, shadow=True):
    resized = logo_img.resize((size, size), Image.Resampling.LANCZOS)
    if bw:
        r, g, b, a = resized.split()
        gray = resized.convert("L")
        lut = [int(np.clip((i - 128) * 1.35 + 140, 0, 255)) for i in range(256)]
        gray_contrasted = gray.point(lut)
        resized = Image.merge("RGBA", (gray_contrasted, gray_contrasted, gray_contrasted, a))
    
    if not shadow:
        return resized
        
    pad = 16
    shadow_canvas = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_canvas)
    s_draw.ellipse([pad + 2, pad + 4, pad + size + 2, pad + size + 4], fill=(0, 0, 0, 160))
    shadow_blurred = shadow_canvas.filter(ImageFilter.GaussianBlur(6))
    shadow_blurred.paste(resized, (pad, pad), resized)
    return shadow_blurred

def draw_dracula_letterforms(draw, text, x_center, y_top, font, fill_color, shadow_color=None):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    tx = x_center - tw // 2
    
    if shadow_color:
        draw.text((tx + 2, y_top + 3), text, font=font, fill=shadow_color)
    draw.text((tx, y_top), text, font=font, fill=fill_color)
    
    # Sharp spires on top and bottom serifs
    draw.polygon([(tx + 3, y_top), (tx + 7, y_top), (tx + 5, y_top - 7)], fill=fill_color)
    draw.polygon([(tx + tw - 8, y_top), (tx + tw - 4, y_top), (tx + tw - 6, y_top - 7)], fill=fill_color)

# =============================================================================
# VARIATION 1: B&W CLASSIC FILM NOIR BILLBOARD (Dracula Stake Shadow)
# =============================================================================
def render_var1():
    base = Image.open(os.path.join(FLOW_DIR, "scene-01.jpeg")).convert("RGBA")
    draw = ImageDraw.Draw(base)
    
    # Perfectly centered in the clean white billboard quadrant [780, 1080]
    tx = 930
    
    # 1. Between the Notes Circular Logo Medallion
    logo_size = 120
    logo = get_styled_logo(size=logo_size, bw=True, shadow=True)
    base.paste(logo, (tx - (logo_size + 32) // 2, 160), logo)
    
    # 2. Main Title: NOIR (Tall Jet Black Gothic Serif)
    draw_dracula_letterforms(draw, "NOIR", tx, 295, fonts["dracula_130"], (8, 8, 12, 255), (160, 160, 165, 120))
    
    # 3. Bengali Title: নি শি ডা ক
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_32"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 425), ben, font=fonts["bengali_32"], fill=(12, 12, 16, 255))
    
    # 4. Tagline: FROM THE CREATORS OF AFTER MIDNIGHT
    sub1 = "FROM THE CREATORS OF AFTER MIDNIGHT"
    bb_s1 = draw.textbbox((0, 0), sub1, font=fonts["tag_15"])
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, 475), sub1, font=fonts["tag_15"], fill=(15, 15, 20, 255))
    
    # 5. Subtitle
    sub2 = "A Bengali Cosmic Horror Broadcast"
    bb_s2 = draw.textbbox((0, 0), sub2, font=fonts["sub_14"])
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, 505), sub2, font=fonts["sub_14"], fill=(35, 35, 40, 255))
    
    # 6. Metadata row
    cred_pill = "BHARAT DARPAN 1994  •  SCORE: ATANDRA & SAYAN"
    bb_c = draw.textbbox((0, 0), cred_pill, font=fonts["meta_12"])
    draw.text((tx - (bb_c[2]-bb_c[0]) // 2, 538), cred_pill, font=fonts["meta_12"], fill=(45, 45, 50, 255))
    
    # 7. Environmental Box on Fence below: "IN CASE OF NISHIDAK"
    box_x, box_y = 585, 838
    draw.rectangle([box_x, box_y, box_x + 210, box_y + 45], fill=(12, 12, 15), outline=(90, 90, 95), width=2)
    draw.text((box_x + 16, box_y + 11), "IN CASE OF NISHIDAK", font=fonts["emergency"], fill=(235, 235, 240))
    
    return base.convert("RGB")

# =============================================================================
# VARIATION 2: CRIMSON COLOR EDITION (Dracula Blood-Red on White Board)
# =============================================================================
def render_var2():
    base = Image.open(os.path.join(FLOW_DIR, "scene-02.jpeg")).convert("RGBA")
    draw = ImageDraw.Draw(base)
    
    # Centered in the perspective-shortened board face [760, 960]
    tx = 860
    
    # 1. Color Medallion Logo
    logo_size = 95
    logo = get_styled_logo(size=logo_size, bw=False, shadow=True)
    base.paste(logo, (tx - (logo_size + 32) // 2, 235), logo)
    
    # 2. Main Title: NOIR in Saturated Dracula Blood-Red
    draw_dracula_letterforms(draw, "NOIR", tx, 340, fonts["dracula_95"], (215, 24, 30, 255), (60, 10, 14, 220))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_26"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 440), ben, font=fonts["bengali_26"], fill=(15, 12, 16, 255))
    
    # 4. Taglines (Crisp Black on White Paper)
    sub1 = "FROM THE CREATORS OF AFTER MIDNIGHT"
    bb_s1 = draw.textbbox((0, 0), sub1, font=fonts["tag_13"])
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, 480), sub1, font=fonts["tag_13"], fill=(10, 8, 12, 255))
    
    sub2 = "AN EXPERIMENTAL ANALOG HORROR"
    bb_s2 = draw.textbbox((0, 0), sub2, font=fonts["sub_12"])
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, 505), sub2, font=fonts["sub_12"], fill=(25, 12, 16, 255))
    
    # 5. Metadata pill
    cred_pill = "ORIGINAL TUNE: ATANDRA & SAYAN"
    bb_c = draw.textbbox((0, 0), cred_pill, font=fonts["meta_10"])
    draw.text((tx - (bb_c[2]-bb_c[0]) // 2, 532), cred_pill, font=fonts["meta_10"], fill=(35, 18, 20, 255))
    
    # 6. Red Emergency Box on Roadside with glass glare
    box_x, box_y = 580, 855
    draw.rectangle([box_x, box_y, box_x + 225, box_y + 48], fill=(168, 20, 26), outline=(245, 240, 240), width=2)
    draw.text((box_x + 16, box_y + 13), "IN CASE OF NISHIDAK", font=fonts["emergency"], fill=(255, 255, 255))
    
    return base.convert("RGB")

# =============================================================================
# VARIATION 3: ACOUSTIC PINS & THE UNCANNY FELINE (B&W Studio Horror)
# =============================================================================
def render_var3():
    base = Image.open(os.path.join(FLOW_DIR, "scene-03.jpeg")).convert("RGBA")
    draw = ImageDraw.Draw(base)
    
    # Clean night space to the right of the sound baffle
    tx = 1060
    
    # 1. Prominent Between the Notes Silver Logo
    logo_size = 125
    logo = get_styled_logo(size=logo_size, bw=True, shadow=True)
    base.paste(logo, (tx - (logo_size + 32) // 2, 165), logo)
    
    # 2. Main Title: NOIR in Glowing Silver / Ivory
    draw_dracula_letterforms(draw, "NOIR", tx, 305, fonts["dracula_130"], (248, 248, 242, 255), (15, 15, 18, 240))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_32"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 435), ben, font=fonts["bengali_32"], fill=(225, 225, 220, 250))
    
    # 4. Taglines
    sub1 = "THE UNCANNY FELINE TRANSMISSION"
    bb_s1 = draw.textbbox((0, 0), sub1, font=fonts["tag_15"])
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, 485), sub1, font=fonts["tag_15"], fill=(220, 220, 215, 255))
    
    sub2 = "ACOUSTIC COMPOSITION: ATANDRA  •  VISUAL ENGINE: SAYAN"
    bb_s2 = draw.textbbox((0, 0), sub2, font=fonts["sub_14"])
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, 515), sub2, font=fonts["sub_14"], fill=(185, 185, 180, 255))
    
    cred_pill = "AFTER MIDNIGHT, SOMEWHERE ELSE  •  STREAMING NOW"
    bb_c = draw.textbbox((0, 0), cred_pill, font=fonts["meta_12"])
    draw.text((tx - (bb_c[2]-bb_c[0]) // 2, 545), cred_pill, font=fonts["meta_12"], fill=(205, 205, 200, 255))
    
    return base.convert("RGB")

# =============================================================================
# VARIATION 4: DAMODAR HIGHWAY METAMORPHOSIS (Stormy Palms Color)
# =============================================================================
def render_var4():
    base = Image.open(os.path.join(FLOW_DIR, "scene-04.jpeg")).convert("RGBA")
    draw = ImageDraw.Draw(base)
    
    # Centered in the highway billboard board face [800, 1140]
    tx = 970
    
    # 1. Color Between the Notes Logo Medallion
    logo_size = 110
    logo = get_styled_logo(size=logo_size, bw=False, shadow=True)
    base.paste(logo, (tx - (logo_size + 32) // 2, 205), logo)
    
    # 2. Main Title: NOIR in Dark Crimson (#B41A22)
    draw_dracula_letterforms(draw, "NOIR", tx, 325, fonts["dracula_115"], (195, 24, 30, 255), (45, 15, 20, 180))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_32"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 445), ben, font=fonts["bengali_32"], fill=(25, 20, 22, 255))
    
    # 4. Taglines
    sub1 = "DO NOT ANSWER THE CALLING"
    bb_s1 = draw.textbbox((0, 0), sub1, font=fonts["tag_15"])
    draw.text((tx - (bb_s1[2]-bb_s1[0]) // 2, 490), sub1, font=fonts["tag_15"], fill=(20, 16, 18, 255))
    
    sub2 = "A 1994 Rural Bengal Emergency Broadcast"
    bb_s2 = draw.textbbox((0, 0), sub2, font=fonts["sub_14"])
    draw.text((tx - (bb_s2[2]-bb_s2[0]) // 2, 518), sub2, font=fonts["sub_14"], fill=(50, 35, 38, 255))
    
    cred_pill = "PRODUCED BY BETWEEN THE NOTES  •  ATANDRA & SAYAN"
    bb_c = draw.textbbox((0, 0), cred_pill, font=fonts["meta_12"])
    draw.text((tx - (bb_c[2]-bb_c[0]) // 2, 545), cred_pill, font=fonts["meta_12"], fill=(65, 45, 48, 255))
    
    return base.convert("RGB")

# =============================================================================
# VARIATION 5: THE FALLING MAN ABYSS (End Credits Epilogue in B&W)
# =============================================================================
def render_var5():
    base = Image.open(os.path.join(FLOW_DIR, "scene-05.jpeg")).convert("RGBA")
    draw = ImageDraw.Draw(base)
    
    # Clean frontal board quadrant [720, 1140]
    tx = 930
    
    # 1. Prominent Between the Notes Hallmark Logo
    logo_size = 120
    logo = get_styled_logo(size=logo_size, bw=True, shadow=True)
    base.paste(logo, (tx - (logo_size + 32) // 2, 190), logo)
    
    # 2. Main Title: NOIR
    draw_dracula_letterforms(draw, "NOIR", tx, 325, fonts["dracula_115"], (10, 10, 14, 255), (140, 140, 145, 120))
    
    # 3. Bengali Title
    ben = "নি  শি  ডা  ক"
    bb_b = draw.textbbox((0, 0), ben, font=fonts["bengali_32"])
    draw.text((tx - (bb_b[2]-bb_b[0]) // 2, 450), ben, font=fonts["bengali_32"], fill=(15, 15, 18, 255))
    
    # 4. Formal End Credits Block (Theatrical Billing Block)
    lines = [
        ("END TRANSMISSION", fonts["tag_18"], (12, 12, 16)),
        ("ORIGINAL SCORE & SOUND DESIGN: ATANDRA", fonts["sub_14"], (20, 20, 24)),
        ("DIRECTED & VISUAL ENGINE BY SAYAN", fonts["sub_14"], (20, 20, 24)),
        ("AFTER MIDNIGHT, SOMEWHERE ELSE  •  1994", fonts["meta_12"], (35, 35, 40)),
        ("ALL RIGHTS RESERVED  •  BETWEEN THE NOTES", fonts["meta_10"], (50, 50, 55))
    ]
    cur_y = 495
    for text, fnt, col in lines:
        b = draw.textbbox((0, 0), text, font=fnt)
        w_t = b[2] - b[0]
        draw.text((tx - w_t // 2, cur_y), text, font=fnt, fill=col)
        cur_y += 28
        
    return base.convert("RGB")

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
    print(f"Rendered refined poster: {fname} -> {local_out}")
