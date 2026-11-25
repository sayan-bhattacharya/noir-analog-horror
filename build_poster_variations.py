import os
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

font_title_serif = get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 138)
font_title_serif_med = get_font(["ONYX.TTF", "georgiab.ttf", "timesbd.ttf"], 110)
font_bengali_title = get_font(["NotoSansBengali-Bold.ttf", "kalpurush.ttf", "vrinda.ttf"], 44)
font_bug = get_font(["GOTHICB.TTF", "corbelb.ttf", "impact.ttf"], 28)
font_subtitle = get_font(["GOTHICB.TTF", "corbelb.ttf", "IBMPlexMono-Bold.ttf"], 24)
font_small = get_font(["GOTHIC.TTF", "corbel.ttf", "IBMPlexMono-Regular.ttf"], 19)
font_box = get_font(["impact.ttf", "GOTHICB.TTF", "IBMPlexMono-Bold.ttf"], 22)

# Load BTN circular logo
logo_raw = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
if logo_raw is None:
    logo_raw = cv2.imread(r"E:\betweenthenotes\public\images\logo.jpg")

def create_circular_logo(size=120, bw=False):
    if logo_raw is None:
        return None
    # Resize
    resized = cv2.resize(logo_raw, (size, size), interpolation=cv2.INTER_AREA)
    if resized.shape[2] == 3:
        # Create circular alpha mask
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

