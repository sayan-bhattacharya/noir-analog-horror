import sys
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = r"e:\betweenthenotes\noir_film_project"
FONTS_DIR = os.path.join(ROOT, "noir_film", "fonts")
BN_FONT = os.path.join(FONTS_DIR, "NotoSansBengali-Bold.ttf")
EN_FONT = os.path.join(FONTS_DIR, "IBMPlexMono-Bold.ttf")

w, h = 1280, 720
frame = np.zeros((h, w, 3), dtype=np.uint8)

# Dark room ambient
frame[:, :] = [8, 8, 10]

# Bezel / Screen dimensions
bw = int(w * 0.94)
bh = int(h * 0.56)
bx1 = (w - bw) // 2
by1 = (h - bh) // 2
bx2 = bx1 + bw
by2 = by1 + bh

# Television Cabinet / Bezel Trim
cv2.rectangle(frame, (bx1 - 8, by1 - 8), (bx2 + 8, by2 + 8), (22, 18, 14), -1)
cv2.rectangle(frame, (bx1 - 8, by1 - 8), (bx2 + 8, by2 + 8), (48, 42, 34), 2)
cv2.rectangle(frame, (bx1 - 4, by1 - 4), (bx2 + 4, by2 + 4), (14, 12, 10), 2)

# Curved glass CRT screen
screen = np.full((bh, bw, 3), 14, dtype=np.uint8)
# Subtle horizontal brushed scanlines on the glass
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
cv2.rectangle(frame, (bx1, by1), (bx2, by2), (38, 38, 46), 2)

# Crisp PIL typography
pil_img = Image.fromarray(frame)
draw = ImageDraw.Draw(pil_img)

font_bn = ImageFont.truetype(BN_FONT, 52)
font_en = ImageFont.truetype(EN_FONT, 25)

line1 = "“ওটা আপনার মা নয়..."
line2 = "ওটা আপনার শরীরের মাপ নিচ্ছে...”"
line_en = "[ That is not your mother... It is taking the measurement of your body... ]"

# Crisp text with soft shadow for depth
y_l1 = by1 + int(bh * 0.28)
y_l2 = by1 + int(bh * 0.54)
y_en = by1 + int(bh * 0.82)

for dx, dy in [(0, 2), (1, 1), (-1, 1), (0, -1)]:
    draw.text((w // 2 + dx, y_l1 + dy), line1, font=font_bn, fill=(4, 4, 6), anchor="mm")
    draw.text((w // 2 + dx, y_l2 + dy), line2, font=font_bn, fill=(4, 4, 6), anchor="mm")
    draw.text((w // 2 + dx, y_en + dy), line_en, font=font_en, fill=(4, 4, 6), anchor="mm")

draw.text((w // 2, y_l1), line1, font=font_bn, fill=(255, 255, 255), anchor="mm")
draw.text((w // 2, y_l2), line2, font=font_bn, fill=(255, 255, 255), anchor="mm")
draw.text((w // 2, y_en), line_en, font=font_en, fill=(235, 235, 240), anchor="mm")

out = np.array(pil_img)
out_path = os.path.join(ROOT, "output", "test_broadcast_card.png")
cv2.imwrite(out_path, cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
print("Saved to:", out_path)
