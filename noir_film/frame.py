"""
Master frame compositor for PROJECT NOIR (Bengali / Indian Analog Horror).
Rhythmic editorial montage with frequent cuts every 1.5s - 3.5s:
- 1994 Doordarshan Kendra Calcutta (দূরদর্শন কেন্দ্র কলকাতা) emergency alerts.
- Photorealistic AI plates: vintage bedroom draped in sheer mosquito net (moshari),
  macro rusty door latch, mist-shrouded bamboo grove, dangling telephone.
- Silent film / Alex Kister style dialogue intertitles in Bengali.
- The Twilight Zone optical illusion spiral abyss with the tumbling falling man.
- The rural Black Tomcat on rustic bamboo fence and the celestial third-eye.
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
        "moshari_bedroom": ["moshari_bedroom_realistic.jpg", "bengal_bedroom.jpg", "kafka_bedroom.jpg"],
        "door_latch": ["rustic_door_latch.jpg"],
        "bamboo_mist": ["bamboo_grove_mist.jpg"],
        "telephone": ["telephone_off_hook.jpg"],
        "homestead": ["nowhere_farmhouse.jpg", "bengal_courage_homestead.jpg"],
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


def zoom_pan(plate, local_t, duration, zoom_start=1.0, zoom_end=1.06, pan_x=0, pan_y=0):
    """Applies smooth cinematic camera creep/zoom to a static plate."""
    h, w = plate.shape[:2]
    progress = min(1.0, max(0.0, local_t / max(0.01, duration)))
    zoom = zoom_start + (zoom_end - zoom_start) * progress
    cx = w * 0.5 + pan_x * progress
    cy = h * 0.5 + pan_y * progress
    M = cv2.getRotationMatrix2D((cx, cy), 0, zoom)
    return cv2.warpAffine(plate, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def render_noir_frame(plates, t, width=1280, height=720, sub_bass=0.1):
    """
    Renders a single frame of NOIR at timestamp t.
    Fast-paced editorial montage with cuts every 1.5s to 3.5s.
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # SHOT 1 (0.0s - 3.2s): Doordarshan Calcutta Emergency Interruption Header
    if t < 3.2:
        actors.draw_doordarshan_alert(frame, t)

    # SHOT 2 (3.2s - 5.5s): Macro Zoom into Corrupted Doordarshan Eye
    elif 3.2 <= t < 5.5:
        st = t - 3.2
        frame[:, :] = [18, 15, 48]
        # Pulsating macro eye
        actors.draw_doordarshan_logo(frame, width // 2, height // 2, radius=int(75 + st * 15), t=t)
        actors.draw_bengali_text(frame, "ভারত দর্পণ কেন্দ্র কলকাতা", (width // 2, int(height * 0.78)),
                                 font_size=26, fill_color=(245, 205, 55), anchor="mm")
        if st > 1.8:
            frame = shaders.apply_white_noise(frame, amount=0.45 * (st - 1.8))

    # SHOT 3 (5.5s - 8.2s): Doordarshan Directive 1 Bulletin
    elif 5.5 <= t < 8.2:
        actors.draw_doordarshan_alert(frame, t)

    # SHOT 4 (8.2s - 10.5s): B-Roll Cutaway 1: Macro Rusty Door Latch (Chhitkini)
    elif 8.2 <= t < 10.5:
        st = t - 8.2
        # Camera slowly creeping into the bolted latch
        frame[:] = zoom_pan(plates["door_latch"], st, 2.3, 1.0, 1.08)
        # Subtle rattle jitter on latch
        jitter = int(math.sin(t * 28.0) * (2.5 if sub_bass > 0.2 else 0.5))
        if jitter != 0:
            frame[:] = np.roll(frame, jitter, axis=0)

    # SHOT 5 (10.5s - 13.0s): Silent Film Intertitle 1
    elif 10.5 <= t < 13.0:
        st = t - 10.5
        actors.draw_silent_film_intertitle(frame,
                                          "“কে?... দরজায় কে ধাক্কা দিচ্ছে?”",
                                          "[Who is that?... Who is banging on the door?]", t=st)

    # SHOT 6 (13.0s - 15.5s): B-Roll Cutaway 2: Misty Bamboo Grove (Banshjhar)
    elif 13.0 <= t < 15.5:
        st = t - 13.0
        frame[:] = zoom_pan(plates["bamboo_mist"], st, 2.5, 1.0, 1.07, pan_x=-15)

    # SHOT 7 (15.5s - 18.0s): Silent Film Intertitle 2
    elif 15.5 <= t < 18.0:
        st = t - 15.5
        actors.draw_silent_film_intertitle(frame,
                                          "“দরজা খুলবেন না। ওটা আপনার মা নয়।”",
                                          "[Do not open the door. That is not your mother.]", t=st)

    # SHOT 8 (18.0s - 21.0s): Wide Establishing: Nowhere Rural Farmhouse
    elif 18.0 <= t < 21.0:
        st = t - 18.0
        frame[:] = zoom_pan(plates["homestead"], st, 3.0, 1.0, 1.05)
        # Peripheral subtle banana frond
        actors.draw_subtle_banana_frond(frame, t, cx=int(width * 0.94), cy=height, scale=0.85)

    # SHOT 9 (21.0s - 23.5s): B-Roll Cutaway 3: Rotary Telephone Off the Hook
    elif 21.0 <= t < 23.5:
        st = t - 21.0
        frame[:] = zoom_pan(plates["telephone"], st, 2.5, 1.0, 1.06, pan_y=10)

    # SHOT 10 (23.5s - 26.0s): Silent Film Intertitle 3
    elif 23.5 <= t < 26.0:
        st = t - 23.5
        actors.draw_silent_film_intertitle(frame,
                                          "“লাইন কেটে গেছে। ফোন তোলার মতো কেউ বেঁচে নেই।”",
                                          "[The line is dead. No one is alive to pick up.]", t=st)

    # SHOT 11 (26.0s - 29.0s): Photorealistic Bedroom Draped in Real Mosquito Net (Moshari)
    elif 26.0 <= t < 29.0:
        st = t - 26.0
        frame[:] = zoom_pan(plates["moshari_bedroom"], st, 3.0, 1.0, 1.06)

    # SHOT 12 (29.0s - 31.5s): Silent Film Intertitle 4
    elif 29.0 <= t < 31.5:
        st = t - 29.0
        actors.draw_silent_film_intertitle(frame,
                                          "“আমি মেঝের ওপর থেকে উঠতে পারছি না...”",
                                          "[I cannot get up from the floor...]", t=st)

    # SHOT 13 (31.5s - 36.5s): THE TWILIGHT ZONE OPTICAL SPIRAL ABYSS (First Descent)
    elif 31.5 <= t < 36.5:
        st = t - 31.5
        actors.draw_twilight_zone_abyss(frame, st, sub_bass=sub_bass)
        if sub_bass > 0.3:
            frame = shaders.apply_vhs_tracking(frame, t, tear_intensity=0.8, sub_bass=sub_bass)

    # SHOT 14 (36.5s - 38.5s): Subliminal Flash Cuts (Door Latch -> Telephone -> Bed)
    elif 36.5 <= t < 38.5:
        st = t - 36.5
        phase = int(st * 4) % 3
        if phase == 0:
            frame[:] = plates["door_latch"]
        elif phase == 1:
            frame[:] = plates["telephone"]
        else:
            frame[:] = plates["moshari_bedroom"]
        frame = shaders.apply_white_noise(frame, amount=0.35)

    # SHOT 15 (38.5s - 41.0s): Silent Film Intertitle 5
    elif 38.5 <= t < 41.0:
        st = t - 38.5
        actors.draw_silent_film_intertitle(frame,
                                          "“নিশিডাক দ্বিতীয়বার ডেকে উঠেছে।”",
                                          "[The Nishidak has called for the second time.]", t=st)

    # SHOT 16 (41.0s - 44.0s): Rural Bamboo Fence & The Black Tomcat (Eyes Glowing)
    elif 41.0 <= t < 44.0:
        st = t - 41.0
        frame[:] = plates["homestead"].copy()
        actors.draw_bengal_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.65), stretch=0.0)

    # SHOT 17 (44.0s - 47.0s): The Tomcat Neck Stretching into the Night Sky
    elif 44.0 <= t < 47.0:
        st = t - 44.0
        frame[:] = plates["homestead"].copy()
        stretch = min(1.0, st / 2.8)
        actors.draw_bengal_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.65), stretch=stretch)

    # SHOT 18 (47.0s - 49.5s): Silent Film Intertitle 6
    elif 47.0 <= t < 49.5:
        st = t - 49.5
        actors.draw_silent_film_intertitle(frame,
                                          "“ওর চোখ আকাশের লাল চোখের দিকে স্থির হয়ে আছে।”",
                                          "[Its eyes are locked onto the red Eye in the sky.]", t=st)

    # SHOT 19 (49.5s - 54.0s): Colossal Cosmic Third-Eye Over Bengal Palms
    elif 49.5 <= t < 54.0:
        st = t - 49.5
        frame[:] = zoom_pan(plates["cosmic_eye"], st, 4.5, 1.0, 1.08)
        actors.draw_subtle_banana_frond(frame, t, cx=int(width * 0.08), cy=height, scale=0.8)

    # SHOT 20 (54.0s - 63.0s): THE TWILIGHT ZONE INFINITE ABYSS (Second Climactic Descent)
    elif 54.0 <= t < 63.0:
        st = t - 54.0
        actors.draw_twilight_zone_abyss(frame, st * 1.25, sub_bass=max(0.4, sub_bass))
        frame = shaders.apply_vhs_tracking(frame, t, tear_intensity=1.2, sub_bass=sub_bass)

    # SHOT 21 (63.0s - 66.0s): Silent Film Intertitle 7
    elif 63.0 <= t < 66.0:
        st = t - 63.0
        actors.draw_silent_film_intertitle(frame,
                                          "“চোখটা আপনাকে অনেক আগেই দেখে ফেলেছে।”",
                                          "[The Eye saw you long ago.]", t=st)

    # SHOT 22 (66.0s - 74.0s): Doordarshan CRT Terminal Decree (Unending Broadcast)
    elif 66.0 <= t < 74.0:
        st = t - 66.0
        frame[:, :] = [18, 15, 48]
        actors.draw_doordarshan_logo(frame, width // 2, 110, radius=42, t=t)
        actors.draw_bengali_text(frame, "ভারত দর্পণ কেন্দ্র কলকাতা", (width // 2, 170),
                                 font_size=22, fill_color=(245, 205, 55), anchor="mm")
        actors.draw_bengali_text(frame, "সম্প্রচার বন্ধ হবে না", (width // 2, height // 2 + 10),
                                 font_size=34, fill_color=(245, 60, 60), anchor="mm")
        actors.draw_bengali_text(frame, "এই জরুরি সম্প্রচার একটানা চলবে। দরজা খুলবেন না।",
                                 (width // 2, height // 2 + 65), font_size=20, fill_color=(220, 220, 220), anchor="mm")

    # SHOT 23 (74.0s - 77.5s): Rapid Flash-Cut Cadence Before Severance
    elif 74.0 <= t < 77.5:
        st = t - 74.0
        flash_step = int(st * 6) % 4
        if flash_step == 0:
            actors.draw_twilight_zone_abyss(frame, st * 2.0, sub_bass=0.6)
        elif flash_step == 1:
            frame[:] = plates["moshari_bedroom"]
        elif flash_step == 2:
            frame[:] = plates["door_latch"]
        else:
            frame[:] = plates["cosmic_eye"]
        frame = shaders.apply_white_noise(frame, amount=0.50)

    # SHOT 24 (77.5s - 90.0s): Final Cathode Severance & Decaying Analog Static
    else:
        st = t - 77.5
        frame[:, :] = [12, 10, 16]
        actors.draw_bengali_text(frame, "সম্প্রচার সমাপ্ত হইবে না", (width // 2, height // 2),
                                 font_size=30, fill_color=(180, 50, 50), anchor="mm")
        fade = min(1.0, st / 8.0)
        frame = shaders.apply_white_noise(frame, amount=0.30 + 0.65 * fade)

    # Unified Master Analog CRT & VHS Master Processing
    frame = shaders.apply_crt(frame, curvature=0.06, scanline_intensity=0.20)
    frame = shaders.apply_vhs_tracking(frame, t, tear_intensity=1.0, sub_bass=sub_bass)
    shaders.draw_vcr_osd(frame, t, channel="DD 04", message="PLAY")

    return frame
