import sys
sys.path.insert(0, "e:/betweenthenotes/noir_film_project")
import cv2
from noir_film.timeline import NoirTimeline

tl = NoirTimeline()

f6 = tl.render_frame_at(39.0, 1920, 1080)
cv2.imwrite("e:/betweenthenotes/noir_film_project/output/text_audit/shot_06_broadcast_card_1.png", cv2.cvtColor(f6, cv2.COLOR_RGB2BGR))

f7 = tl.render_frame_at(43.0, 1920, 1080)
cv2.imwrite("e:/betweenthenotes/noir_film_project/output/text_audit/shot_07_broadcast_card_2.png", cv2.cvtColor(f7, cv2.COLOR_RGB2BGR))

crop7 = f7[int(f7.shape[0]*0.22):int(f7.shape[0]*0.80), int(f7.shape[1]*0.15):int(f7.shape[1]*0.85)]
cv2.imwrite("C:/Users/sayan/.gemini/antigravity/brain/b3d17fa9-62a2-4701-acdb-0633a94e4498/crop_shot_07_harfbuzz.png", cv2.cvtColor(crop7, cv2.COLOR_RGB2BGR))

print("Rendered with HarfBuzz shaper successfully!")
