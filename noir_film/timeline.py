"""
Master Timeline Compositor for Project NOIR / Nishidak.
Coordinates all 7 narrative movements (180 seconds) with audio reactivity and CRT/VHS shaders.
"""
import os
import math
import cv2
import numpy as np

from .utils.config_loader import load_global_config, load_scene_config
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


class NoirTimeline:
    """Master scene coordinator for the 180s analog horror film."""
    def __init__(self, global_config: dict = None):
        self.cfg = global_config or load_global_config()
        self.plates = {}
        self._load_plates()

    def _load_plates(self):
        plates_dir = os.path.join(ROOT, "plates")
        mapping = {
            "homestead": "bengal_courage_homestead.jpg",
            "bedroom": "moshari_bedroom_realistic.jpg",
            "cosmic_eye": "bengal_cosmic_eye.jpg",
            "door_latch": "rustic_door_latch.jpg",
            "bamboo_mist": "bamboo_grove_mist.jpg",
            "telephone": "telephone_off_hook.jpg"
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
        """Renders the master frame at timestamp t."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        audio_features = audio_features or {"sub_bass": 0.1, "rms": 0.1, "transient": False}
        sub_bass = audio_features.get("sub_bass", 0.1)

        # SCENE 1: ACT_01_DD_INTERRUPT (00:00 - 00:15)
        if t < 15.0:
            scene_cfg = load_scene_config(1).get("parameters", {})
            frame = doordarshan_alert.render_scene_01(frame, t, scene_cfg)

        # SCENE 2: ACT_02_HOMESTEAD_BANANA (00:15 - 00:35)
        elif 15.0 <= t < 35.0:
            st = t - 15.0
            base = self.get_plate("homestead", width, height)
            # 1.0x to 1.15x slow camera push-in
            zoom = 1.0 + (st / 20.0) * 0.15
            M = cv2.getRotationMatrix2D((width * 0.5, height * 0.5), 0, zoom)
            frame[:] = cv2.warpAffine(base, M, (width, height))

            # Foreground banana trees & creaking handpump
            banana_trees.draw_banana_tree(frame, int(width * 0.84), height, t, scale=1.0, wind_strength=0.7)
            banana_trees.draw_creaking_handpump(frame, int(width * 0.72), int(height * 0.88), t, scale=0.85)

            # Rule 1 display at t >= 22.0
            if t >= 22.0:
                text_overlay.draw_rule_card(
                    frame,
                    "[বিধি ১] (RULE 1)",
                    "রাত ১২টার পর কলাবাগান থেকে চেনা কণ্ঠে নিশিডাক শুনলে দরজা খুলবেন না।",
                    "DO NOT ANSWER FAMILIAR VOICES CALLING FROM THE BANANA GROVES.",
                    y_start=int(height * 0.76)
                )

        # SCENE 3: ACT_03_KAFKA_BEDROOM (00:35 - 01:05)
        elif 35.0 <= t < 65.0:
            st = t - 35.0
            frame[:] = self.get_plate("bedroom", width, height)

            # Bimal Metamorphosis on the floor (starts at t=42.0)
            if t >= 42.0:
                progress = min(1.0, (t - 42.0) / 16.0)
                bimal_metamorphosis.draw_bimal_metamorphosis(frame, t, int(width * 0.50), int(height * 0.70), progress=progress)

            # Rule 2 display at t >= 48.0
            if t >= 48.0:
                text_overlay.draw_rule_card(
                    frame,
                    "[বিধি ২] (RULE 2)",
                    "ঘরের মেঝেতে খোলস ও কীটপতঙ্গের পা গজাতে শুরু করলে শান্ত থাকুন।",
                    "IF CHITINOUS EXOSKELETON EMERGES: REMAIN FLAT UPON THE RED STONE.",
                    y_start=int(height * 0.76)
                )

        # SCENE 4: ACT_04_ABYSS_ALARM (01:05 - 01:35)
        elif 65.0 <= t < 95.0:
            st = t - 65.0
            frame = cosmic.draw_twilight_zone_abyss(frame, st, sub_bass=sub_bass)
            if sub_bass > 0.35:
                frame = distortion.apply_gravity_warp(frame, t, intensity=sub_bass * 0.6)

            # Frantic warning teletype at t >= 72.0
            if t >= 72.0:
                text_overlay.draw_text(frame, "সতর্কতা: মাধ্যাকর্ষণ বিচ্ছিন্ন হয়েছে।", (width // 2, 70),
                                       font_size=24, fill_color=(245, 60, 60), anchor="mm")
                text_overlay.draw_text(frame, "WARNING: GRAVITATIONAL VECTOR DECOUPLED.", (width // 2, 102),
                                       font_size=16, fill_color=(200, 200, 200), anchor="mm")

        # SCENE 5: ACT_05_HULO_CAT_NECK (01:35 - 02:05)
        elif 95.0 <= t < 125.0:
            st = t - 95.0
            frame[:] = self.get_plate("homestead", width, height)
            # Neck stretch starts at t=102.0
            stretch = min(1.0, max(0.0, (t - 102.0) / 18.0))
            hulo_cat.draw_hulo_cat(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=stretch)

            # Rule 3 display at t >= 106.0
            if t >= 106.0:
                text_overlay.draw_rule_card(
                    frame,
                    "[বিধি ৩] (RULE 3)",
                    "বাঁশের বেড়ায় বসা হুলো বেড়ালের চোখের দিকে তাকাবেন না।",
                    "DO NOT GAZE INTO THE EYES OF THE TOMCAT UPON THE BAMBOO RAIL.",
                    y_start=int(height * 0.76)
                )

        # SCENE 6: ACT_06_TRINETRA_COSMIC (02:05 - 02:45)
        elif 125.0 <= t < 165.0:
            st = t - 125.0
            frame[:] = self.get_plate("cosmic_eye", width, height)
            trinetra_eye.draw_trinetra_eye(frame, width // 2, int(height * 0.44), t, scale=1.1, dilation_extra=sub_bass)
            banana_trees.draw_banana_tree(frame, int(width * 0.08), height, t, scale=0.8, wind_strength=0.5)
            banana_trees.draw_banana_tree(frame, int(width * 0.92), height, t, scale=0.8, wind_strength=0.5)

            # Final decree reveal at t >= 142.0
            if t >= 142.0:
                text_overlay.draw_text(frame, "আকাশের রক্তিম নয়নের দিকে তাকাবেন না।", (width // 2, int(height * 0.74)),
                                       font_size=24, fill_color=(245, 60, 60), anchor="mm")
                text_overlay.draw_text(frame, "DO NOT LOOK UPON THE CELESTIAL EYE IN THE HEAVENS.", (width // 2, int(height * 0.78)),
                                       font_size=15, fill_color=(210, 210, 210), anchor="mm")
                text_overlay.draw_text(frame, "নয়নটি আপনাকে বহু পূর্বেই দেখে ফেলেছে।", (width // 2, int(height * 0.83)),
                                       font_size=24, fill_color=(245, 205, 55), anchor="mm")
                text_overlay.draw_text(frame, "সম্প্রচার সমাপ্ত হবে না।", (width // 2, int(height * 0.88)),
                                       font_size=28, fill_color=(245, 40, 40), anchor="mm")

        # SCENE 7: ACT_07_CATHODE_COLLAPSE (02:45 - 03:00)
        else:
            st = t - 165.0
            if st < 3.5:
                # White static sweep
                frame = noise.apply_static_snow(frame, amount=0.85)
            elif 3.5 <= st < 4.0:
                # 12 frames of inverted red logo
                frame[:, :] = [178, 24, 24]
                doordarshan_alert.draw_doordarshan_logo(frame, width // 2, height // 2, radius=55, t=t, red_scanlines=1.0)
            elif 4.0 <= st < 7.0:
                # Horizontal line collapse
                frame[:, :] = [4, 4, 6]
                line_w = int(width * max(0.05, 1.0 - (st - 4.0) / 3.0))
                cv2.line(frame, (width // 2 - line_w // 2, height // 2),
                         (width // 2 + line_w // 2, height // 2), (240, 240, 235), 2)
            elif 7.0 <= st < 9.0:
                # Phosphor dot pinch
                frame[:, :] = [4, 4, 6]
                dot_r = max(1, int(4 * (1.0 - (st - 7.0) / 2.0)))
                cv2.circle(frame, (width // 2, height // 2), dot_r, (120, 240, 140), -1)
            else:
                # Total blackout
                frame[:, :] = [4, 4, 6]

        # Post-Processing CRT & VHS Pipeline
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
