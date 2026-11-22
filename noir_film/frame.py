"""
Master frame compositor for PROJECT NOIR (Bengali / Indian Analog Horror).
Integrates rural Bengal Courage homestead, Doordarshan CRT broadcasts,
Kafkaesque metamorphosis of Bimal Babu, and Lovecraftian celestial eye.
"""
import os
import math
import cv2
import numpy as np

from . import shaders
from . import actors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_plates(width=1280, height=720):
    """Loads and resizes Bengali analog horror background plates."""
    plates_dir = os.path.join(ROOT, "plates")
    plates = {}

    names = {
        "homestead": "bengal_courage_homestead.jpg",
        "bedroom": "bengal_bedroom.jpg",
        "dd_crt": "doordarshan_crt.jpg",
        "cosmic_eye": "bengal_cosmic_eye.jpg",
    }

    for key, fname in names.items():
        fpath = os.path.join(plates_dir, fname)
        if os.path.exists(fpath):
            img = cv2.imread(fpath)
            if img is not None:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                plates[key] = cv2.resize(img_rgb, (width, height), interpolation=cv2.INTER_AREA).astype(np.uint8)
            else:
                plates[key] = np.zeros((height, width, 3), np.uint8)
        else:
            plates[key] = np.zeros((height, width, 3), np.uint8)

    return plates


def render_noir_frame(plates, t, width=1280, height=720, sub_bass=0.1):
    """
    Renders a single frame of NOIR at timestamp t.
    Rich Indian / Bengali Analog Horror aesthetics.
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # 1. SCENE 1: Doordarshan Emergency Broadcast Alert (t = 0s to 12s)
    if t < 12.0:
        actors.draw_doordarshan_alert(frame, t)
        if t > 9.5:
            # Harsh static snow burst before cut
            fade = (t - 9.5) / 2.5
            frame = shaders.apply_white_noise(frame, amount=0.45 * fade)

    # 2. SCENE 2: Courage in Rural Bengal — Isolated House & Banana Trees (t = 12s to 30s)
    elif 12.0 <= t < 30.0:
        scene_t = t - 12.0
        base = plates["homestead"].copy()
        # Slow, eerie zoom-in
        zoom = 1.0 + scene_t * 0.007
        M = cv2.getRotationMatrix2D((width * 0.5, height * 0.5), 0, zoom)
        base = cv2.warpAffine(base, M, (width, height))
        frame[:] = base

        # Swaying silhouetted banana trees (kola gachh) and handpump (tubewell)
        actors.draw_bengal_banana_trees(frame, t, cx=int(width * 0.82), cy=int(height * 0.72), scale=1.0)
        actors.draw_bengal_banana_trees(frame, t + 1.2, cx=int(width * 0.18), cy=int(height * 0.76), scale=0.85)

    # 3. SCENE 3: Kafka's Metamorphosis in Bengal — Bimal Babu's Room (t = 30s to 55s)
    elif 30.0 <= t < 55.0:
        scene_t = t - 30.0
        frame[:] = plates["bedroom"].copy()
        # Metamorphosis stage
        stage = min(1.0, scene_t / 18.0)
        actors.draw_bimal_kafka_bengal(frame, t, cx=int(width * 0.42), cy=int(height * 0.68), stage=stage)

    # 4. SCENE 4: The Black Tomcat on Bamboo Fence by Banana Grove (t = 55s to 75s)
    elif 55.0 <= t < 75.0:
        scene_t = t - 55.0
        frame[:] = plates["homestead"].copy()
        # Background banana trees behind the fence
        actors.draw_bengal_banana_trees(frame, t, cx=int(width * 0.80), cy=int(height * 0.74), scale=0.9)
        # Black Tomcat neck stretches into the sky
        stretch = min(1.0, scene_t / 14.0)
        actors.draw_bengal_hulo_cat(frame, t, cx=int(width * 0.55), cy=int(height * 0.64), stretch=stretch)

    # 5. SCENE 5: The Lovecraftian Cosmic Third-Eye over Bengal Palms (t = 75s to 90s)
    else:
        scene_t = t - 75.0
        frame[:] = plates["cosmic_eye"].copy()
        # Silhouetted banana leaves framing the bottom
        actors.draw_bengal_banana_trees(frame, t, cx=int(width * 0.12), cy=height, scale=1.1)
        actors.draw_bengal_banana_trees(frame, t, cx=int(width * 0.92), cy=height, scale=1.1)
        # Cosmic television static interference
        noise_amt = 0.12 + 0.60 * (scene_t / 15.0)
        frame = shaders.apply_white_noise(frame, amount=noise_amt, breathing=math.sin(t * 4.0))

    # ─────────────────────────────────────────────────────────────
    # GLOBAL ANALOG HORROR SHADER POST-PROCESSING
    # ─────────────────────────────────────────────────────────────
    # 1. VHS tracking jitter & bottom 24px head switching noise
    frame = shaders.apply_vhs_tracking(frame, t, sub_bass=sub_bass)

    # 2. Doordarshan DD-1 On-Screen Display (OSD)
    osd_msg = "DD-1 BANGLA"
    shaders.draw_vcr_osd(frame, t, channel="VHF 04", message=osd_msg)

    # 3. Vintage Indian curved CRT glass & cathode scanlines
    frame = shaders.apply_crt(frame, curvature=0.06, scanline_intensity=0.22)

    return np.clip(frame, 0, 255).astype(np.uint8)
