"""
Master frame compositor for PROJECT NOIR (Bengali / Indian Analog Horror).
Integrates:
- 1994 Doordarshan Calcutta Emergency Interruption in authentic Bengali.
- Nowhere rural farmhouse with subtle, uncluttered Bengali banana fronds.
- Regular bedroom draped with an authentic suspended Moshari (mosquito net).
- Twilight Zone spinning optical illusion spiral abyss with the tumbling falling man.
- The Black Tomcat on rustic bamboo fence & the cosmic celestial eye.
"""
import os
import math
import cv2
import numpy as np

from . import shaders
from . import actors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_plates(width=1280, height=720):
    """Loads and resizes background plates with fallback options."""
    plates_dir = os.path.join(ROOT, "plates")
    plates = {}

    file_candidates = {
        "homestead": ["nowhere_farmhouse.jpg", "bengal_courage_homestead.jpg"],
        "bedroom": ["kafka_bedroom.jpg", "bengal_bedroom.jpg"],
        "cosmic_eye": ["optic_cosmic_moon.jpg", "bengal_cosmic_eye.jpg"],
        "dd_crt": ["doordarshan_crt.jpg", "crt_television_static.jpg"]
    }

    for key, fnames in file_candidates.items():
        found = False
        for fname in fnames:
            fpath = os.path.join(plates_dir, fname)
            if os.path.exists(fpath):
                img = cv2.imread(fpath)
                if img is not None:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    plates[key] = cv2.resize(img_rgb, (width, height), interpolation=cv2.INTER_AREA).astype(np.uint8)
                    found = True
                    break
        if not found:
            plates[key] = np.zeros((height, width, 3), np.uint8)

    return plates


def render_noir_frame(plates, t, width=1280, height=720, sub_bass=0.1):
    """
    Renders a single frame of NOIR at timestamp t.
    Seamless progression across 6 narrative analog horror movements (0s to 90s).
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # 1. SCENE 1: Doordarshan Kendra Calcutta 1994 Emergency Alert (t = 0s to 14s)
    if t < 14.0:
        actors.draw_doordarshan_alert(frame, t)
        if t > 11.5:
            # Cathode static burst transition
            fade = (t - 11.5) / 2.5
            frame = shaders.apply_white_noise(frame, amount=0.55 * fade)

    # 2. SCENE 2: The Nowhere Homestead — Subtly Grounded in Bengal Night (t = 14s to 30s)
    elif 14.0 <= t < 30.0:
        scene_t = t - 14.0
        base = plates["homestead"].copy()
        # Slow atmospheric dread push-in
        zoom = 1.0 + scene_t * 0.005
        M = cv2.getRotationMatrix2D((width * 0.5, height * 0.5), 0, zoom)
        base = cv2.warpAffine(base, M, (width, height))
        frame[:] = base

        # Subtle, uncluttered touch: single delicate banana frond in the peripheral darkness
        actors.draw_subtle_banana_frond(frame, t, cx=int(width * 0.94), cy=height, scale=0.85)

    # 3. SCENE 3: The Regular Bedroom Draped in Moshari (Mosquito Net) (t = 30s to 48s)
    elif 30.0 <= t < 48.0:
        scene_t = t - 30.0
        frame[:] = plates["bedroom"].copy()
        # Slow eerie breathing pan
        shift_x = int(math.sin(scene_t * 0.3) * 6)
        if shift_x != 0:
            frame[:] = np.roll(frame, shift_x, axis=1)

        # Authentic suspended Moshari canopy over the bed
        actors.draw_moshari_net(frame, t, bed_rect=(int(width * 0.22), int(height * 0.32),
                                                    int(width * 0.58), int(height * 0.58)))

        # Teletext OSD whisper at bottom
        if scene_t > 8.0:
            glitch_alpha = min(1.0, (scene_t - 8.0) / 4.0)
            if int(t * 4) % 2 == 0:
                actors.draw_bengali_text(frame, "মশারি অপসারিত করিবেন না", (width // 2, int(height * 0.92)),
                                         font_size=20, fill_color=(240, 220, 180), anchor="mm")

    # 4. SCENE 4: The Twilight Zone Optical Illusion Spiral Abyss (t = 48s to 70s)
    elif 48.0 <= t < 70.0:
        scene_t = t - 48.0
        actors.draw_twilight_zone_abyss(frame, scene_t, sub_bass=sub_bass)

        # Sub-bass tracking ripple in the abyss
        if sub_bass > 0.3:
            frame = shaders.apply_vhs_tracking(frame, t, tear_intensity=0.8, sub_bass=sub_bass)

    # 5. SCENE 5: The Black Tomcat on Bamboo Fence & Cosmic Eye (t = 70s to 85s)
    elif 70.0 <= t < 85.0:
        scene_t = t - 70.0
        # Blend cosmic eye sky with fence
        frame[:] = plates["cosmic_eye"].copy()

        # Silhouette of rustic bamboo fence & stretching tomcat
        stretch = min(1.0, scene_t / 11.0)
        actors.draw_bengal_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.65), stretch=stretch)
        # Peripheral subtle frond
        actors.draw_subtle_banana_frond(frame, t, cx=int(width * 0.08), cy=height, scale=0.75)

    # 6. SCENE 6: Broadcast Severance & Final Decay (t = 85s to 90s)
    else:
        scene_t = t - 85.0
        frame[:, :] = [18, 15, 48]
        # Burning terminal message
        actors.draw_bengali_text(frame, "সম্প্রচার সমাপ্ত হইবে না", (width // 2, height // 2 - 20),
                                 font_size=32, fill_color=(245, 60, 60), anchor="mm")
        actors.draw_bengali_text(frame, "দূরদর্শন কেন্দ্র কলকাতা  |  ভিএইচএফ ০৪", (width // 2, height // 2 + 35),
                                 font_size=20, fill_color=(200, 200, 200), anchor="mm")
        # Heavy static collapse
        fade = scene_t / 5.0
        frame = shaders.apply_white_noise(frame, amount=0.25 + 0.65 * fade)

    # Unified Master Analog CRT & VHS Master Processing
    frame = shaders.apply_crt(frame, curvature=0.06, scanline_intensity=0.20)
    frame = shaders.apply_vhs_tracking(frame, t, tear_intensity=1.0, sub_bass=sub_bass)
    shaders.draw_vcr_osd(frame, t, channel="DD 04", message="PLAY")

    return frame