# =============================================================================
# VARIATION 1: B&W CLASSIC FILM NOIR BILLBOARD (The Stake Horror)
# =============================================================================
def render_variation_1():
    base_path = os.path.join(FLOW_DIR, "scene-01.jpeg")
    img = Image.open(base_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Billboard center coordinates for text (Right side blank area)
    # Billboard extends roughly x: 620 to 1100, y: 160 to 620
    tx = 860
    
    # 1. BBC-style channel bug (Between the Notes / Bharat Darpan)
    bug_text = "BETWEEN THE NOTES"
    bbox = draw.textbbox((0, 0), bug_text, font=font_bug)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = tx - bw // 2, 195
    # Dark rounded pill
    draw.rounded_rectangle([bx - 16, by - 8, bx + bw + 16, by + bh + 10], radius=6, fill=(18, 18, 20, 240))
    draw.text((bx, by), bug_text, font=font_bug, fill=(245, 245, 245))

    # 2. Main Title: NOIR (Tall Dracula Style Serif)
    # In Dracula it is tall and red, in B&W it is obsidian black with sharp serifs
    title_text = "NOIR"
    tbox = draw.textbbox((0, 0), title_text, font=font_title_serif)
    tw = tbox[2] - tbox[0]
    draw.text((tx - tw // 2, 245), title_text, font=font_title_serif, fill=(12, 12, 15, 255))
    
    # Bengali Title beside/underneath
    ben_text = "নি শি ডা ক"
    bbox_b = draw.textbbox((0, 0), ben_text, font=font_bengali_title)
    bw_b = bbox_b[2] - bbox_b[0]
    draw.text((tx - bw_b // 2, 400), ben_text, font=font_bengali_title, fill=(25, 25, 30, 240))

    # 3. Subtitle lines (Matching Dracula layout)
    sub1 = "FROM THE CREATORS OF AFTER MIDNIGHT"
    bbox_s1 = draw.textbbox((0, 0), sub1, font=font_subtitle)
    draw.text((tx - (bbox_s1[2]-bbox_s1[0]) // 2, 465), sub1, font=font_subtitle, fill=(40, 40, 45, 255))

    sub2 = "A Bengali Cosmic Horror Transmission"
    bbox_s2 = draw.textbbox((0, 0), sub2, font=font_small)
    draw.text((tx - (bbox_s2[2]-bbox_s2[0]) // 2, 502), sub2, font=font_small, fill=(70, 70, 75, 255))

    # 4. Air Date / Credits
    sub3 = "MUSIC: ATANDRA  •  VISUAL ENGINE: SAYAN"
    bbox_s3 = draw.textbbox((0, 0), sub3, font=font_small)
    draw.text((tx - (bbox_s3[2]-bbox_s3[0]) // 2, 532), sub3, font=font_small, fill=(85, 85, 90, 255))

    # 5. BTN Circular Logo Emblem (like the iPlayer emblem)
    btn_logo = create_circular_logo(size=72, bw=True)
    if btn_logo:
        img.paste(btn_logo, (tx - 36, 568), btn_logo)

    # 6. Environmental detail: "IN CASE OF NISHIDAK" emergency box below billboard
    eb_x, eb_y = 580, 835
    draw.rectangle([eb_x, eb_y, eb_x + 190, eb_y + 45], fill=(15, 15, 18), outline=(60, 60, 65), width=2)
    draw.text((eb_x + 15, eb_y + 11), "IN CASE OF NISHIDAK", font=font_small, fill=(220, 220, 225))

    return img.convert("RGB")

# =============================================================================
# VARIATION 2: CRIMSON COLOR EDITION (Dracula Blood & Red Flare Aesthetic)
# =============================================================================
def render_variation_2():
    base_path = os.path.join(FLOW_DIR, "scene-02.jpeg")
    img = Image.open(base_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Billboard right-hand area
    tx = 860

    # 1. Black BBC-style pill for BETWEEN THE NOTES
    bug_text = "BETWEEN THE NOTES"
    bbox = draw.textbbox((0, 0), bug_text, font=font_bug)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = tx - bw // 2, 280
    draw.rounded_rectangle([bx - 16, by - 8, bx + bw + 16, by + bh + 10], radius=6, fill=(14, 14, 18, 240))
    draw.text((bx, by), bug_text, font=font_bug, fill=(245, 245, 245))

    # 2. Main Title: NOIR in Saturated Blood-Crimson (Exact Dracula title styling)
    title_text = "NOIR"
    tbox = draw.textbbox((0, 0), title_text, font=font_title_serif)
    tw = tbox[2] - tbox[0]
    # Subtle drop shadow for physical print depth
    draw.text((tx - tw // 2 + 3, 335 + 3), title_text, font=font_title_serif, fill=(15, 12, 16, 180))
    draw.text((tx - tw // 2, 335), title_text, font=font_title_serif, fill=(195, 26, 32, 255))

    # Bengali Title
    ben_text = "নি শি ডা ক"
    bbox_b = draw.textbbox((0, 0), ben_text, font=font_bengali_title)
    bw_b = bbox_b[2] - bbox_b[0]
    draw.text((tx - bw_b // 2, 490), ben_text, font=font_bengali_title, fill=(20, 20, 24, 230))

    # 3. Subtitles
    sub1 = "FROM THE CREATORS OF AFTER MIDNIGHT"
    bbox_s1 = draw.textbbox((0, 0), sub1, font=font_subtitle)
    draw.text((tx - (bbox_s1[2]-bbox_s1[0]) // 2, 555), sub1, font=font_subtitle, fill=(28, 28, 34, 255))

    sub2 = "AN EXPERIMENTAL ANALOG HORROR BROADCAST"
    bbox_s2 = draw.textbbox((0, 0), sub2, font=font_small)
    draw.text((tx - (bbox_s2[2]-bbox_s2[0]) // 2, 592), sub2, font=font_small, fill=(65, 30, 32, 255))

    # 4. Color BTN Medallion Logo
    btn_logo = create_circular_logo(size=78, bw=False)
    if btn_logo:
        img.paste(btn_logo, (tx - 39, 630), btn_logo)

    # 5. Red Emergency Box on Roadside (Matching Dracula "IN CASE OF VAMPIRES")
    box_x, box_y = 580, 855
    draw.rectangle([box_x, box_y, box_x + 220, box_y + 48], fill=(160, 20, 24), outline=(240, 235, 235), width=2)
    draw.text((box_x + 16, box_y + 12), "IN CASE OF NISHIDAK", font=font_box, fill=(255, 255, 255))

    return img.convert("RGB")

# =============================================================================
# VARIATION 3: ACOUSTIC PINS & FELINE SHADOW (B&W Sepia Tone)
# =============================================================================
def render_variation_3():
    base_path = os.path.join(FLOW_DIR, "scene-03.jpeg")
    img = Image.open(base_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Street background on right side
    tx = 840

    # 1. Channel bug
    bug_text = "BETWEEN THE NOTES"
    bbox = draw.textbbox((0, 0), bug_text, font=font_bug)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = tx - bw // 2, 230
    draw.rounded_rectangle([bx - 16, by - 8, bx + bw + 16, by + bh + 10], radius=6, fill=(235, 235, 235, 240))
    draw.text((bx, by), bug_text, font=font_bug, fill=(18, 18, 20))

    # 2. Main Title: NOIR in glowing ivory/silver
    title_text = "NOIR"
    tbox = draw.textbbox((0, 0), title_text, font=font_title_serif)
    tw = tbox[2] - tbox[0]
    draw.text((tx - tw // 2, 280), title_text, font=font_title_serif, fill=(245, 245, 240, 255))

    # Bengali Title
    ben_text = "নি শি ডা ক"
    bbox_b = draw.textbbox((0, 0), ben_text, font=font_bengali_title)
    bw_b = bbox_b[2] - bbox_b[0]
    draw.text((tx - bw_b // 2, 435), ben_text, font=font_bengali_title, fill=(210, 210, 205, 230))

    # 3. Subtitles
    sub1 = "THE UNCANNY FELINE TRANSMISSION"
    bbox_s1 = draw.textbbox((0, 0), sub1, font=font_subtitle)
    draw.text((tx - (bbox_s1[2]-bbox_s1[0]) // 2, 500), sub1, font=font_subtitle, fill=(200, 200, 195, 255))

    sub2 = "Original Atmospheric Score: Atandra  •  Visuals: Sayan"
    bbox_s2 = draw.textbbox((0, 0), sub2, font=font_small)
    draw.text((tx - (bbox_s2[2]-bbox_s2[0]) // 2, 538), sub2, font=font_small, fill=(160, 160, 155, 255))

    # 4. Engraved Medallion
    btn_logo = create_circular_logo(size=76, bw=True)
    if btn_logo:
        img.paste(btn_logo, (tx - 38, 580), btn_logo)

    return img.convert("RGB")

# =============================================================================
# VARIATION 4: DAMODAR HIGHWAY METAMORPHOSIS (Color 1990s Analog)
# =============================================================================
def render_variation_4():
    base_path = os.path.join(FLOW_DIR, "scene-04.jpeg")
    img = Image.open(base_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Billboard board face on right
    tx = 875

    # 1. Dark pill bug
    bug_text = "BETWEEN THE NOTES"
    bbox = draw.textbbox((0, 0), bug_text, font=font_bug)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = tx - bw // 2, 230
    draw.rounded_rectangle([bx - 16, by - 8, bx + bw + 16, by + bh + 10], radius=6, fill=(20, 22, 28, 230))
    draw.text((bx, by), bug_text, font=font_bug, fill=(245, 245, 245))

    # 2. Main Title: NOIR in Dark Crimson
    title_text = "NOIR"
    tbox = draw.textbbox((0, 0), title_text, font=font_title_serif)
    tw = tbox[2] - tbox[0]
    draw.text((tx - tw // 2 + 2, 280 + 2), title_text, font=font_title_serif, fill=(15, 12, 16, 160))
    draw.text((tx - tw // 2, 280), title_text, font=font_title_serif, fill=(185, 28, 36, 255))

    # Bengali Title
    ben_text = "নি শি ডা ক"
    bbox_b = draw.textbbox((0, 0), ben_text, font=font_bengali_title)
    bw_b = bbox_b[2] - bbox_b[0]
    draw.text((tx - bw_b // 2, 435), ben_text, font=font_bengali_title, fill=(35, 30, 32, 230))

    # 3. Subtitles
    sub1 = "DO NOT ANSWER THE CALLING"
    bbox_s1 = draw.textbbox((0, 0), sub1, font=font_subtitle)
    draw.text((tx - (bbox_s1[2]-bbox_s1[0]) // 2, 498), sub1, font=font_subtitle, fill=(45, 38, 40, 255))

    sub2 = "A 1994 Rural Bengal Emergency Broadcast"
    bbox_s2 = draw.textbbox((0, 0), sub2, font=font_small)
    draw.text((tx - (bbox_s2[2]-bbox_s2[0]) // 2, 532), sub2, font=font_small, fill=(75, 60, 62, 255))

    # 4. Color BTN Logo
    btn_logo = create_circular_logo(size=74, bw=False)
    if btn_logo:
        img.paste(btn_logo, (tx - 37, 570), btn_logo)

    return img.convert("RGB")

# =============================================================================
# VARIATION 5: END CREDITS EPILOGUE (B&W Rain Plunge into Abyss)
# =============================================================================
def render_variation_5():
    base_path = os.path.join(FLOW_DIR, "scene-05.jpeg")
    img = Image.open(base_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Right side blank paper texture
    tx = 860

    # 1. BBC style header
    bug_text = "BETWEEN THE NOTES"
    bbox = draw.textbbox((0, 0), bug_text, font=font_bug)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bx, by = tx - bw // 2, 220
    draw.rounded_rectangle([bx - 16, by - 8, bx + bw + 16, by + bh + 10], radius=6, fill=(15, 15, 18, 240))
    draw.text((bx, by), bug_text, font=font_bug, fill=(245, 245, 245))

    # 2. Main Title: NOIR
    title_text = "NOIR"
    tbox = draw.textbbox((0, 0), title_text, font=font_title_serif)
    tw = tbox[2] - tbox[0]
    draw.text((tx - tw // 2, 270), title_text, font=font_title_serif, fill=(18, 18, 22, 255))

    # Bengali Title
    ben_text = "নি শি ডা ক"
    bbox_b = draw.textbbox((0, 0), ben_text, font=font_bengali_title)
    bw_b = bbox_b[2] - bbox_b[0]
    draw.text((tx - bw_b // 2, 425), ben_text, font=font_bengali_title, fill=(30, 30, 35, 230))

    # 3. Formal End Credits Block
    lines = [
        ("END TRANSMISSION", font_subtitle, (40, 40, 45)),
        ("COMPOSED & PERFORMED BY ATANDRA", font_small, (60, 60, 65)),
        ("DIRECTED & PRODUCED BY SAYAN", font_small, (60, 60, 65)),
        ("AFTER MIDNIGHT, SOMEWHERE ELSE  •  1994", font_small, (90, 90, 95))
    ]
    cur_y = 485
    for text, fnt, col in lines:
        b = draw.textbbox((0, 0), text, font=fnt)
        w = b[2] - b[0]
        draw.text((tx - w // 2, cur_y), text, font=fnt, fill=col)
        cur_y += 32

    # 4. BTN Hallmark Seal
    btn_logo = create_circular_logo(size=76, bw=True)
    if btn_logo:
        img.paste(btn_logo, (tx - 38, cur_y + 10), btn_logo)

    return img.convert("RGB")

# Execute and Save all 5
variations = [
    ("poster_var1_bw_classic.png", render_variation_1),
    ("poster_var2_crimson_color.png", render_variation_2),
    ("poster_var3_acoustic_feline.png", render_variation_3),
    ("poster_var4_highway_metamorphosis.png", render_variation_4),
    ("poster_var5_abyss_end_credits.png", render_variation_5),
]

os.makedirs(os.path.join(ROOT, "assets", "posters"), exist_ok=True)

for fname, renderer in variations:
    res = renderer()
    local_out = os.path.join(ROOT, "assets", "posters", fname)
    art_out = os.path.join(ARTIFACT_DIR, fname)
    res.save(local_out, quality=95)
    res.save(art_out, quality=95)
    print(f"Rendered: {fname} -> {local_out}")
