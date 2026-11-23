"""
Master Timeline Compositor for Project NOIR / Nishidak.
Coordinates the full 5-Minute (300 Seconds, 7,200 frames @ 24 fps) cinematic analog horror film.

Calibrated to the Silent Reading Timing Table:
- Quick dialogue / reaction: 3–4 sec
- Normal dialogue card: 4–6 sec
- Warning or instruction: 7–8 sec
- Emergency broadcast: 8–9 sec
- Corrupted / glitching text: 7–8 sec
- Hidden message / lore: 8–9 sec
- Final threat / reveal: 10 sec

Narrative Structure across 7 Acts:
- ACT I: The Signal Interrupt & Corrupted TV News (00:00 – 00:45)
- ACT II: Rural Lockdown & The First Call (00:45 – 01:30)
- ACT III: The Mosquito Net Metamorphosis (01:30 – 02:20)
- ACT IV: The Uncanny Feline Transmission (02:20 – 03:05)
- ACT V: After Midnight, Somewhere Else — Abyss Plunge (03:05 – 03:55)
- ACT VI: Trinetra — Tantric Cosmic Dread & The Third Call (03:55 – 04:35)
- ACT VII: Terminal Severance & Theatrical End Credits (04:35 – 05:00)
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def zoom_pan(plate, local_t, duration, zoom_start=1.0, zoom_end=1.06, pan_x=0, pan_y=0):
    """Applies smooth cinematic camera creep/zoom to a static plate."""
    h, w = plate.shape[:2]
    progress = min(1.0, max(0.0, local_t / max(0.01, duration)))
    zoom = zoom_start + (zoom_end - zoom_start) * progress
    cx = w * 0.5 + pan_x * progress
    cy = h * 0.5 + pan_y * progress
    M = cv2.getRotationMatrix2D((cx, cy), 0, zoom)
    return cv2.warpAffine(plate, M, (w, h), borderMode=cv2.BORDER_REFLECT)


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
                    self.plates[key] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                else:
                    self.plates[key] = create_placeholder_plate(1280, 720, label=key)
            else:
                self.plates[key] = create_placeholder_plate(1280, 720, label=key)

        # End credits billboard poster
        end_cred_path = os.path.join(posters_dir, "poster_var5_abyss_end_credits.png")
        if os.path.exists(end_cred_path):
            img = cv2.imread(end_cred_path)
            if img is not None:
                self.plates["end_credits_billboard"] = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

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
        # ACT I: THE EMERGENCY BROADCAST INTERRUPTION & ALERT (00:00 – 00:45)
        # =========================================================================
        if t < 6.0:
            # Shot 1: Bharat Darpan station ID & spinning mandala logo (6.0s - Emergency Broadcast)
            doordarshan_alert.draw_bharat_darpan_logo(frame, width // 2, int(height * 0.35), radius=int(height * 0.12), t=t)
            text_overlay.draw_text(frame, "ভারত দর্পণ কেন্দ্র কলকাতা", (width // 2, int(height * 0.62)),
                                   font_size=int(height * 0.038), fill_color=(245, 205, 55), anchor="mm")
            text_overlay.draw_text(frame, "সত্যম শিবম সুন্দরম • মধ্যরাত্রিকালীন বিশেষ অধিবেশন", (width // 2, int(height * 0.70)),
                                   font_size=int(height * 0.026), fill_color=(212, 175, 55), anchor="mm")

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
            if math.sin(t * 35.0) > 0.8:
                frame = np.clip(frame.astype(np.float32) * 1.18, 0, 255).astype(np.uint8)
            sig_val = int(np.clip(98 - st * 10, 24, 98))
            frame = news_broadcast.draw_corrupted_news_overlay(
                frame, t=t,
                headline="উহারা দরজার বাহিরে অবস্থান করিতেছে",
                sub_headline="নিশি ডাকের আহ্বান শুনিবামাত্র দরজা বন্ধ রাখুন — কদাচ উত্তর দিবেন না",
                ticker_text="জরুরি অবস্থা  |  সিগন্যাল ড্রপ  |  কোথাও যাবেন না  |  পর্দায় চোখ রাখবেন না  |  নিশিডাকের আহ্বান গ্রহণ করিবেন না",
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
            # Shot 6: Silent Film Intertitle 1 (4.0s - Quick Dialogue / Reaction)
            st = t - 37.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“কে?... কপাটে কে আঘাত করিতেছে?”", "[ Who is knocking at the door? ]", t=st
            )

        elif 41.0 <= t < 45.0:
            # Shot 7: Silent Film Intertitle 2 (4.0s - Normal Dialogue Card)
            st = t - 41.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“কপাট খুলিবেন না। উহা আপনার মাতা নহে।”", "[ Do not open. That is not your mother. ]", t=st
            )

        # =========================================================================
        # ACT II: THE RURAL LOCKDOWN & THE FIRST CALL (00:45 – 01:30)
        # =========================================================================
        elif 45.0 <= t < 53.0:
            # Shot 8: Solitary Farmhouse in Moonlit Plain (8.0s - Atmospheric B-Roll)
            st = t - 45.0
            frame[:] = zoom_pan(self.get_plate("homestead", width, height), st, 8.0, 1.0, 1.07)
            banana_trees.draw_banana_tree(frame, int(width * 0.90), height, t, scale=0.9, wind_strength=0.7)
            banana_trees.draw_creaking_handpump(frame, int(width * 0.65), int(height * 0.82), t, scale=1.0)

        elif 53.0 <= t < 60.0:
            # Shot 9: Rule 1 Civil Defense Card (7.0s - Warning / Instruction)
            st = t - 53.0
            frame[:] = self.get_plate("homestead", width, height)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85)
            text_overlay.draw_rule_card(
                frame, "[বিধি ১] (RULE 1)",
                "রাত ১২টার পর কলাবাগান থেকে চেনা কণ্ঠে নিশিডাক শুনলে দরজা খুলবেন না।",
                "DO NOT ANSWER FAMILIAR VOICES CALLING FROM THE BANANA GROVES.",
                y_start=int(height * 0.74)
            )

        elif 60.0 <= t < 67.0:
            # Shot 10: Macro B-Roll — Rusted Tube-well Handpump dripping viscous water (7.0s - Macro B-Roll)
            st = t - 60.0
            frame[:] = zoom_pan(self.get_plate("rusted_handpump", width, height), st, 7.0, 1.0, 1.06, pan_y=-10)

        elif 67.0 <= t < 74.0:
            # Shot 11: Macro B-Roll — Weathered Teak Door & Rusted Latch (7.0s - Macro B-Roll)
            st = t - 67.0
            frame[:] = zoom_pan(self.get_plate("door_latch", width, height), st, 7.0, 1.0, 1.08)
            jitter = int(math.sin(t * 32.0) * (3.0 if sub_bass > 0.2 else 1.0))
            if jitter != 0:
                frame[:] = np.roll(frame, jitter, axis=0)

        elif 74.0 <= t < 80.0:
            # Shot 12: Dialogue Card 1 — The First Call (6.0s - Normal Dialogue Card)
            st = t - 74.0
            text_overlay.draw_silent_film_intertitle(
                frame, "প্রথম আহ্বান: “বিমল... ও বিমল... একবারটি বাহিরে আয়...”",
                "[ The First Call: 'Bimal... O Bimal... come outside just once...' ]", t=st
            )

        elif 80.0 <= t < 86.0:
            # Shot 13: Archival B-Roll — 1994 Yellowed Bengali Newspaper Cutting (6.0s - Hidden Message / Lore)
            st = t - 80.0
            frame[:] = zoom_pan(self.get_plate("newspaper_cutting", width, height), st, 6.0, 1.0, 1.07)
            text_overlay.draw_text(
                frame, "সরকারি নথি ১৯৯৪: নিস্তব্ধপুর তদন্ত",
                (width // 2, int(height * 0.12)), font_size=int(height * 0.030), fill_color=(240, 210, 60), anchor="mm"
            )

        elif 86.0 <= t < 90.0:
            # Shot 14: Macro B-Roll — Rotary Telephone Off the Hook (4.0s - Normal Dialogue Card)
            st = t - 86.0
            frame[:] = zoom_pan(self.get_plate("telephone", width, height), st, 4.0, 1.0, 1.06, pan_y=10)
            text_overlay.draw_text(
                frame, "“সংযোগ বিচ্ছিন্ন। টেলিফোন ধরিবার কেহ নাই।”",
                (width // 2, int(height * 0.86)), font_size=int(height * 0.030), fill_color=(230, 230, 230), anchor="mm"
            )

        # =========================================================================
        # ACT III: THE MOSQUITO NET METAMORPHOSIS (01:30 – 02:20)
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
                "ঘরের মেঝেতে খোলস ও কীটপতঙ্গের পা গজাতে শুরু করলে শান্ত থাকুন।",
                "IF CHITINOUS EXOSKELETON EMERGES: REMAIN FLAT UPON THE RED STONE.",
                y_start=int(height * 0.74)
            )

        elif 104.0 <= t < 112.0:
            # Shot 17: POV through Mosquito Net mesh watching the shadow entity (8.0s - Macro POV B-Roll)
            st = t - 104.0
            frame[:] = zoom_pan(self.get_plate("net_pov", width, height), st, 8.0, 1.0, 1.07)
            frame = distortion.apply_lens_breathing(frame, t, amplitude=0.03)

        elif 112.0 <= t < 117.0:
            # Shot 18: Dialogue Card 2 — The Second Call (5.0s - Normal Dialogue Card)
            st = t - 112.0
            text_overlay.draw_silent_film_intertitle(
                frame, "দ্বিতীয় আহ্বান: “দুয়ার খোল বাছা... মা আসিয়াছি... ভিজিয়া যাইতেছি রে...”",
                "[ The Second Call: 'Open the door child... Mother has come home...' ]", t=st
            )

        elif 117.0 <= t < 125.0:
            # Shot 19: Bimal Metamorphosis 1 — Chitin limb eruption on floor (8.0s - Psychological Actor B-Roll)
            st = t - 117.0
            frame[:] = self.get_plate("bedroom", width, height)
            bimal_metamorphosis.draw_bimal_metamorphosis(
                frame, t, int(width * 0.50), int(height * 0.70), progress=min(0.7, st / 8.0)
            )

        elif 125.0 <= t < 132.0:
            # Shot 20: Bimal Metamorphosis 2 — 32 Hz segmentation & crimson cataract eyes (7.0s - Metamorphosis)
            st = t - 125.0
            frame[:] = self.get_plate("bedroom", width, height)
            bimal_metamorphosis.draw_bimal_metamorphosis(
                frame, t, int(width * 0.48), int(height * 0.72), progress=1.0, cataract_glow=1.0, jitter_hz=32.0
            )
            text_overlay.draw_text(
                frame, "ত্রিনেত্র প্রস্ফুটিত হইতেছে...",
                (width // 2, int(height * 0.18)), font_size=int(height * 0.034), fill_color=(245, 60, 60), anchor="mm"
            )

        elif 132.0 <= t < 140.0:
            # Shot 21: Corrupted Lore Card (8.0s - Corrupted / Glitching Text)
            st = t - 132.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“উহা আপনার মাতা নহে... উহা আপনার চর্মের মাপ লইতেছে...”",
                "[ That is not your mother... It is taking the measurement of your skin... ]", t=st
            )

        # =========================================================================
        # ACT IV: THE UNCANNY FELINE TRANSMISSION & CRACKING REALITY (02:20 – 03:05)
        # =========================================================================
        elif 140.0 <= t < 147.0:
            # Shot 22: Black Tomcat on Split-Bamboo Fence (7.0s - Atmospheric B-Roll)
            st = t - 140.0
            frame[:] = self.get_plate("black_cat", width, height)
            hulo_cat.draw_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.0)

        elif 147.0 <= t < 154.0:
            # Shot 23: Rule 3 Civil Defense Card (7.0s - Warning / Instruction)
            st = t - 147.0
            frame[:] = self.get_plate("homestead", width, height)
            hulo_cat.draw_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.0)
            text_overlay.draw_rule_card(
                frame, "[বিধি ৩] (RULE 3)",
                "বাঁশের বেড়ায় বসা হুলো বেড়ালের চোখের দিকে তাকাবেন না।",
                "DO NOT GAZE INTO THE EYES OF THE TOMCAT UPON THE BAMBOO RAIL.",
                y_start=int(height * 0.74)
            )

        elif 154.0 <= t < 162.0:
            # Shot 24: The Tomcat Neck Stretching upward into the night sky (8.0s - Surreal B-Roll)
            st = t - 154.0
            frame[:] = self.get_plate("homestead", width, height)
            stretch = min(1.0, st / 7.0)
            hulo_cat.draw_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=stretch)

        elif 162.0 <= t < 169.0:
            # Shot 25: Corrupted Intertitle (7.0s - Corrupted / Glitching Text)
            st = t - 162.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“বিড়ালটি ডাকিতেছে না... আকাশ বিড়ালটির কণ্ঠে আপনার নাম উচ্চারণ করিতেছে...”",
                "[ The cat is not crying... The sky speaks your name through its jaws... ]", t=st
            )

        elif 169.0 <= t < 176.0:
            # Shot 26: Exterior Mud Wall with Protective Occult Yantra Diagrams (7.0s - Occult B-Roll)
            st = t - 169.0
            frame[:] = zoom_pan(self.get_plate("protective_occult_wall", width, height), st, 7.0, 1.0, 1.07)
            text_overlay.draw_text(
                frame, "প্রতিরক্ষা রেখা ভঙ্গ হইয়াছে",
                (width // 2, int(height * 0.88)), font_size=int(height * 0.030), fill_color=(235, 70, 70), anchor="mm"
            )

        elif 176.0 <= t < 182.0:
            # Shot 27: Aerial Crossroads at 3:00 AM with Swirling Fog (6.0s - Aerial B-Roll)
            st = t - 176.0
            frame[:] = zoom_pan(self.get_plate("aerial_crossroads", width, height), st, 6.0, 1.0, 1.06)

        elif 182.0 <= t < 185.0:
            # Shot 28: Quick Dialogue Countdown (3.0s - Quick Dialogue / Reaction)
            st = t - 182.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“তৃতীয় আহ্বান সমাসন্ন...”", "[ The Third Call is imminent... ]", t=st
            )

        # =========================================================================
        # ACT V: AFTER MIDNIGHT, SOMEWHERE ELSE — THE ABYSS PLUNGE (03:05 – 03:55)
        # =========================================================================
        elif 185.0 <= t < 194.0:
            # Shot 29: Bharat Darpan Interstitial Slate (9.0s - Hidden Message / Lore)
            st = t - 185.0
            frame[:, :] = [16, 12, 36]
            doordarshan_alert.draw_bharat_darpan_logo(frame, width // 2, int(height * 0.28), radius=int(height * 0.10), t=t)
            text_overlay.draw_text(frame, "মধ্যরাতের পর, অন্য কোথাও", (width // 2, int(height * 0.52)),
                                   font_size=int(height * 0.046), fill_color=(245, 205, 55), anchor="mm")
            text_overlay.draw_text(frame, "AFTER MIDNIGHT, SOMEWHERE ELSE", (width // 2, int(height * 0.61)),
                                   font_size=int(height * 0.026), fill_color=(210, 210, 210), anchor="mm")
            text_overlay.draw_text(frame, "পর্ব শূন্য: মহাকর্ষের বিলুপ্তি  •  EPISODE ZERO", (width // 2, int(height * 0.70)),
                                   font_size=int(height * 0.024), fill_color=(190, 60, 60), anchor="mm")

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
            text_overlay.draw_text(frame, "সতর্কতা: মাধ্যাকর্ষণ ভেক্টর বিচ্ছিন্ন হইয়াছে।", (width // 2, int(height * 0.16)),
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
            frame = noise.apply_static_snow(frame, amount=min(0.65, st / 10.0))

        # =========================================================================
        # ACT VI: TRINETRA — TANTRIC COSMIC DREAD & THE THIRD CALL (03:55 – 04:35)
        # =========================================================================
        elif 235.0 <= t < 244.0:
            # Shot 34: Celestial Third Eye (ত্রিনেত্র) in Monsoon Clouds (9.0s - Cosmic B-Roll)
            st = t - 235.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            trinetra_eye.draw_trinetra_eye(frame, width // 2, int(height * 0.44), t, scale=1.1, dilation_extra=sub_bass)
            banana_trees.draw_banana_tree(frame, int(width * 0.08), height, t, scale=0.8, wind_strength=0.5)
            banana_trees.draw_banana_tree(frame, int(width * 0.92), height, t, scale=0.8, wind_strength=0.5)

        elif 244.0 <= t < 252.0:
            # Shot 35: Rule 4 Final Prohibition Card (8.0s - Warning / Instruction)
            st = t - 244.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            text_overlay.draw_rule_card(
                frame, "[চূড়ান্ত নিষেধ] (RULE 4)",
                "আকাশের রক্তিম নয়নের দিকে তাকাবেন না। উহা আপনাকে বহু পূর্বেই প্রত্যক্ষ করিয়াছে।",
                "DO NOT GAZE INTO THE CRIMSON EYE. IT HAS WITNESSED YOU LONG BEFORE TONIGHT.",
                y_start=int(height * 0.74)
            )

        elif 252.0 <= t < 263.0:
            # Shot 36: Extreme Macro Pupil Dilation swallowing the heavens (11.0s - Macro Eye Dilation)
            st = t - 252.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            dilation = min(1.2, st / 8.0) + sub_bass * 0.5
            trinetra_eye.draw_trinetra_eye(frame, width // 2, int(height * 0.44), t, scale=1.35, dilation_extra=dilation)

        elif 263.0 <= t < 273.0:
            # Shot 37: Final Threat / Climax Reveal Card (10.0s - Final Threat / Reveal)
            st = t - 263.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“তৃতীয় আহ্বান সম্পূর্ণ হইয়াছে। আপনি ইতোমধ্যে উত্তর দিয়াছেন।”",
                "[ The Third Call is complete. You have already answered. ]", t=st
            )

        elif 273.0 <= t < 275.0:
            # Shot 38: Violent Subliminal Flash Cadence (2.0s - Rapid Montage)
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
            frame = noise.apply_static_snow(frame, amount=0.55)

        # =========================================================================
        # ACT VII: TERMINAL SEVERANCE & THEATRICAL END CREDITS (04:35 – 05:00)
        # =========================================================================
        elif 275.0 <= t < 282.0:
            # Shot 39: Empty Cot Aftermath (7.0s - Emergency Broadcast Decree)
            st = t - 275.0
            frame[:] = zoom_pan(self.get_plate("empty_cot", width, height), st, 7.0, 1.0, 1.05)
            text_overlay.draw_text(
                frame, "দূরদর্শন সম্প্রচার অনির্দিষ্টকালের জন্য বন্ধ থাকিবে।",
                (width // 2, int(height * 0.88)), font_size=int(height * 0.032), fill_color=(240, 240, 240), anchor="mm"
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
            # Shot 42: Theatrical Billboard End Credits (13.0s - 04:47 to 05:00)
            st = t - 287.0
            if "end_credits_billboard" in self.plates:
                frame[:] = zoom_pan(self.get_plate("end_credits_billboard", width, height), st, 13.0, 1.0, 1.04)
            else:
                # Elegant typographic credits backup
                frame[:, :] = [8, 8, 12]
                text_overlay.draw_text(frame, "BETWEEN THE NOTES", (width // 2, int(height * 0.28)),
                                       font_size=int(height * 0.045), fill_color=(235, 235, 235), anchor="mm")
                text_overlay.draw_text(frame, "A BETWEEN THE NOTES ORIGINAL", (width // 2, int(height * 0.38)),
                                       font_size=int(height * 0.028), fill_color=(200, 40, 40), anchor="mm")
                text_overlay.draw_text(frame, "ORIGINAL SCORE & SOUND DESIGN BY ATANDRA", (width // 2, int(height * 0.52)),
                                       font_size=int(height * 0.024), fill_color=(210, 210, 210), anchor="mm")
                text_overlay.draw_text(frame, "ANALOG HORROR ENGINE BY SAYAN", (width // 2, int(height * 0.60)),
                                       font_size=int(height * 0.024), fill_color=(210, 210, 210), anchor="mm")
                text_overlay.draw_text(frame, "IN CASE OF NISHIDAK: DO NOT ANSWER", (width // 2, int(height * 0.74)),
                                       font_size=int(height * 0.026), fill_color=(245, 60, 60), anchor="mm")

        # =========================================================================
        # UNIFIED CRT & VHS POST-PROCESSING PIPELINE
        # =========================================================================
        # Billboard credits get milder CRT distortion to keep poster credits perfectly readable
        if t >= 287.0:
            frame = crt.apply_crt(
                frame,
                curvature=0.03,
                scanline_strength=0.12,
                vignette_strength=0.18,
                chromatic_aberration_px=1.0,
                head_switching_px=12,
                sub_bass=sub_bass,
                t=t
            )
            frame = vhs.apply_vhs_tracking(
                frame, t,
                tear_strength=0.10,
                tracking_prob=0.04,
                sub_bass=sub_bass
            )
        else:
            crt_cfg = self.cfg.get("crt", {})
            vhs_cfg = self.cfg.get("vhs", {})

            frame = crt.apply_crt(
                frame,
                curvature=crt_cfg.get("barrel_distortion", 0.08),
                scanline_strength=crt_cfg.get("scanline_strength", 0.22),
                vignette_strength=crt_cfg.get("vignette_strength", 0.35),
                chromatic_aberration_px=crt_cfg.get("chromatic_aberration_px", 2.0),
                head_switching_px=crt_cfg.get("head_switching_band_px", 24),
                sub_bass=sub_bass,
                t=t
            )
            frame = vhs.apply_vhs_tracking(
                frame, t,
                tear_strength=vhs_cfg.get("horizontal_tear_strength", 0.25),
                tracking_prob=vhs_cfg.get("tracking_error_probability", 0.08),
                sub_bass=sub_bass
            )

        return frame
