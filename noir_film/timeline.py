"""
Master Timeline Compositor for Project NOIR / Nishidak.
Coordinates the full 3-Minute (180 Seconds, 4320 frames @ 24 fps) cinematic analog horror film.
Rapid-cut editorial montage pacing with cuts every 2.0 to 4.5 seconds:
- 1994 Bharat Darpan Kendra Calcutta emergency broadcast interruption
- High-detail photorealistic AI plates: mosquito net bedroom, macro rusty door latch,
  misty bamboo grove, telephone off the hook, solitary rural homestead
- Silent film / Alex Kister style dialogue intertitles in authentic Bengali & English
- "After Midnight, Somewhere Else" optical illusion spiral abyss with the tumbling falling man
- Bimal Babu's Kafkaesque metamorphosis on the red-oxide floor
- The Uncanny Black Tomcat stretching its neck into the monsoon clouds
- Tantric Cosmic Dread: Trinetra (Celestial Third Eye) dilating to subterranean sub-bass
- Terminal cathode line collapse and blackout
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
    """Master scene coordinator for the 180s analog horror film."""
    def __init__(self, global_config: dict = None):
        self.cfg = global_config or load_global_config()
        self.plates = {}
        self._load_plates()

    def _load_plates(self):
        plates_dir = os.path.join(ROOT, "plates")
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
            "cathode_collapse": "scene-20.jpeg"
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

    def get_plate(self, name: str, w: int, h: int) -> np.ndarray:
        raw = self.plates.get(name)
        if raw is None:
            raw = create_placeholder_plate(w, h, label=name)
        if raw.shape[1] != w or raw.shape[0] != h:
            return cv2.resize(raw, (w, h), interpolation=cv2.INTER_AREA)
        return raw.copy()

    def render_frame_at(self, t: float, width: int = 1280, height: int = 720, audio_features: dict = None) -> np.ndarray:
        """
        Renders the master frame across the complete 180-second timeline.
        Rapid editorial transitions every 2.0 to 4.5 seconds.
        """
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        audio_features = audio_features or {"sub_bass": 0.1, "rms": 0.1, "transient": False}
        sub_bass = audio_features.get("sub_bass", 0.1)

        # =========================================================================
        # ACT I: THE SIGNAL INTERRUPT & THE CALL (00:00 – 00:45)
        # =========================================================================
        if t < 3.5:
            # Shot 1: Initial Bharat Darpan CRT raster and spinning logo
            doordarshan_alert.draw_bharat_darpan_logo(frame, width // 2, int(height * 0.35), radius=int(height * 0.12), t=t)
            text_overlay.draw_text(frame, "ভারত দর্পণ কেন্দ্র কলকাতা", (width // 2, int(height * 0.62)),
                                   font_size=int(height * 0.038), fill_color=(245, 205, 55), anchor="mm")
            text_overlay.draw_text(frame, "সত্যম শিবম সুন্দরম", (width // 2, int(height * 0.70)),
                                   font_size=int(height * 0.030), fill_color=(212, 175, 55), anchor="mm")

        elif 3.5 <= t < 6.5:
            # Shot 2: Macro zoom into corrupted eye with pupil twitch
            st = t - 3.5
            frame[:, :] = [18, 15, 48]
            doordarshan_alert.draw_bharat_darpan_logo(frame, width // 2, height // 2,
                                                    radius=int(height * 0.18 + st * 15), t=t,
                                                    pupil_twitch=True, red_scanlines=0.45)

        elif 6.5 <= t < 10.0:
            # Shot 3: Blood-red emergency broadcast banner
            frame[:, :] = [18, 15, 48]
            doordarshan_alert.draw_bharat_darpan_logo(frame, width // 2, int(height * 0.20), radius=int(height * 0.08), t=t)
            text_overlay.draw_emergency_banner(
                frame,
                "ভারত দর্পণ বিশেষ জরুরি সম্প্রচার — পশ্চিমবঙ্গ বিপর্যয় মোকাবিলা",
                "[ BHARAT DARPAN BROADCAST  •  CODE: 94/NISHIDAK  •  SECTOR: WB ]",
                y_center=int(height * 0.44)
            )
            text_overlay.draw_text(
                frame, "অধিক্ষেত্র: নিস্তব্ধপুর ও তৎসংলগ্ন জনহীন প্রান্তর",
                (int(width * 0.10), int(height * 0.60)), font_size=int(height * 0.034), fill_color=(94, 220, 120)
            )
            text_overlay.draw_text(
                frame, "[ JURISDICTION: NISTOBDHOPUR  •  THREAT LEVEL: IV ]",
                (int(width * 0.10), int(height * 0.65)), font_size=int(height * 0.024), fill_color=(190, 215, 190)
            )

        elif 10.0 <= t < 13.0:
            # Shot 4: Macro B-Roll — Rusty Door Latch (Chhitkini) rattling
            st = t - 10.0
            frame[:] = zoom_pan(self.get_plate("door_latch", width, height), st, 3.0, 1.0, 1.08)
            jitter = int(math.sin(t * 32.0) * (3.0 if sub_bass > 0.2 else 1.0))
            if jitter != 0:
                frame[:] = np.roll(frame, jitter, axis=0)

        elif 13.0 <= t < 15.5:
            # Shot 5: Silent Film Intertitle 1
            st = t - 13.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“কে?... কপাটে কে আঘাত করিতেছে?”", "[ Who is knocking at the door? ]", t=st
            )

        elif 15.5 <= t < 18.5:
            # Shot 6: Macro B-Roll — Misty Bamboo Grove
            st = t - 15.5
            frame[:] = zoom_pan(self.get_plate("bamboo_mist", width, height), st, 3.0, 1.0, 1.07, pan_x=-15)

        elif 18.5 <= t < 21.0:
            # Shot 7: Silent Film Intertitle 2
            st = t - 18.5
            text_overlay.draw_silent_film_intertitle(
                frame, "“কপাট খুলিবেন না। উহা আপনার মাতা নহে।”", "[ Do not open. That is not your mother. ]", t=st
            )

        elif 21.0 <= t < 25.5:
            # Shot 8: Solitary Farmhouse in Moonlit Plain
            st = t - 21.0
            frame[:] = zoom_pan(self.get_plate("homestead", width, height), st, 4.5, 1.0, 1.06)
            banana_trees.draw_banana_tree(frame, int(width * 0.90), height, t, scale=0.9, wind_strength=0.7)

        elif 25.5 <= t < 29.5:
            # Shot 9: Creaking Handpump with Dark Water Drip
            st = t - 25.5
            frame[:] = zoom_pan(self.get_plate("homestead", width, height), st, 4.0, 1.06, 1.10, pan_x=30)
            banana_trees.draw_creaking_handpump(frame, int(width * 0.65), int(height * 0.82), t, scale=1.0)

        elif 29.5 <= t < 34.0:
            # Shot 10: Rule 1 Card
            st = t - 29.5
            frame[:] = self.get_plate("homestead", width, height)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85)
            text_overlay.draw_rule_card(
                frame, "[বিধি ১] (RULE 1)",
                "রাত ১২টার পর কলাবাগান থেকে চেনা কণ্ঠে নিশিডাক শুনলে দরজা খুলবেন না।",
                "DO NOT ANSWER FAMILIAR VOICES CALLING FROM THE BANANA GROVES.",
                y_start=int(height * 0.74)
            )

        elif 34.0 <= t < 37.0:
            # Shot 11: B-Roll — Rotary Telephone Off the Hook
            st = t - 34.0
            frame[:] = zoom_pan(self.get_plate("telephone", width, height), st, 3.0, 1.0, 1.07, pan_y=10)

        elif 37.0 <= t < 40.0:
            # Shot 12: Silent Film Intertitle 3
            st = t - 37.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“টেলিফোন ধরিবার কেহ নাই। সংযোগ বিচ্ছিন্ন।”", "[ There is no one to answer. The line is dead. ]", t=st
            )

        elif 40.0 <= t < 45.0:
            # Shot 13: Emergency Directive Bulletin
            st = t - 40.0
            frame[:, :] = [18, 15, 48]
            doordarshan_alert.draw_doordarshan_logo(frame, width // 2, int(height * 0.22), radius=int(height * 0.08), t=t)
            text_overlay.draw_emergency_banner(
                frame, "জরুরি নির্দেশাবলী — গৃহের অভ্যন্তরে অবস্থান করুন",
                "[ DIRECTIVE: REMAIN INDOORS  •  EXTINGUISH LANTERNS ]", y_center=int(height * 0.45)
            )
            text_overlay.draw_text(
                frame, "১. রাত ১২টার পর পরিচিত কণ্ঠে নিশিডাক আসিলে ভুলেও কপাট খুলিবেন না।",
                (int(width * 0.10), int(height * 0.62)), font_size=int(height * 0.032), fill_color=(240, 240, 240)
            )

        # =========================================================================
        # ACT II: THE MOSQUITO NET METAMORPHOSIS (00:45 – 01:25)
        # =========================================================================
        elif 45.0 <= t < 49.0:
            # Shot 14: Photorealistic AI Bedroom draped in real Mosquito Net
            st = t - 45.0
            frame[:] = zoom_pan(self.get_plate("bedroom", width, height), st, 4.0, 1.0, 1.06)

        elif 49.0 <= t < 52.0:
            # Shot 15: Silent Film Intertitle 4
            st = t - 49.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“মশারি অপসারিত করিবেন না।”", "[ Do not remove the mosquito net. ]", t=st
            )

        elif 52.0 <= t < 56.5:
            # Shot 16: Restless slumber inside the mosquito net
            st = t - 52.0
            frame[:] = zoom_pan(self.get_plate("bedroom", width, height), st, 4.5, 1.06, 1.12, pan_x=-20)
            # Breathing darkness distortion
            frame = distortion.apply_lens_breathing(frame, t, amplitude=0.03)

        elif 56.5 <= t < 61.5:
            # Shot 17: Metamorphosis Begins — Chitin limb eruption on floor
            st = t - 56.5
            frame[:] = self.get_plate("bedroom", width, height)
            bimal_metamorphosis.draw_bimal_metamorphosis(
                frame, t, int(width * 0.50), int(height * 0.70), progress=min(0.6, st / 5.0)
            )

        elif 61.5 <= t < 66.0:
            # Shot 18: Full Stop-Motion 32 Hz Segmentation
            st = t - 61.5
            frame[:] = self.get_plate("bedroom", width, height)
            bimal_metamorphosis.draw_bimal_metamorphosis(
                frame, t, int(width * 0.50), int(height * 0.70), progress=0.85, jitter_hz=32.0
            )

        elif 66.0 <= t < 70.0:
            # Shot 19: Sliding onto Red-Oxide Floor
            st = t - 66.0
            frame[:] = zoom_pan(self.get_plate("bedroom", width, height), st, 4.0, 1.10, 1.15, pan_y=25)
            bimal_metamorphosis.draw_bimal_metamorphosis(
                frame, t, int(width * 0.48), int(height * 0.72), progress=1.0, cataract_glow=1.0
            )

        elif 70.0 <= t < 74.0:
            # Shot 20: Crimson Cataract Eyes
            st = t - 70.0
            frame[:] = self.get_plate("bedroom", width, height)
            bimal_metamorphosis.draw_bimal_metamorphosis(frame, t, int(width * 0.48), int(height * 0.72), progress=1.0)
            text_overlay.draw_text(
                frame, "ত্রিনেত্র প্রস্ফুটিত হইতেছে...",
                (width // 2, int(height * 0.20)), font_size=int(height * 0.034), fill_color=(245, 60, 60), anchor="mm"
            )

        elif 74.0 <= t < 78.5:
            # Shot 21: Rule 2 Card
            st = t - 74.0
            frame[:] = self.get_plate("bedroom", width, height)
            text_overlay.draw_rule_card(
                frame, "[বিধি ২] (RULE 2)",
                "ঘরের মেঝেতে খোলস ও কীটপতঙ্গের পা গজাতে শুরু করলে শান্ত থাকুন।",
                "IF CHITINOUS EXOSKELETON EMERGES: REMAIN FLAT UPON THE RED STONE.",
                y_start=int(height * 0.74)
            )

        elif 78.5 <= t < 81.5:
            # Shot 22: Silent Film Intertitle 5
            st = t - 78.5
            text_overlay.draw_silent_film_intertitle(
                frame, "“আমি মেঝে ছাড়িয়া উঠিতে পারিতেছি না...”", "[ I cannot rise from the floor... ]", t=st
            )

        elif 81.5 <= t < 85.0:
            # Shot 23: Subliminal Flash Montage (0.5s flashes: door latch -> phone -> bed -> eyes)
            st = t - 81.5
            phase = int(st * 4.0) % 4
            if phase == 0:
                frame[:] = self.get_plate("door_latch", width, height)
            elif phase == 1:
                frame[:] = self.get_plate("telephone", width, height)
            elif phase == 2:
                frame[:] = self.get_plate("bedroom", width, height)
            else:
                frame[:] = self.get_plate("cosmic_eye", width, height)
            frame = noise.apply_static_snow(frame, amount=0.35)

        elif 85.0 <= t < 90.0:
            # Shot 24: Bedroom walls shearing into static snow
            st = t - 85.0
            frame[:] = self.get_plate("bedroom", width, height)
            frame = distortion.apply_gravity_warp(frame, t, intensity=0.45)
            frame = noise.apply_static_snow(frame, amount=min(0.8, st / 5.0))

        # =========================================================================
        # ACT III: AFTER MIDNIGHT, SOMEWHERE ELSE — THE ABYSS (01:30 – 02:10)
        # =========================================================================
        elif 90.0 <= t < 96.0:
            # Shot 25: AFTER MIDNIGHT, SOMEWHERE ELSE — OPTICAL SPIRAL ABYSS (First Plunge)
            st = t - 90.0
            frame = cosmic.draw_after_midnight_abyss(frame, st, sub_bass=sub_bass)

        elif 96.0 <= t < 100.0:
            # Shot 26: Teletype Gravitational Warning
            st = t - 96.0
            frame = cosmic.draw_after_midnight_abyss(frame, st + 6.0, sub_bass=sub_bass)
            text_overlay.draw_text(frame, "সতর্কতা: মাধ্যাকর্ষণ বিচ্ছিন্ন হয়েছে।", (width // 2, int(height * 0.15)),
                                   font_size=int(height * 0.038), fill_color=(245, 60, 60), anchor="mm")
            text_overlay.draw_text(frame, "WARNING: GRAVITATIONAL VECTOR DECOUPLED.", (width // 2, int(height * 0.20)),
                                   font_size=int(height * 0.024), fill_color=(220, 220, 220), anchor="mm")

        elif 100.0 <= t < 103.5:
            # Shot 27: Silent Film Intertitle 6
            st = t - 100.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“নিশিডাক দ্বিতীয়বার উচ্চারিত হইল।”", "[ The Nishidak called for the second time. ]", t=st
            )

        elif 103.5 <= t < 107.0:
            # Shot 28: Macro B-Roll — Door Latch violently shaking
            st = t - 103.5
            frame[:] = zoom_pan(self.get_plate("door_latch", width, height), st, 3.5, 1.08, 1.15)
            frame = vhs.apply_vhs_tracking(frame, t, tear_strength=0.55, sub_bass=sub_bass)

        elif 107.0 <= t < 110.5:
            # Shot 29: Silent Film Intertitle 7
            st = t - 107.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“কদাচ কপাট খুলিবেন না। উহা প্রবেশ করিতে পারিবে না।”",
                "[ Never open the door. It cannot enter without consent. ]", t=st
            )

        elif 110.5 <= t < 118.0:
            # Shot 30: AFTER MIDNIGHT, SOMEWHERE ELSE — THE INFINITE ABYSS (Deepening Acceleration)
            st = t - 110.5
            frame = cosmic.draw_after_midnight_abyss(frame, st * 1.35, sub_bass=max(0.4, sub_bass))
            frame = distortion.apply_gravity_warp(frame, t, intensity=0.5)

        elif 118.0 <= t < 123.0:
            # Shot 31: Silent Film Intertitle 8
            st = t - 118.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“আপনি অতলে তলাইয়া যাইতেছেন... মধ্যরাতের পর, অন্য কোথাও...”",
                "[ You are plunging into the abyss... After Midnight, Somewhere Else... ]", t=st
            )

        # =========================================================================
        # ACT IV: THE UNCANNY FELINE & TANTRIC COSMIC EYE (02:03 – 02:45)
        # =========================================================================
        elif 123.0 <= t < 128.0:
            # Shot 32: Return to Homestead Exterior with Black Tomcat on Bamboo Rail
            st = t - 123.0
            frame[:] = self.get_plate("homestead", width, height)
            hulo_cat.draw_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.0)

        elif 128.0 <= t < 132.5:
            # Shot 33: Rule 3 Card
            st = t - 128.0
            frame[:] = self.get_plate("homestead", width, height)
            hulo_cat.draw_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.0)
            text_overlay.draw_rule_card(
                frame, "[বিধি ৩] (RULE 3)",
                "বাঁশের বেড়ায় বসা হুলো বেড়ালের চোখের দিকে তাকাবেন না।",
                "DO NOT GAZE INTO THE EYES OF THE TOMCAT UPON THE BAMBOO RAIL.",
                y_start=int(height * 0.74)
            )

        elif 132.5 <= t < 137.0:
            # Shot 34: The Tomcat Neck Stretching into the Night Sky
            st = t - 132.5
            frame[:] = self.get_plate("homestead", width, height)
            stretch = min(1.0, st / 4.0)
            hulo_cat.draw_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=stretch)

        elif 137.0 <= t < 141.0:
            # Shot 35: Extreme Close-up of Glowing Sulfur Eyes
            st = t - 137.0
            frame[:] = zoom_pan(self.get_plate("homestead", width, height), st, 4.0, 1.25, 1.35, pan_x=30, pan_y=-30)
            hulo_cat.draw_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=1.0)

        elif 141.0 <= t < 144.5:
            # Shot 36: Silent Film Intertitle 9
            st = t - 141.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“উহার গ্রীবা আকাশ স্পর্শ করিয়াছে। উহা সংকেত প্রেরণ করিতেছে।”",
                "[ Its neck has touched the heavens. It is transmitting. ]", t=st
            )

        elif 144.5 <= t < 149.0:
            # Shot 37: Low Monsoon Clouds Tearing Open
            st = t - 144.5
            frame[:] = zoom_pan(self.get_plate("cosmic_eye", width, height), st, 4.5, 1.0, 1.08)
            banana_trees.draw_banana_tree(frame, int(width * 0.08), height, t, scale=0.8, wind_strength=0.5)
            banana_trees.draw_banana_tree(frame, int(width * 0.92), height, t, scale=0.8, wind_strength=0.5)

        elif 149.0 <= t < 156.0:
            # Shot 38: TRINETRA — The Colossal Third Eye in the Heavens
            st = t - 149.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            trinetra_eye.draw_trinetra_eye(frame, width // 2, int(height * 0.44), t, scale=1.1, dilation_extra=sub_bass)
            banana_trees.draw_banana_tree(frame, int(width * 0.08), height, t, scale=0.8)
            banana_trees.draw_banana_tree(frame, int(width * 0.92), height, t, scale=0.8)

        elif 156.0 <= t < 160.0:
            # Shot 39: Silent Film Intertitle 10
            st = t - 156.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“আকাশের রক্তিম নয়নের দিকে তাকাবেন না।”",
                "[ Do not look upon the Celestial Eye in the heavens. ]", t=st
            )

        elif 160.0 <= t < 165.0:
            # Shot 40: Cosmic Eye Pupil Dilating & Threatening to Swallow the Stars
            st = t - 160.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            dilation = min(1.0, st / 4.0) + sub_bass * 0.4
            trinetra_eye.draw_trinetra_eye(frame, width // 2, int(height * 0.44), t, scale=1.25, dilation_extra=dilation)

        elif 165.0 <= t < 169.0:
            # Shot 41: Silent Film Intertitle 11
            st = t - 165.0
            text_overlay.draw_silent_film_intertitle(
                frame, "“নয়নটি আপনাকে বহু পূর্বেই প্রত্যক্ষ করিয়াছে।”",
                "[ The Eye has witnessed you long before tonight. ]", t=st
            )

        elif 169.0 <= t < 173.0:
            # Shot 42: Final Bharat Darpan CRT Terminal Decree
            st = t - 169.0
            frame[:, :] = [18, 15, 48]
            doordarshan_alert.draw_bharat_darpan_logo(frame, width // 2, int(height * 0.22), radius=int(height * 0.08), t=t)
            text_overlay.draw_emergency_banner(
                frame, "ভারত দর্পণ সম্প্রচার অনির্দিষ্টকালের জন্য স্থগিত",
                "[ BHARAT DARPAN TRANSMISSION  •  SECTOR WB ]", y_center=int(height * 0.45)
            )
            text_overlay.draw_text(
                frame, "এই জরুরি সম্প্রচার নিরবচ্ছিন্নভাবে চলিবে। কপাট খুলিবেন না।",
                (width // 2, int(height * 0.65)), font_size=int(height * 0.032), fill_color=(240, 240, 240), anchor="mm"
            )

        # =========================================================================
        # ACT V: CATHODE COLLAPSE & TOTAL BLACKOUT (02:53 – 03:00)
        # =========================================================================
        elif 173.0 <= t < 175.5:
            # Shot 43: Subliminal Flash Cadence before Severance
            st = t - 173.0
            phase = int(st * 6.0) % 4
            if phase == 0:
                frame[:] = self.get_plate("door_latch", width, height)
            elif phase == 1:
                frame[:] = self.get_plate("bedroom", width, height)
            elif phase == 2:
                frame = cosmic.draw_after_midnight_abyss(frame, st * 2.0, sub_bass=0.6)
            else:
                frame[:] = self.get_plate("cosmic_eye", width, height)
            frame = noise.apply_static_snow(frame, amount=0.55)

        elif 175.5 <= t < 177.0:
            # Shot 44: Inverted Red-and-Black Bharat Darpan Logo (12 frames)
            frame[:, :] = [178, 24, 24]
            doordarshan_alert.draw_bharat_darpan_logo(
                frame, width // 2, height // 2, radius=int(height * 0.14), t=t, red_scanlines=1.0
            )

        elif 177.0 <= t < 178.5:
            # Shot 45: Horizontal Cathode Line Collapse
            st = t - 177.0
            frame[:, :] = [4, 4, 6]
            line_w = int(width * max(0.04, 1.0 - (st / 1.5)))
            cv2.line(frame, (width // 2 - line_w // 2, height // 2),
                     (width // 2 + line_w // 2, height // 2), (240, 240, 235), 2)

        elif 178.5 <= t < 179.3:
            # Shot 46: Phosphor Dot Pinch Decay
            st = t - 178.5
            frame[:, :] = [4, 4, 6]
            dot_r = max(1, int(4 * (1.0 - (st / 0.8))))
            cv2.circle(frame, (width // 2, height // 2), dot_r, (120, 240, 140), -1)

        else:
            # Shot 47: Absolute Blackout
            frame[:, :] = [4, 4, 6]

        # =========================================================================
        # UNIFIED CRT & VHS POST-PROCESSING PIPELINE
        # =========================================================================
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
