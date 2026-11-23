"""
Master Timeline Compositor for Project NOIR / Nishidak.
Coordinates the full 5-Minute (300 Seconds, 7,200 frames @ 24 fps) cinematic analog horror film.

Calibrated to the Silent Reading Timing Table & User Creative Direction:
- Broadcast Readability Cards matching 'Improve Broadcast Readability.png' (large, bold, zero jitter/shimmer).
- Automatic Open-Source AI Watermark Removal on all plates during load.
- 1:07 Mark: Left-hand cast-iron tube-well dripping black fluid frame-by-frame + cloud time-lapse across the moon.
- 1:49 Mark: Tightly enclosed, closed mosquito net (spooky sheer white fabric cage).
- 2:02 Mark: Tiny crawling spider swells suddenly into a colossal GIANT spanning the size of the net at the emergency beep.
- 2:05 Mark: "ত্রিনেত্র জেগে উঠছে..." transitions into a blank screen with huge font, followed by slow gradual development of the eye.
- 2:20 - 2:40 Mark: The Black Cat replaced with the uncanny Shadowy Hyper-Object Figure.
- 2:33 Mark: Full-screen modular Night Sky Cloud Time-Lapse.
- 4:47 Mark: Minimalist Between the Notes End Credits.
- Tuned noise/haze for grounded cinematic realism.
"""
import os
import math
import cv2
import numpy as np

from .utils.config_loader import load_global_config
from .utils.video_io import create_placeholder_plate
from . import crt
from . import vhs
from . import noise
from . import distortion
from . import cosmic
from . import text_overlay
from .actors import doordarshan_alert
from .actors import banana_trees
from .actors import bimal_metamorphosis
from .actors import hulo_cat
from .actors import trinetra_eye
from .actors import news_broadcast
from .actors import sector_map
from .actors import civil_danger
from .actors import tubewell_scene
from .actors import cloud_timelapse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scrub_ai_watermark(img: np.ndarray) -> np.ndarray:
    """
    Open-Source AI Watermark Scrubber:
    Removes Gemini / Imagen / Flow corner watermarks without altering composition.
    Applies Telea inpainting over the bottom-right corner watermark zone
    plus a subtle safe margin crop to guarantee 100% watermark elimination.
    """
    if img is None:
        return img
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    cx_mark = w - int(w * 0.068)
    cy_mark = h - int(h * 0.108)
    cv2.circle(mask, (cx_mark, cy_mark), int(min(w, h) * 0.058), 255, -1)
    cv2.circle(mask, (int(w * 0.068), cy_mark), int(min(w, h) * 0.040), 255, -1)

    scrubbed = cv2.inpaint(img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

    crop_y = int(h * 0.015)
    crop_x = int(w * 0.015)
    cropped = scrubbed[crop_y:h - crop_y, crop_x:w - crop_x]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)


def zoom_pan(plate, local_t, duration, zoom_start=1.0, zoom_end=1.06, pan_x=0, pan_y=0):
    """Applies smooth cinematic camera creep/zoom to a static plate."""
    h, w = plate.shape[:2]
    progress = min(1.0, max(0.0, local_t / max(0.01, duration)))
    zoom = zoom_start + (zoom_end - zoom_start) * progress
    cx = w * 0.5 + pan_x * progress
    cy = h * 0.5 + pan_y * progress
    M = cv2.getRotationMatrix2D((cx, cy), 0, zoom)
    return cv2.warpAffine(plate, M, (w, h), borderMode=cv2.BORDER_REFLECT)


def draw_enclosed_mosquito_net(frame: np.ndarray, width: int, height: int, t: float):
    """
    Subtle atmospheric sheer textile breathing and claustrophobic vignette over the bedroom plate.
    Preserves the authentic photorealistic plate while adding eerie claustrophobic enclosure.
    """
    # 1. Subtle rhythmic breathing vignette (claustrophobic enclosure)
    pulse = math.sin(t * 1.5) * 0.04
    h, w = frame.shape[:2]
    Y, X = np.ogrid[:h, :w]
    center_y, center_x = h / 2.0, w / 2.0
    dist_sq = ((X - center_x) / (w * 0.55)) ** 2 + ((Y - center_y) / (h * 0.55)) ** 2
    vignette = np.clip(1.0 - (dist_sq * (0.42 + pulse)), 0.35, 1.0)
    for c in range(3):
        frame[:, :, c] = (frame[:, :, c] * vignette).astype(np.uint8)

    # 2. Ultra-fine micro textile weave shimmer (fine 1-pixel sheer mesh grain)
    weave = (np.sin(X * 1.2) * np.sin(Y * 1.2) * 4.0).astype(np.int16)
    adjusted = np.clip(frame.astype(np.int16) + weave[:, :, None], 0, 255).astype(np.uint8)
    frame[:] = adjusted


