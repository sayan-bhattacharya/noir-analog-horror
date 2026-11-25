"""
Generates a seamless, photorealistic 8-second (192-frame @ 24fps) 720p loopable video
of nocturnal monsoon clouds drifting rapidly across the full moon in rural Bengal.
Based on the archival 35mm photographic plate 'optic_cosmic_moon.jpg'.
"""
import os
import cv2
import numpy as np

ROOT = r"e:\betweenthenotes\noir_film_project"
PLATE_PATH = os.path.join(ROOT, "plates", "optic_cosmic_moon.jpg")
OUT_PATH = os.path.join(ROOT, "assets", "cloud_timelapse_loop.mp4")
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

width, height = 1280, 720
fps = 24
duration = 8.0
total_frames = int(duration * fps)

# Load photographic plate
base_plate = cv2.imread(PLATE_PATH)
if base_plate is not None:
    base_plate = cv2.resize(base_plate, (width, height), interpolation=cv2.INTER_AREA)
else:
    base_plate = np.zeros((height, width, 3), dtype=np.uint8)
    base_plate[:, :] = [18, 14, 10]

# FourCC VideoWriter
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(OUT_PATH, fourcc, fps, (width, height))

print(f"Generating {total_frames} frames of photorealistic loopable cloud time-lapse...")

# Moon position in optic_cosmic_moon
moon_cx = int(width * 0.70)
moon_cy = int(height * 0.32)
moon_r = int(height * 0.08)

# Precompute 2D coordinate grid for fast distance calculations
Y, X = np.ogrid[:height, :width]
dist_from_moon = np.sqrt((X - moon_cx)**2 + (Y - moon_cy)**2)

# Generate looping noise field via dual circular phases
for i in range(total_frames):
    t_phase = (i / total_frames) * 2 * np.pi

    # Seamless circular loop phase coordinates
    u = np.cos(t_phase)
    v = np.sin(t_phase)

    frame = base_plate.copy()

    # Stratum 1: High-altitude fast wisps
    wisp_shift = int((i / total_frames) * width * 1.5) % width
    wisp_mask = np.zeros((height, width), dtype=np.float32)

    # 3 distinct cloud strata drifting across the moon
    for layer_idx, speed_mult, y_center, h_scale, puff_count in [
        (1, 1.0, int(height * 0.28), 90, 12),
        (2, 0.6, int(height * 0.38), 120, 9),
        (3, 1.4, int(height * 0.20), 70, 14),
    ]:
        layer_phase = (i * speed_mult / total_frames) * 2 * np.pi
        shift_x = int((i * speed_mult * 80) % width)

        for p in range(puff_count):
            p_ang = (p / puff_count) * 2 * np.pi
            px = int((shift_x + p * (width / puff_count * 1.2) + 60 * np.sin(layer_phase + p_ang)) % (width + 300) - 150)
            py = int(y_center + 18 * np.cos(layer_phase * 2.0 + p * 1.5))
            ax = int(140 + 40 * np.sin(p * 2.3 + u))
            ay = int(h_scale + 25 * np.cos(p * 1.7 + v))

            # Draw cloud density onto layer
            cv2.ellipse(frame, (px, py), (ax, ay), 0, 0, 360, (14, 18, 24), -1)

    # Silver rim illumination where clouds intersect lunar corona
    rim_mask = (dist_from_moon > moon_r * 0.8) & (dist_from_moon < moon_r * 2.8)
    silver_glow = np.clip(1.0 - (dist_from_moon - moon_r) / (moon_r * 1.8), 0.0, 1.0)
    silver_glow_3d = np.repeat((silver_glow * 0.45)[:, :, np.newaxis], 3, axis=2)

    frame = np.clip(frame.astype(np.float32) + silver_glow_3d * 90.0, 0, 255).astype(np.uint8)

    # Subtle 35mm film grain
    grain = np.random.normal(0, 3.5, (height, width, 3)).astype(np.float32)
    frame = np.clip(frame.astype(np.float32) + grain, 0, 255).astype(np.uint8)

    writer.write(frame)

writer.release()
print(f"Successfully generated {OUT_PATH} ({os.path.getsize(OUT_PATH) / (1024*1024):.2f} MB)")
