import cv2
import numpy as np
from noir_film.timeline import NoirTimeline
from noir_film.utils.config_loader import load_global_config

cfg = load_global_config()
timeline = NoirTimeline(cfg)

w, h = 1280, 720

# 1. Test Shot 1 (Station ID & Between the Notes Logo)
f1 = timeline.render_frame_at(2.5, width=w, height=h)
cv2.imwrite(r"C:\Users\sayan\.gemini\antigravity\brain\b3d17fa9-62a2-4701-acdb-0633a94e4498\test_shot01_btn_station_id.png", f1)

# 2. Test Shot 2 (News Broadcast with Between the Notes Bug & Ticker)
f2 = timeline.render_frame_at(8.0, width=w, height=h)
cv2.imwrite(r"C:\Users\sayan\.gemini\antigravity\brain\b3d17fa9-62a2-4701-acdb-0633a94e4498\test_shot02_btn_news_channel.png", f2)

# 3. Test Shot 3 (Corrupted News Broadcast)
f3 = timeline.render_frame_at(18.0, width=w, height=h)
cv2.imwrite(r"C:\Users\sayan\.gemini\antigravity\brain\b3d17fa9-62a2-4701-acdb-0633a94e4498\test_shot03_btn_corrupted_news.png", f3)

# 4. Test Shot 24 (Photorealistic Video Cloud Time-Lapse + Shadow Cat)
f24 = timeline.render_frame_at(156.0, width=w, height=h)
cv2.imwrite(r"C:\Users\sayan\.gemini\antigravity\brain\b3d17fa9-62a2-4701-acdb-0633a94e4498\test_shot24_photorealistic_cloud_timelapse.png", f24)

print("All 4 test frames rendered successfully!")