class NoirTimeline:
    """Master scene coordinator for the 300s (5-minute) analog horror film."""
    def __init__(self, global_config: dict = None):
        self.cfg = global_config or load_global_config()
        self.plates = {}
        self._load_plates()

    def _load_plates(self):
        plates_dir = os.path.join(ROOT, "plates")
        posters_dir = os.path.join(ROOT, "assets", "posters")

        mapping = {
            "tower": "scene-01.jpeg",
            "living_room": "scene-02.jpeg",
            "tv_knobs": "scene-03.jpeg",
            "mcr_studio": "scene-04.jpeg",
            "courtyard": "scene-05.jpeg",
            "homestead": "scene-05.jpeg",
            "door_latch": "scene-06.jpeg",
            "bamboo_mist": "scene-07.jpeg",
            "telephone": "scene-08.jpeg",
            "black_cat": "scene-09.jpeg",
            "pond": "scene-10.jpeg",
            "bedroom": "scene-11.jpeg",
            "moshari": "scene-11.jpeg",
            "entity": "scene-12.jpeg",
            "net_pov": "scene-13.jpeg",
            "man_face": "scene-14.jpeg",
            "optical_spiral": "scene-15.jpeg",
            "tumbling_man": "scene-16.jpeg",
            "scanline_dissolve": "scene-17.jpeg",
            "cosmic_eye": "scene-18.jpeg",
            "empty_cot": "scene-19.jpeg",
            "cathode_collapse": "scene-20.jpeg",
            "sector_map_plate": "scene-21.jpeg",
            "civil_danger_plate": "scene-22.jpeg",
            "stormy_homestead": "scene-23.jpeg",
            "newspaper_cutting": "scene-24.jpeg",
            "rusted_handpump": "scene-25.jpeg",
            "protective_occult_wall": "scene-26.jpeg",
            "macro_pupil_tv_reflection": "scene-27.jpeg",
            "aerial_crossroads": "scene-28.jpeg"
        }
        for key, fname in mapping.items():
            path = os.path.join(plates_dir, fname)
            if os.path.exists(path):
                img = cv2.imread(path)
                if img is not None:
                    # Apply automated Open-Source AI Watermark Removal
                    clean_img = scrub_ai_watermark(img)
                    self.plates[key] = cv2.cvtColor(clean_img, cv2.COLOR_BGR2RGB)
                else:
                    self.plates[key] = create_placeholder_plate(1280, 720, label=key)
            else:
                self.plates[key] = create_placeholder_plate(1280, 720, label=key)

    def get_plate(self, name: str, w: int, h: int) -> np.ndarray:
        raw = self.plates.get(name)
        if raw is None:
            raw = create_placeholder_plate(w, h, label=name)
        if raw.shape[1] != w or raw.shape[0] != h:
            return cv2.resize(raw, (w, h), interpolation=cv2.INTER_AREA)
        return raw.copy()

    def render_frame_at(self, t: float, width: int = 1280, height: int = 720, audio_features: dict = None) -> np.ndarray:
        """
        Renders the master frame across the complete 300-second timeline.
        """
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        audio_features = audio_features or {"sub_bass": 0.1, "rms": 0.1, "transient": False}
        sub_bass = audio_features.get("sub_bass", 0.1)

        # =========================================================================
        # ACT I: THE EMERGENCY BROADCAST INTERRUPTION & ALERT (00:00 - 00:45)
        # =========================================================================
        if t < 6.0:
            # Shot 1: Bharat Darpan station ID (6.0s - Emergency Broadcast)
            doordarshan_alert.draw_bharat_darpan_logo(frame, width // 2, int(height * 0.35), radius=int(height * 0.12), t=t)
            text_overlay.draw_text(frame, "ভারত দর্পণ কেন্দ্র কলকাতা", (width // 2, int(height * 0.62)),
                                   font_size=int(height * 0.040), fill_color=(245, 205, 55), anchor="mm")
            text_overlay.draw_text(frame, "সত্যম শিবম সুন্দরম • মধ্যরাত্রিকালীন বিশেষ অধিবেশন", (width // 2, int(height * 0.70)),
                                   font_size=int(height * 0.028), fill_color=(212, 175, 55), anchor="mm")

        elif 6.0 <= t < 14.0:
            # Shot 2: Upgraded TV News Broadcast (Realistic) (8.0s - Emergency Broadcast)
            st = t - 6.0
            frame[:] = zoom_pan(self.get_plate("stormy_homestead", width, height), st, 8.0, 1.0, 1.05)
            frame = news_broadcast.draw_corrupted_news_overlay(
                frame, t=t,
                headline="গ্রামের জঙ্গল রহস্য, জেলায় ছড়াল আতঙ্ক",
                sub_headline="বাঁশবনে অদ্ভুত শব্দ, এলাকায় চাঞ্চল্য",
                ticker_text="নিস্তব্ধপুরে সান্ধ্য আইন জারি  |  বাঁশবনে আলো জ্বালাবেন না  |  অচেনা কণ্ঠে সাড়া নিষেধ  |  পশ্চিমবঙ্গে সতর্কতা",
                sector_code="রাত্রি ৩ | ০০০০ ৩",
                clock_str="03:12 AM",
                weather_str="24°C",
                channel_name="দর্পণ বাংলা",
                signal_integrity=98,
                is_recorded=False,
                globe_corrupted=False
            )

        elif 14.0 <= t < 22.0:
            # Shot 3: Upgraded TV News Broadcast (Corrupted) (8.0s - Corrupted / Glitching Text)
            st = t - 14.0
            frame[:] = zoom_pan(self.get_plate("stormy_homestead", width, height), st, 8.0, 1.05, 1.10)
            sig_val = int(np.clip(98 - st * 10, 24, 98))
            frame = news_broadcast.draw_corrupted_news_overlay(
                frame, t=t,
                headline="ওরা দরজার বাইরে দাঁড়িয়ে আছে",
                sub_headline="নিশিডাক শুনলে ঘরের দরজা বন্ধ রাখুন, কোনো সাড়া দেবেন না",
                ticker_text="জরুরি অবস্থা  |  সিগন্যাল ড্রপ  |  কোথাও যাবেন না  |  টিভির পর্দায় চোখ রাখবেন না  |  নিশিডাকের ডাকে সাড়া দেবেন না",
                sector_code="রাত্রি ৩ | ০০০০ ৩",
                clock_str="03:12 AM",
                weather_str="24°C",
                channel_name="দর্পণ বাংলা",
                signal_integrity=sig_val,
                is_recorded=(st >= 2.5),  # Flips to RECORDED
                globe_corrupted=True      # Globe morphs into staring dilated pupil
            )

        elif 22.0 <= t < 29.0:
            # Shot 4: Glowing Red CRT Vector Sector Radar Map (7.0s - Warning / Instruction)
            frame = sector_map.draw_sector_radar_map(frame, t=t, sub_bass=sub_bass)

        elif 29.0 <= t < 37.0:
            # Shot 5: Saturated Blood-Red Civil Danger Screen (8.0s - Emergency Broadcast)
            frame = civil_danger.draw_civil_danger_screen(frame, t=t, sub_bass=sub_bass)

        elif 37.0 <= t < 41.0:
            # Shot 6: High-Readability Broadcast Card 1 (4.0s - Quick Dialogue / Reaction)
            st = t - 37.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“কে?... দরজায় কে ধাক্কা দিচ্ছে?”", "[ Who is that?... Who is banging on the door? ]", t=st
            )

        elif 41.0 <= t < 45.0:
            # Shot 7: High-Readability Broadcast Card 2 (4.0s - Normal Dialogue Card)
            st = t - 41.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“দরজা খুলবেন না। ওটা আপনার মা নয়।”", "[ Do not open the door. That is not your mother. ]", t=st
            )

        # =========================================================================
        # ACT II: THE RURAL LOCKDOWN & THE FIRST CALL (00:45 - 01:30)
        # =========================================================================
        elif 45.0 <= t < 53.0:
            # Shot 8: Solitary Farmhouse in Moonlit Plain (8.0s - Atmospheric B-Roll)
            # Tap on right side completely removed per user request
            st = t - 45.0
            frame[:] = zoom_pan(self.get_plate("homestead", width, height), st, 8.0, 1.0, 1.07)
            banana_trees.draw_banana_tree(frame, int(width * 0.90), height, t, scale=0.9, wind_strength=0.7)

        elif 53.0 <= t < 60.0:
            # Shot 9: Rule 1 Civil Defense Card (7.0s - Warning / Instruction)
            st = t - 53.0
            frame[:] = self.get_plate("homestead", width, height)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85)
            text_overlay.draw_rule_card(
                frame, "[বিধি ১] (RULE 1)",
                "রাত বারোটার পর কলাবাগান থেকে চেনা গলায় ডাকলেও দরজা খুলবেন না।",
                "DO NOT OPEN THE DOOR IF FAMILIAR VOICES CALL FROM THE BANANA TREES AFTER MIDNIGHT.",
                y_start=int(height * 0.70)
            )

        elif 60.0 <= t < 67.0:
            # Shot 10: 1:07 MARK - Left-Hand Cast-Iron Tube-Well with Dripping Black Fluid & Cloud Time-Lapse
            st = t - 60.0
            frame[:] = zoom_pan(self.get_plate("homestead", width, height), st, 7.0, 1.0, 1.05)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85, wind_strength=0.6)
            tubewell_scene.draw_tubewell_scene_0107(frame, t, width, height)

        elif 67.0 <= t < 74.0:
            # Shot 11: Macro B-Roll - Weathered Teak Door & Rusted Latch (7.0s - Macro B-Roll)
            st = t - 67.0
            frame[:] = zoom_pan(self.get_plate("door_latch", width, height), st, 7.0, 1.0, 1.08)

        elif 74.0 <= t < 80.0:
            # Shot 12: Broadcast Card 3 - The First Call (6.0s - Normal Dialogue Card)
            st = t - 74.0
            text_overlay.draw_broadcast_readability_card(
                frame, "প্রথম ডাক: “বিমল... ও বিমল... একবার বাইরে আয় না রে...”",
                "[ First Call: 'Bimal... O Bimal... come outside just once...' ]", t=st
            )

        elif 80.0 <= t < 86.0:
            # Shot 13: Archival B-Roll - 1994 Yellowed Bengali Newspaper Cutting (6.0s - Hidden Message / Lore)
            st = t - 80.0
            frame[:] = zoom_pan(self.get_plate("newspaper_cutting", width, height), st, 6.0, 1.0, 1.07)
            text_overlay.draw_text(
                frame, "সরকারি নথি ১৯৯৪: নিস্তব্ধপুর তদন্ত",
                (width // 2, int(height * 0.12)), font_size=int(height * 0.034), fill_color=(240, 210, 60), anchor="mm"
            )

        elif 86.0 <= t < 90.0:
            # Shot 14: Macro B-Roll - Rotary Telephone Off the Hook (4.0s - Normal Dialogue Card)
            st = t - 86.0
            frame[:] = zoom_pan(self.get_plate("telephone", width, height), st, 4.0, 1.0, 1.06, pan_y=10)
            text_overlay.draw_text(
                frame, "“লাইন কেটে গেছে। ফোন তোলার মতো কেউ বেঁচে নেই।”",
                (width // 2, int(height * 0.86)), font_size=int(height * 0.032), fill_color=(230, 230, 230), anchor="mm"
            )

        # =========================================================================
        # ACT III: THE MOSQUITO NET METAMORPHOSIS (01:30 - 02:20)
        # =========================================================================
        elif 90.0 <= t < 97.0:
            # Shot 15: Interior Bedroom draped in sheer white Mosquito Net (7.0s - Atmospheric B-Roll)
            st = t - 90.0
            frame[:] = zoom_pan(self.get_plate("bedroom", width, height), st, 7.0, 1.0, 1.06)

        elif 97.0 <= t < 104.0:
            # Shot 16: Rule 2 Civil Defense Card (7.0s - Warning / Instruction)
            st = t - 97.0
            frame[:] = self.get_plate("bedroom", width, height)
            text_overlay.draw_rule_card(
                frame, "[বিধি ২] (RULE 2)",
                "ঘরের মেঝেতে পোকার পা বেরোতে শুরু করলে শান্ত থাকুন। নড়াচড়া করবেন না।",
                "IF INSECT LEGS EMERGE FROM THE FLOOR: STAY STILL. DO NOT MOVE.",
                y_start=int(height * 0.70)
            )

        elif 104.0 <= t < 112.0:
            # Shot 17: 1:49 MARK - TIGHTLY ENCLOSED MOSQUITO NET (Spooky sheer fabric cage)
            st = t - 104.0
            frame[:] = zoom_pan(self.get_plate("bedroom", width, height), st, 8.0, 1.0, 1.06)
            draw_enclosed_mosquito_net(frame, width, height, t)

        elif 112.0 <= t < 117.0:
            # Shot 18: Broadcast Card 4 - The Second Call (5.0s - Normal Dialogue Card)
            st = t - 112.0
            text_overlay.draw_broadcast_readability_card(
                frame, "দ্বিতীয় ডাক: “দরজা খোল বাবা... মা এসেছি... বৃষ্টিতে ভিজে যাচ্ছি রে...”",
                "[ Second Call: 'Open the door child... Mother has come home... I am getting drenched in the rain...' ]", t=st
            )

        elif 117.0 <= t < 125.0:
            # Shot 19: 2:02 MARK - KAFKAESQUE SPIDER ERUPTION AT EMERGENCY BEEP SWELL
            st = t - 117.0
            frame[:] = self.get_plate("bedroom", width, height)
            draw_enclosed_mosquito_net(frame, width, height, t)

            if t < 122.0:
                # Before 2:02: Remains VERY TINY, subtle arachnid crawling under the cot
                bimal_metamorphosis.draw_bimal_metamorphosis(
                    frame, t, int(width * 0.48), int(height * 0.76), progress=0.35, scale=0.25
                )
            else:
                # At 2:02 emergency beep swell: erupts into GIANT room-sized spider spanning the mosquito net!
                swell = min(1.0, (t - 122.0) / 1.6)
                giant_scale = 0.25 + 2.3 * (swell ** 1.5)  # Expands to 2.55x
                bimal_metamorphosis.draw_bimal_metamorphosis(
                    frame, t, int(width * 0.50), int(height * 0.62), progress=1.0,
                    cataract_glow=1.0, jitter_hz=34.0, scale=giant_scale
                )

        elif 125.0 <= t < 129.0:
            # Shot 20A: 2:05 MARK - 'ত্রিনেত্র জেগে উঠছে...' HUGE TYPOGRAPHY ON BLANK SCREEN
            st = t - 125.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“ত্রিনেত্র জেগে উঠছে...”",
                "[ The Third Eye is awakening... ]", t=st
            )

        elif 129.0 <= t < 132.0:
            # Shot 20B: SLOW GRADUAL EMERGENCE OF THE MANDALA EYE DEVELOPING OUT OF DARKNESS
            st = t - 129.0
            frame[:, :] = [4, 4, 6]
            eye_opacity = min(1.0, st / 2.8)
            overlay = frame.copy()
            trinetra_eye.draw_trinetra_eye(overlay, width // 2, height // 2, t, scale=0.95, dilation_extra=sub_bass)
            cv2.addWeighted(overlay, eye_opacity, frame, 1.0 - eye_opacity, 0, frame)

        elif 132.0 <= t < 140.0:
            # Shot 21: High-Readability Card 5 - Body Measurement (8.0s)
            st = t - 132.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“ওটা আপনার মা নয়...\nওটা আপনার শরীরের মাপ নিচ্ছে...”",
                "[ That is not your mother... It is taking the measurement of your body... ]", t=st
            )

        # =========================================================================
        # ACT IV: THE UNCANNY SHADOWY HYPER-OBJECT TRANSMISSION (02:20 - 03:05)
        # =========================================================================
        elif 140.0 <= t < 147.0:
            # Shot 22: Shadowy Hyper-Object Figure perched on Split-Bamboo Fence (no cat)
            st = t - 140.0
            frame[:] = zoom_pan(self.get_plate("homestead", width, height), st, 7.0, 1.0, 1.04)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85)
            hulo_cat.draw_shadowy_figure(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.0)

        elif 147.0 <= t < 154.0:
            # Shot 23: Rule 3 Civil Defense Card (7.0s - Warning / Instruction)
            st = t - 147.0
            frame[:] = self.get_plate("homestead", width, height)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85)
            hulo_cat.draw_shadowy_figure(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.0)
            text_overlay.draw_rule_card(
                frame, "[বিধি ৩] (RULE 3)",
                "বাঁশের বেড়ায় বসে থাকা ছায়ার চোখের দিকে একদম তাকাবেন না।",
                "DO NOT LOOK INTO THE EYES OF THE SHADOW PERCHED ON THE FENCE.",
                y_start=int(height * 0.70)
            )

        elif 154.0 <= t < 162.0:
            # Shot 24: 2:33 MARK - FULL-SCREEN NIGHT SKY CLOUD TIME-LAPSE & ELONGATING SHADOW COLUMN
            st = t - 154.0
            # Continuous multi-layered volumetric cloud time-lapse across the moon
            cloud_timelapse.render_cloud_timelapse_sky(frame, t, width, height, cloud_speed=50.0)
            banana_trees.draw_banana_tree(frame, int(width * 0.90), height, t, scale=0.85, wind_strength=0.7)
            stretch = min(1.0, st / 7.0)
            hulo_cat.draw_shadowy_figure(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=stretch)

        elif 162.0 <= t < 169.0:
            # Shot 25: Broadcast Card 6 - Shadowy Entity Intertitle (7.0s)
            st = t - 162.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“ছায়ামূর্তিটা ডাকছে না... আকাশ ওর গলায় আপনার নাম ধরে ডাকছে...”",
                "[ The shadow is not calling you... The sky is using its voice to speak your name... ]", t=st
            )

        elif 169.0 <= t < 176.0:
            # Shot 26: Exterior Mud Wall with Protective Occult Yantra Diagrams (7.0s - Occult B-Roll)
            st = t - 169.0
            frame[:] = zoom_pan(self.get_plate("protective_occult_wall", width, height), st, 7.0, 1.0, 1.07)
            text_overlay.draw_text(
                frame, "সুরক্ষা বলয় ভেঙে গেছে",
                (width // 2, int(height * 0.88)), font_size=int(height * 0.034), fill_color=(235, 70, 70), anchor="mm"
            )

        elif 176.0 <= t < 182.0:
            # Shot 27: Aerial Crossroads at 3:00 AM with Swirling Fog (6.0s - Aerial B-Roll)
            st = t - 176.0
            frame[:] = zoom_pan(self.get_plate("aerial_crossroads", width, height), st, 6.0, 1.0, 1.06)

        elif 182.0 <= t < 185.0:
            # Shot 28: Quick Dialogue Countdown (3.0s - Quick Dialogue / Reaction)
            st = t - 182.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“শেষ ডাক আর কিছুক্ষণেই...”", "[ The Final Call is coming... ]", t=st
            )

        # =========================================================================
        # ACT V: BETWEEN THE NOTES - THE ABYSS PLUNGE (03:05 - 03:55)
        # =========================================================================
        elif 185.0 <= t < 194.0:
            # Shot 29: Between the Notes Interstitial Slate (9.0s - High Readability Broadcast Card)
            st = t - 185.0
            text_overlay.draw_broadcast_readability_card(
                frame, "বিটুইন দ্য নোটস: অ্যানালগ হরর চলচ্চিত্র\nপর্ব শূন্য: মহাকর্ষের পতন",
                "[ BETWEEN THE NOTES: AN ANALOG HORROR FILM / EPISODE ZERO: FALL OF GRAVITY ]", t=st
            )

        elif 194.0 <= t < 205.0:
            # Shot 30: Hypnotic Optical Spiral Abyss (11.0s - Abyss B-Roll)
            st = t - 194.0
            frame = cosmic.draw_after_midnight_abyss(frame, st, sub_bass=sub_bass)

        elif 205.0 <= t < 216.0:
            # Shot 31: Tumbling Man Vertigo Plunge into Spiral Abyss (11.0s - Vertigo B-Roll)
            st = t - 205.0
            frame[:] = zoom_pan(self.get_plate("tumbling_man", width, height), st, 11.0, 1.0, 1.15)
            frame = distortion.apply_lens_breathing(frame, t, amplitude=0.04)

        elif 216.0 <= t < 225.0:
            # Shot 32: Archival Decoupling Log (9.0s - Hidden Message / Lore)
            st = t - 216.0
            frame = cosmic.draw_after_midnight_abyss(frame, st + 10.0, sub_bass=sub_bass)
            text_overlay.draw_text(frame, "সতর্কতা: মাধ্যাকর্ষণ আর কাজ করছে না।", (width // 2, int(height * 0.16)),
                                   font_size=int(height * 0.036), fill_color=(245, 60, 60), anchor="mm")
            text_overlay.draw_text(frame, "WARNING: GRAVITATIONAL VECTOR PERMANENTLY DECOUPLED.", (width // 2, int(height * 0.22)),
                                   font_size=int(height * 0.022), fill_color=(220, 220, 220), anchor="mm")
            text_overlay.draw_text(frame, "YOU ARE FALLING UPWARD INTO THE CARRIER WAVE.", (width // 2, int(height * 0.27)),
                                   font_size=int(height * 0.020), fill_color=(180, 180, 180), anchor="mm")

        elif 225.0 <= t < 235.0:
            # Shot 33: Human Face Disintegrating into Scanlines & Phosphor (10.0s - Glitch Dissolve B-Roll)
            st = t - 225.0
            frame[:] = zoom_pan(self.get_plate("scanline_dissolve", width, height), st, 10.0, 1.0, 1.10)
            frame = distortion.apply_gravity_warp(frame, t, intensity=0.35)

        # =========================================================================
        # ACT VI: TRINETRA - TANTRIC COSMIC DREAD & THE THIRD CALL (03:55 - 04:35)
        # =========================================================================
        elif 235.0 <= t < 244.0:
            # Shot 34: Celestial Third Eye (ত্রিনেত্র) in Monsoon Clouds (9.0s - Cosmic B-Roll)
            st = t - 235.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            trinetra_eye.draw_trinetra_eye(frame, width // 2, int(height * 0.44), t, scale=1.1, dilation_extra=sub_bass, sinister_red=0.85)
            banana_trees.draw_banana_tree(frame, int(width * 0.08), height, t, scale=0.8, wind_strength=0.5)
            banana_trees.draw_banana_tree(frame, int(width * 0.92), height, t, scale=0.8, wind_strength=0.5)

        elif 244.0 <= t < 252.0:
            # Shot 35: 4:11 MARK - SINISTER BLOOD-RED EYE LOOK & FINAL PROHIBITION (8.0s)
            st = t - 244.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            trinetra_eye.draw_trinetra_eye(frame, width // 2, int(height * 0.44), t, scale=1.20, dilation_extra=sub_bass, sinister_red=1.0)
            text_overlay.draw_rule_card(
                frame, "[চূড়ান্ত নিষেধ] (RULE 4)",
                "আকাশের লাল চোখের দিকে তাকাবেন না। ও অনেক আগেই আপনাকে দেখে ফেলেছে।",
                "DO NOT GAZE INTO THE RED EYE IN THE SKY. IT SAW YOU LONG AGO.",
                y_start=int(height * 0.70)
            )

        elif 252.0 <= t < 263.0:
            # Shot 36: Extreme Macro Sinister Red Pupil Dilation swallowing the heavens (11.0s)
            st = t - 252.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            dilation = min(1.2, st / 8.0) + sub_bass * 0.5
            trinetra_eye.draw_trinetra_eye(frame, width // 2, int(height * 0.44), t, scale=1.35, dilation_extra=dilation, sinister_red=1.0)

        elif 263.0 <= t < 273.0:
            # Shot 37: Final Threat / Climax Reveal Card (10.0s - Final Threat / Reveal)
            st = t - 263.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“তৃতীয় ডাক শেষ।\nআপনি আগেই উত্তর দিয়ে ফেলেছেন।”",
                "[ The Third Call is complete. You have already answered. ]", t=st
            )

        elif 273.0 <= t < 275.0:
            # Shot 38: Subliminal Flash Cadence (2.0s - Rapid Montage)
            st = t - 273.0
            phase = int(st * 6.0) % 4
            if phase == 0:
                frame[:] = self.get_plate("door_latch", width, height)
            elif phase == 1:
                frame = civil_danger.draw_civil_danger_screen(frame, t=t, sub_bass=sub_bass)
            elif phase == 2:
                frame = sector_map.draw_sector_radar_map(frame, t=t, sub_bass=sub_bass)
            else:
                frame[:] = self.get_plate("macro_pupil_tv_reflection", width, height)

        # =========================================================================
        # ACT VII: TERMINAL SEVERANCE & MINIMALIST END CREDITS (04:35 - 05:00)
        # =========================================================================
        elif 275.0 <= t < 282.0:
            # Shot 39: Empty Cot Aftermath (7.0s - Emergency Broadcast Decree)
            st = t - 275.0
            frame[:] = zoom_pan(self.get_plate("empty_cot", width, height), st, 7.0, 1.0, 1.05)
            text_overlay.draw_text(
                frame, "টেলিভিশন সম্প্রচার অনির্দিষ্টকালের জন্য বন্ধ থাকবে।",
                (width // 2, int(height * 0.88)), font_size=int(height * 0.034), fill_color=(240, 240, 240), anchor="mm"
            )

        elif 282.0 <= t < 284.5:
            # Shot 40: Horizontal Cathode Line Collapse (2.5s)
            st = t - 282.0
            frame[:, :] = [4, 4, 6]
            line_w = int(width * max(0.02, 1.0 - (st / 2.5)))
            cv2.line(frame, (width // 2 - line_w // 2, height // 2),
                     (width // 2 + line_w // 2, height // 2), (240, 240, 235), 2)

        elif 284.5 <= t < 287.0:
            # Shot 41: Phosphor Dot Pinch Decay to Black (2.5s)
            st = t - 284.5
            frame[:, :] = [4, 4, 6]
            dot_r = max(1, int(4 * (1.0 - (st / 2.5))))
            cv2.circle(frame, (width // 2, height // 2), dot_r, (120, 240, 140), -1)

        else:
            # Shot 42: PURE MINIMALIST THEATRICAL END CREDITS (13.0s - 04:47 to 05:00)
            st = t - 287.0
            frame = text_overlay.draw_minimal_end_credits(frame, t=st)

        # =========================================================================
        # UNIFIED CRT & VHS POST-PROCESSING PIPELINE
        # =========================================================================
        # Check if frame is a high-readability text card, rule card, slate, or credits
        is_text_card = (
            (t < 6.0) or
            (37.0 <= t < 45.0) or
            (53.0 <= t < 60.0) or
            (74.0 <= t < 80.0) or
            (97.0 <= t < 104.0) or
            (112.0 <= t < 117.0) or
            (125.0 <= t < 129.0) or
            (132.0 <= t < 140.0) or
            (147.0 <= t < 154.0) or
            (162.0 <= t < 169.0) or
            (182.0 <= t < 194.0) or
            (244.0 <= t < 252.0) or
            (263.0 <= t < 273.0) or
            (t >= 287.0)
        )

        if is_text_card:
            # Ultra-mild post-processing to guarantee 100% crispness, zero jitter, and readability
            frame = crt.apply_crt(
                frame,
                curvature=0.01,
                scanline_strength=0.04,
                vignette_strength=0.10,
                chromatic_aberration_px=0.0,
                head_switching_px=0,
                sub_bass=0.0,
                t=t
            )
        else:
            # Grounded cinematic analog horror: subtle scanlines, no over-the-top haze
            crt_cfg = self.cfg.get("crt", {})
            vhs_cfg = self.cfg.get("vhs", {})

            frame = crt.apply_crt(
                frame,
                curvature=crt_cfg.get("barrel_distortion", 0.05),
                scanline_strength=0.14,  # Reduced from 0.22 for realism
                vignette_strength=0.25,  # Reduced from 0.35
                chromatic_aberration_px=1.2,  # Controlled chromatic split
                head_switching_px=18,
                sub_bass=sub_bass,
                t=t
            )
            # Tracking line glitching tied directly to audio sub-bass hits
            tracking_prob = 0.12 if sub_bass > 0.3 else 0.03
            frame = vhs.apply_vhs_tracking(
                frame, t,
                tear_strength=0.18,
                tracking_prob=tracking_prob,
                sub_bass=sub_bass
            )

        return frame
