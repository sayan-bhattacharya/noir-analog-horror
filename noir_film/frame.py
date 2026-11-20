"""
Frame compositor for PROJECT NOIR.
Composites background plates, procedural surreal actors, and analog horror CRT shaders.
"""
import os
import math
import cv2
import numpy as np

from . import shaders
from . import actors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_plates(width=1280, height=720):
    """Loads and resizes background plates to 720p (or 1080p)."""
    plates_dir = os.path.join(ROOT, "plates")
    plates = {}

    names = {
        "farmhouse": "nowhere_farmhouse.jpg",
        "tv_static": "crt_television_static.jpg",
        "bedroom": "kafka_bedroom.jpg",
        "optic_moon": "optic_cosmic_moon.jpg",
    }

    for key, fname in names.items():
        fpath = os.path.join(plates_dir, fname)
        if os.path.exists(fpath):
            img = cv2.imread(fpath)
            if img is not None:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                plates[key] = cv2.resize(img_rgb, (width, height), interpolation=cv2.INTER_AREA).astype(np.float32)
            else:
                plates[key] = np.zeros((height, width, 3), np.float32)
        else:
            plates[key] = np.zeros((height, width, 3), np.float32)

    return plates


def render_noir_frame(plates, t, width=1280, height=720, sub_bass=0.1):
    """
    Renders a single frame of NOIR at timestamp t (seconds).
    720p default resolution for lightning-fast preview rendering.
    """
    frame = np.zeros((height, width, 3), dtype=np.float32)

    # 1. SCENE 1: EAS Emergency Action Notification (t = 0s to 12s)
    if t < 12.0:
        actors.draw_eas_card(frame, t)
        if t > 9.5:
            # Static snow intrusion before cut
            fade = (t - 9.5) / 2.5
            frame = shaders.apply_white_noise(frame, amount=0.45 * fade)

    # 2. SCENE 2: The Nowhere Farmhouse & Windmill (t = 12s to 30s)
    elif 12.0 <= t < 30.0:
        scene_t = t - 12.0
        base = plates["farmhouse"].copy()
        # Slow pan / zoom
        zoom = 1.0 + scene_t * 0.008
        M = cv2.getRotationMatrix2D((width * 0.5, height * 0.5), 0, zoom)
        base = cv2.warpAffine(base, M, (width, height))
        frame[:] = base
        # Procedural windmill
        actors.draw_windmill(frame, t, cx=int(width * 0.76), cy=int(height * 0.62), scale=0.85)

    # 3. SCENE 3: Kafka's Metamorphosis Bedroom (t = 30s to 55s)
    elif 30.0 <= t < 55.0:
        scene_t = t - 30.0
        frame[:] = plates["bedroom"].copy()
        # Stage 0 to 1 transformation
        stage = min(1.0, scene_t / 18.0)
        actors.draw_gregor_kafka(frame, t, cx=int(width * 0.38), cy=int(height * 0.72), stage=stage)
        # Procedural crawling spiders on floor
        if stage > 0.4:
            actors.draw_spider_swarm(frame, t, count=int(stage * 24))

    # 4. SCENE 4: The Surreal Nowhere Cat on Fence (t = 55s to 75s)
    elif 55.0 <= t < 75.0:
        scene_t = t - 55.0
        frame[:] = plates["farmhouse"].copy()
        # Cat neck stretches up towards the heavens
        stretch = min(1.0, scene_t / 14.0)
        actors.draw_surreal_cat(frame, t, cx=int(width * 0.62), cy=int(height * 0.68), stretch=stretch)

    # 5. SCENE 5: The Optic Cosmic Moon & Final TV Static (t = 75s to 90s)
    else:
        scene_t = t - 75.0
        frame[:] = plates["optic_moon"].copy()
        # Subliminal TV static snow surge
        noise_amt = 0.12 + 0.55 * (scene_t / 15.0)
        frame = shaders.apply_white_noise(frame, amount=noise_amt, breathing=math.sin(t * 4.0))

    # ─────────────────────────────────────────────────────────────
    # GLOBAL ANALOG HORROR SHADER POST-PROCESSING
    # ─────────────────────────────────────────────────────────────
    # 1. VHS tracking jitter & bottom head switching
    frame = shaders.apply_vhs_tracking(frame, t, sub_bass=sub_bass)

    # 2. VCR On-Screen Display (OSD)
    osd_msg = "ALERT" if t < 12.0 else "PLAY"
    shaders.draw_vcr_osd(frame, t, channel="CH 03", message=osd_msg)

    # 3. Vintage CRT Curved Glass & Scanline Raster
    frame = shaders.apply_crt(frame, curvature=0.06, scanline_intensity=0.20)

    return np.clip(frame, 0, 255).astype(np.uint8)
