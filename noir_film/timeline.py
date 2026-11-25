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
from .actors import descent_fall
from .actors import machinist_stickman
from .actors import v2_director

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_VIDEO_CACHE = {}


def get_video_frame_at(rel_path: str, t: float, width: int, height: int) -> np.ndarray:
    """Loads and loops any MP4 asset in assets/ at 24fps (returned in RGB)."""
    if rel_path not in _VIDEO_CACHE:
        full_path = os.path.join(ROOT, rel_path)
        frames = []
        if os.path.exists(full_path):
            cap = cv2.VideoCapture(full_path)
            while True:
                ret, f = cap.read()
                if not ret or f is None:
                    break
                frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
            cap.release()
        _VIDEO_CACHE[rel_path] = frames

    frames = _VIDEO_CACHE[rel_path]
    if frames:
        idx = int(t * 24.0) % len(frames)
        f = frames[idx]
        if f.shape[1] != width or f.shape[0] != height:
            return cv2.resize(f, (width, height), interpolation=cv2.INTER_AREA)
        return f.copy()
    return None


def get_storm_frame_at(t: float, width: int, height: int) -> np.ndarray:
    """Loads looping Google Flow monsoon storm footage (assets/storm_loop.mp4)."""
    return get_video_frame_at(os.path.join("assets", "storm_loop.mp4"), t, width, height)


def apply_siren_beep_pulse(frame: np.ndarray, t: float, audio_features: dict) -> np.ndarray:
    """Visualizes audio siren/beep transients with subtle crimson strobe edges (clean, zero noisy text)."""
    sub_bass = audio_features.get("sub_bass", 0.1)
    transient = audio_features.get("transient", False)
    if transient or sub_bass > 0.38:
        h, w = frame.shape[:2]
        intensity = min(1.0, (sub_bass - 0.30) * 1.8) if not transient else 0.75
        border = max(3, int(8 * intensity))
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (220, 35, 40), border)
    return frame


def apply_shot_transition(frame: np.ndarray, t: float) -> np.ndarray:
    """
    Applies authentic analog CRT channel-flip static bursts on channel switches
    and smooth phosphor fade-ins/outs on atmospheric scene transitions.
    """
    h, w = frame.shape[:2]

    # Channel-flip cuts (Truman Show channel switching)
    channel_cuts = [6.0, 22.0, 45.0, 90.0, 140.0, 185.0, 204.0, 218.0, 226.0, 236.0, 300.0, 326.0, 338.0, 352.0]
    for c_t in channel_cuts:
        dt = abs(t - c_t)
        if dt < 0.22:
            # Brief CRT horizontal sync roll + static snow burst
            strength = 1.0 - (dt / 0.22)
            shift_y = int(math.sin(t * 95.0) * h * 0.06 * strength)
            if shift_y != 0:
                frame[:] = np.roll(frame, shift_y, axis=0)
            rng = np.random.default_rng(int(t * 1000) % 10000)
            snow = rng.integers(0, 255, (h, w, 3), dtype=np.uint8)
            frame[:] = cv2.addWeighted(frame, 1.0 - 0.55 * strength, snow, 0.55 * strength, 0)
            # Horizontal tracking tear bar
            bar_y = int(((t * 7.0) % 1.0) * h)
            cv2.rectangle(frame, (0, max(0, bar_y - 8)), (w, min(h, bar_y + 8)), (210, 215, 220), -1)
            return frame

    # Smooth phosphor dip-to-dark transitions for atmospheric B-roll cuts
    soft_cuts = [53.0, 60.0, 67.0, 74.0, 80.0, 86.0, 104.0, 154.0, 169.0, 176.0, 193.0, 287.0]
    for s_t in soft_cuts:
        dt = abs(t - s_t)
        if dt < 0.28:
            fade = dt / 0.28
            frame[:] = (frame.astype(np.float32) * (0.25 + 0.75 * fade)).astype(np.uint8)
            return frame

    return frame


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
            "stormy_homestead": "scene-05.jpeg",
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
        if t < 5.0:
            # Shot 0: Opening Fictional & Statutory Disclaimer (5.0s generous reading time)
            v2_director.draw_opening_fictional_disclaimer(frame, width, height)

        elif 5.0 <= t < 9.0:
            # Shot 1: Between the Notes Station ID & Emergency Signal Override
            doordarshan_alert.draw_between_the_notes_logo(frame, width // 2, int(height * 0.32), radius=int(height * 0.12), t=t)
            text_overlay.draw_text(frame, "বিটুইন দ্য নোটস সম্প্রচার কেন্দ্র কলকাতা", (width // 2, int(height * 0.58)),
                                   font_size=int(height * 0.040), fill_color=(245, 205, 55), anchor="mm")
            text_overlay.draw_text(frame, "BETWEEN THE NOTES NETWORK • বিশেষ জরুরি অধিবেশন", (width // 2, int(height * 0.66)),
                                   font_size=int(height * 0.026), fill_color=(212, 175, 55), anchor="mm")
            text_overlay.draw_text(frame, "নিস্তব্ধপুর গ্রামীণ এলাকা থেকে সরাসরি সম্প্রচার", (width // 2, int(height * 0.73)),
                                   font_size=int(height * 0.022), fill_color=(180, 215, 180), anchor="mm")
            v2_director.draw_crimson_point(frame, t, cx=int(width * 0.94), cy=int(height * 0.075), radius=4)

        elif 9.0 <= t < 14.0:
            # Shot 2: CH 03 Bengal Geography / BTN 24 News Broadcast (5.0s - Clean V2 Geography or Storm Loop)
            st = t - 9.0
            geo_f = get_video_frame_at(os.path.join("assets", "v2_videos", "V2_01_bengal_geography.mp4"), st, width, height)
            storm_f = get_storm_frame_at(t, width, height)
            if geo_f is not None:
                frame[:] = geo_f
            elif storm_f is not None:
                frame[:] = storm_f
            else:
                frame[:] = zoom_pan(self.get_plate("stormy_homestead", width, height), st, 8.0, 1.0, 1.05)
            frame = news_broadcast.draw_corrupted_news_overlay(
                frame, t=t,
                headline="গ্রামের জঙ্গল রহস্য, জেলায় ছড়াল আতঙ্ক",
                sub_headline="বাঁশবনে অদ্ভুত শব্দ, এলাকায় চাঞ্চল্য",
                ticker_text="বিটুইন দ্য নোটস বিশেষ সতর্কবার্তা  |  নিস্তব্ধপুরে সান্ধ্য আইন জারি  |  বাঁশবনে আলো জ্বালাবেন না  |  অচেনা কণ্ঠে সাড়া নিষেধ  |  Between the Notes এক্সক্লুসিভ লাইভ",
                sector_code="রাত ৩:১২ | ০০০৩",
                clock_str="03:12 AM",
                weather_str="24°C",
                channel_name="Between the Notes",
                signal_integrity=98,
                is_recorded=False,
                globe_corrupted=False
            )
            v2_director.draw_crimson_point(frame, t, cx=int(width * 0.94), cy=int(height * 0.075), radius=4)

        elif 14.0 <= t < 22.0:
            # Shot 3: Upgraded Between the Notes TV News Broadcast (Corrupted Storm Loop)
            st = t - 14.0
            storm_f = get_storm_frame_at(t, width, height)
            frame[:] = storm_f if storm_f is not None else zoom_pan(self.get_plate("stormy_homestead", width, height), st, 8.0, 1.05, 1.10)
            sig_val = int(np.clip(98 - st * 10, 24, 98))
            frame = news_broadcast.draw_corrupted_news_overlay(
                frame, t=t,
                headline="ওরা দরজার বাইরে দাঁড়িয়ে আছে",
                sub_headline="নিশিডাক শুনলে ঘরের দরজা বন্ধ রাখুন, কোনো সাড়া দেবেন না",
                ticker_text="জরুরি অবস্থা  |  সিগন্যাল ড্রপ  |  কোথাও যাবেন না  |  টিভির পর্দায় চোখ রাখবেন না  |  Between the Notes সতর্কতা জারি",
                sector_code="রাত ৩:১২ | ০০০৩",
                clock_str="03:12 AM",
                weather_str="24°C",
                channel_name="Between the Notes",
                signal_integrity=sig_val,
                is_recorded=(st >= 2.5),  # Flips to RECORDED
                globe_corrupted=True      # Globe morphs into staring dilated pupil
            )

        elif 22.0 <= t < 29.0:
            # Shot 4: V2 Vintage Cartographic Contradiction (22-25.5s) -> Glowing Red CRT Sector Radar Map (25.5-29s)
            st = t - 22.0
            if st < 3.5:
                v2_director.draw_vintage_map_contradiction(frame, t, st, width, height)
                v2_director.draw_channel_hud(frame, "CH 03 // CARTOGRAPHY", t, color=(235, 200, 90))
            else:
                frame = sector_map.draw_sector_radar_map(frame, t=t, sub_bass=sub_bass)
                v2_director.draw_crimson_point(frame, t)

        elif 29.0 <= t < 37.0:
            # Shot 5: Saturated Blood-Red Civil Danger Screen (8.0s - Emergency Broadcast)
            frame = civil_danger.draw_civil_danger_screen(frame, t=t, sub_bass=sub_bass)
            v2_director.draw_channel_hud(frame, "CH 09 // EMERGENCY INFO", t, color=(255, 195, 195))

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
            # Shot 8: V2 Locked-Off Ordinary Black Cat on Bamboo Fence (Shadow Slowly Turns Head)
            st = t - 45.0
            cat_f = get_video_frame_at(os.path.join("assets", "v2_videos", "V2_02_cat_shadow_turn.mp4"), st, width, height)
            if cat_f is not None:
                frame[:] = cat_f
            else:
                v2_director.draw_cat_shadow_turn_scene(frame, t, st, width, height)
            v2_director.draw_channel_hud(frame, "CH 03 // FIELD CAM", t, color=(90, 235, 120), sub_label="NISTOBDHOPUR")

        elif 53.0 <= t < 60.0:
            # Shot 9: Rule 1 Civil Defense Card + Walking & Smoking Machinist Stick-Man + Cancer Warning
            st = t - 53.0
            base_plate = self.get_plate("homestead", width, height)
            frame[:] = cloud_timelapse.composite_sky_timelapse_on_plate(base_plate, t, sky_cutoff=0.44)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85)
            walk_x = int(width * (0.28 + st * 0.022))
            machinist_stickman.draw_machinist_stickman(
                frame, walk_x, int(height * 0.72), t, scale=1.05,
                walk_phase=st * 3.2, is_alert=(sub_bass > 0.30), smoking=True
            )
            v2_director.draw_smoking_cancer_warning(frame, width, height)
            text_overlay.draw_rule_card(
                frame, "[বিধি ১] (RULE 1)",
                "রাত বারোটার পর কলাবাগান থেকে চেনা গলায় ডাকলেও দরজা খুলবেন না।",
                "DO NOT OPEN THE DOOR IF FAMILIAR VOICES CALL FROM THE BANANA TREES AFTER MIDNIGHT.",
                y_start=int(height * 0.70)
            )

        elif 60.0 <= t < 67.0:
            # Shot 10: 1:00 - 1:07 MARK - Google Flow Drone Aerial Angle + Tube-Well Black Oil Close-Up
            st = t - 60.0
            if st < 3.5:
                # Angle 1: Google Flow Drone Aerial Sweep over Courtyard & Tube-Well + Machinist Stick-Man
                drone_f = get_video_frame_at(os.path.join("assets", "flow_drone_courtyard.mp4"), st, width, height)
                frame[:] = drone_f if drone_f is not None else zoom_pan(self.get_plate("aerial_crossroads", width, height), st, 3.5, 1.0, 1.12)
                machinist_stickman.draw_machinist_stickman(frame, int(width * 0.32), int(height * 0.68), t, scale=0.85, walk_phase=st * 3.0, is_alert=True)
                loc_str = "22.9868° N, 87.8550° E" if 1.2 <= st < 2.7 else "LOCATION: NISTOBDHOPUR"
                v2_director.draw_channel_hud(frame, "CH 03 // FIELD CAM", t, color=(90, 235, 120), sub_label=loc_str)
            else:
                # Angle 2: Google Flow Close-Up Facing Tube-Well Dripping Thick Black Oil
                pump_f = get_video_frame_at(os.path.join("assets", "flow_closeup_tubewell.mp4"), st - 3.5, width, height)
                if pump_f is not None:
                    frame[:] = pump_f
                else:
                    frame[:] = zoom_pan(self.get_plate("rusted_handpump", width, height), st - 3.5, 3.5, 1.0, 1.08)
                    tubewell_scene.draw_oil_drip_closeup(frame, t, width, height)
                v2_director.draw_channel_hud(frame, "CAM 02 // TUBE-WELL CLOSE-UP", t, color=(245, 70, 70))

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
            # Shot 15: CH 07 // BEDROOM CAM - Awakening to Nishir Daak + Passing Bike Headlight Through Window
            st = t - 90.0
            frame[:] = zoom_pan(self.get_plate("bedroom", width, height), st, 7.0, 1.0, 1.06)
            gs_f = get_video_frame_at(os.path.join("assets", "v2_videos", "bike_headlight_greenscreen.mp4"), st, width, height)
            v2_director.draw_passing_bike_window_light(frame, t, width, height, gs_frame=gs_f)
            text_overlay.draw_text(frame, "CH 07 // BEDROOM CAM", (int(width * 0.04), int(height * 0.08)),
                                   font_size=int(height * 0.024), fill_color=(245, 70, 70), anchor="lm")

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
            # Shot 17: 1:49 MARK - TIGHTLY ENCLOSED MOSQUITO NET + Passing Bike Headlight
            st = t - 104.0
            frame[:] = zoom_pan(self.get_plate("bedroom", width, height), st, 8.0, 1.0, 1.06)
            gs_f = get_video_frame_at(os.path.join("assets", "v2_videos", "bike_headlight_greenscreen.mp4"), st, width, height)
            v2_director.draw_passing_bike_window_light(frame, t, width, height, gs_frame=gs_f)
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
        # ACT IV: HYPER-OBJECTS ON OTHER CHANNELS (02:20 - 03:05)
        # =========================================================================
        elif 140.0 <= t < 147.0:
            # Shot 22: CH 03 // FIELD CAM - Hyper-Object Figure perched on Locked-off Fence + Sky Time-Lapse
            st = t - 140.0
            base_plate = self.get_plate("homestead", width, height)
            frame[:] = cloud_timelapse.composite_sky_timelapse_on_plate(base_plate, t, sky_cutoff=0.44)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85)
            hulo_cat.draw_shadowy_figure(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.0)
            text_overlay.draw_text(frame, "CH 03 // FIELD CAM", (int(w := width) * 0.04, int(height * 0.08)),
                                   font_size=int(height * 0.024), fill_color=(90, 235, 120), anchor="lm")

        elif 147.0 <= t < 154.0:
            # Shot 23: Rule 3 Civil Defense Card (7.0s - Locked-off Sky Time-Lapse)
            st = t - 147.0
            base_plate = self.get_plate("homestead", width, height)
            frame[:] = cloud_timelapse.composite_sky_timelapse_on_plate(base_plate, t, sky_cutoff=0.44)
            banana_trees.draw_banana_tree(frame, int(width * 0.88), height, t, scale=0.85)
            hulo_cat.draw_shadowy_figure(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.0)
            text_overlay.draw_rule_card(
                frame, "[বিধি ৩] (RULE 3)",
                "বাঁশের বেড়ায় বসে থাকা ছায়ার চোখের দিকে একদম তাকাবেন না।",
                "DO NOT LOOK INTO THE EYES OF THE SHADOW PERCHED ON THE FENCE.",
                y_start=int(height * 0.70)
            )

        elif 154.0 <= t < 162.0:
            # Shot 24: 2:33 MARK - COURAGE-STYLE TWILIGHT VEGETATION, GIANT MOON & ELONGATING HYPER-OBJECT
            st = t - 154.0
            stretch = min(1.0, st / 7.0)
            cloud_timelapse.render_cloud_timelapse_sky(frame, t, width, height, cloud_speed=50.0)
            v2_director.draw_courage_nowhere_vegetation(frame, t, width, height, stretch_factor=stretch)
            banana_trees.draw_banana_tree(frame, int(width * 0.90), height, t, scale=0.85, wind_strength=0.7)
            hulo_cat.draw_shadowy_figure(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=stretch)

        elif 162.0 <= t < 169.0:
            # Shot 25: Broadcast Card 6 - Shadowy Entity Intertitle (7.0s)
            st = t - 162.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“ছায়ামূর্তিটা ডাকছে না... আকাশ ওর গলায় আপনার নাম ধরে ডাকছে...”",
                "[ The shadow is not calling you... The sky is using its voice to speak your name... ]", t=st
            )

        elif 169.0 <= t < 176.0:
            # Shot 26: CH 11 Sahaj Path Linocut Yantra Fracturing + Protective Occult Wall (7.0s)
            st = t - 169.0
            if st < 3.5:
                v2_director.draw_sahaj_path_yantra(frame, t, st, width, height, fractured=(st >= 1.5))
                v2_director.draw_channel_hud(frame, "CH 11 // SAHAJ PATH", t, color=(235, 200, 90))
            else:
                frame[:] = zoom_pan(self.get_plate("protective_occult_wall", width, height), st - 3.5, 3.5, 1.0, 1.07)
                v2_director.draw_crimson_point(frame, t)
            text_overlay.draw_text(
                frame, "সুরক্ষা বলয় ভেঙে গেছে",
                (width // 2, int(height * 0.88)), font_size=int(height * 0.034), fill_color=(235, 70, 70), anchor="mm"
            )

        elif 176.0 <= t < 181.0:
            # Shot 27: Aerial Crossroads at 3:00 AM with Swirling Fog (5.0s - Aerial B-Roll)
            st = t - 176.0
            frame[:] = zoom_pan(self.get_plate("aerial_crossroads", width, height), st, 5.0, 1.0, 1.06)

        elif 181.0 <= t < 185.0:
            # Shot 28: Quick Dialogue Countdown (4.0s generous reading time)
            st = t - 181.0
            text_overlay.draw_broadcast_readability_card(
                frame, "“শেষ ডাক আর কিছুক্ষণেই...”", "[ The Final Call is coming... ]", t=st
            )

        # =========================================================================
        # ACT V: DESCENT... - THE BLACK GLUEY META-OBJECT & TRUMAN FALL (03:05 - 03:55)
        # =========================================================================
        elif 185.0 <= t < 193.0:
            # Shot 29: DESCENT... Title Slate (8.0s - High Readability Broadcast Card)
            st = t - 185.0
            text_overlay.draw_broadcast_readability_card(
                frame, "DESCENT...\nবিটুইন দ্য নোটস: মহাকর্ষের পতন",
                "[ EPISODE ZERO: HE WOKE TO THE NISHIR DAAK AND STEPPED INTO THE HOLE ]", t=st
            )

        elif 193.0 <= t < 204.0:
            # Shot 30: Confronting the Black Gluey Hole -> Pulled Spiraling Into the Abyss (11.0s)
            st = t - 193.0
            base_plate = self.get_plate("homestead", width, height)
            frame[:] = cloud_timelapse.composite_sky_timelapse_on_plate(base_plate, t, sky_cutoff=0.44)
            hole_prog = min(1.0, st / 4.0)
            frame = descent_fall.draw_gluey_meta_hole(frame, t, progress=hole_prog, sub_bass=sub_bass)
            hole_cx, hole_cy = width // 2, int(height * 0.66)
            if st < 5.5:
                # Stick-man walks up to the edge and confronts the black hole
                walk_p = min(1.0, st / 4.0)
                sx = int(width * (0.24 + 0.18 * walk_p))
                sy = int(height * 0.70)
                machinist_stickman.draw_machinist_stickman(
                    frame, sx, sy, t, scale=0.95, walk_phase=st * 3.0 if st < 4.0 else 0.0, is_alert=(st >= 3.5)
                )
            else:
                # Gravity fails: pulled into the black hole swirl seamlessly before Shot 31
                pull = min(1.0, (st - 5.5) / 5.2)
                angle = pull * math.pi * 4.5
                rad = (1.0 - pull) * width * 0.14
                sx = int(hole_cx + math.cos(angle) * rad)
                sy = int(hole_cy + math.sin(angle) * rad * 0.45)
                sc = max(0.18, 0.95 * (1.0 - pull * 0.82))
                machinist_stickman.draw_machinist_stickman(
                    frame, sx, sy, t, scale=sc, walk_phase=st * 6.0, is_alert=True
                )
            text_overlay.draw_text(frame, "CH 07 // COURTYARD ANOMALY", (int(width * 0.04), int(height * 0.08)),
                                   font_size=int(height * 0.024), fill_color=(245, 70, 70), anchor="lm")

        elif 204.0 <= t < 218.0:
            # Shot 31: CH 07 // DESCENT CAM - Endless Rotating Fall inside Black Gluey Void (14.0s)
            st = t - 204.0
            abyss_bg = self.get_plate("tumbling_man", width, height)
            frame = descent_fall.draw_rotating_descent(frame, t, st, plate_bg=abyss_bg, sub_bass=sub_bass, show_hud=True)
            frame = distortion.apply_lens_breathing(frame, t, amplitude=0.03)

        elif 218.0 <= t < 226.0:
            # Shot 32: Truman-Show Channel Cut (CH 03 Hyper-object Cat <-> CH 07 Rotating Fall) (8.0s)
            st = t - 218.0
            if int(st / 2.0) % 2 == 0:
                # Cut to CH 03: Hyper-object Cat perched calmly while sky races
                base_plate = self.get_plate("homestead", width, height)
                frame[:] = cloud_timelapse.composite_sky_timelapse_on_plate(base_plate, t, sky_cutoff=0.44)
                hulo_cat.draw_shadowy_figure(frame, t, cx=int(width * 0.52), cy=int(height * 0.68), stretch_factor=0.6)
                text_overlay.draw_text(frame, "CH 03 // FIELD CAM (HYPER-OBJECT)", (int(width * 0.04), int(height * 0.08)),
                                       font_size=int(height * 0.024), fill_color=(90, 235, 120), anchor="lm")
            else:
                # Cut back to CH 07: Bimal still rotating and falling endlessly
                abyss_bg = self.get_plate("tumbling_man", width, height)
                frame = descent_fall.draw_rotating_descent(frame, t, st + 14.0, plate_bg=abyss_bg, sub_bass=sub_bass, show_hud=True)
                text_overlay.draw_text(frame, "সতর্কতা: মাধ্যাকর্ষণ আর কাজ করছে না।", (width // 2, int(height * 0.18)),
                                       font_size=int(height * 0.032), fill_color=(245, 60, 60), anchor="mm")

        elif 226.0 <= t < 235.0:
            # Shot 33: Human Face & Signal Disintegrating into Scanlines while Falling (9.0s)
            st = t - 226.0
            frame[:] = zoom_pan(self.get_plate("scanline_dissolve", width, height), st, 9.0, 1.0, 1.10)
            frame = distortion.apply_gravity_warp(frame, t, intensity=0.35)
            text_overlay.draw_text(frame, "CH 07 // SIGNAL DECOUPLED", (int(width * 0.04), int(height * 0.08)),
                                   font_size=int(height * 0.024), fill_color=(245, 70, 70), anchor="lm")

        # =========================================================================
        # ACT VI: 03:56 CHOKING AWAKENING -> AMNESIA -> EXIT 8 -> TRAIN HONK (03:56 - 06:00)
        # =========================================================================
        elif 236.0 <= t < 256.0:
            # Shot 34 (03:56 - 04:16): Overhead Top-Down View — Choking / Unable to Breathe in Mosquito Net
            st = t - 236.0
            base_net = self.get_plate("net_pov", width, height)
            # Subtle panicked choking camera shake & claustrophobic zoom
            tremor = math.sin(st * 16.0) * 0.015
            frame[:] = zoom_pan(base_net, st, 20.0, 1.0 + tremor, 1.14)
            draw_enclosed_mosquito_net(frame, width, height, t * 2.4)
            machinist_stickman.draw_machinist_stickman(frame, width // 2, int(height * 0.62), t * 1.8, scale=1.35, walk_phase=st * 5.0, is_alert=True)

        elif 256.0 <= t < 280.0:
            # Shot 35 (04:16 - 04:40): Through the Lens of the Protagonist + Passing Bike Headlight
            st = t - 256.0
            frame[:] = zoom_pan(self.get_plate("bedroom", width, height), st, 24.0, 1.02, 1.08)
            gs_f = get_video_frame_at(os.path.join("assets", "v2_videos", "bike_headlight_greenscreen.mp4"), st, width, height)
            v2_director.draw_passing_bike_window_light(frame, t, width, height, gs_frame=gs_f)
            draw_enclosed_mosquito_net(frame, width, height, t)

            # Dreamy half-awake soft-focus blur + heavy eyelid blink vignette
            blur = cv2.GaussianBlur(frame, (15, 15), 0)
            dream_mix = 0.32 + 0.22 * math.sin(st * 1.1)
            frame[:] = cv2.addWeighted(frame, 1.0 - dream_mix, blur, dream_mix, 0)

            blink = 0.0
            for bt in (2.2, 12.0):
                bd = abs(st - bt)
                if bd < 0.75:
                    blink = max(blink, 1.0 - bd / 0.75)
            if blink > 0.05:
                lid_h = int((height * 0.48) * blink)
                cv2.rectangle(frame, (0, 0), (width, lid_h), (4, 4, 6), -1)
                cv2.rectangle(frame, (0, height - lid_h), (width, height), (4, 4, 6), -1)

            if st < 7.0:
                cv2.rectangle(frame, (int(width * 0.25), int(height * 0.81)), (int(width * 0.75), int(height * 0.91)), (8, 10, 12), -1)
                cv2.rectangle(frame, (int(width * 0.25), int(height * 0.81)), (int(width * 0.75), int(height * 0.91)), (212, 175, 72), 1)
                text_overlay.draw_text(
                    frame, "আমি... আমি কোথায়?...",
                    (width // 2, int(height * 0.86)),
                    font_size=int(height * 0.036), fill_color=(250, 248, 236), anchor="mm"
                )

        elif 280.0 <= t < 300.0:
            # Shot 36 (04:40 - 05:00): Retrograde Amnesia -> CRT False Ending Collapse -> 04:58 Snap Open
            st = t - 280.0
            frame[:] = zoom_pan(self.get_plate("door_latch", width, height), st, 20.0, 1.0, 1.18)
            v2_director.draw_crt_collapse_open(frame, t, st, width, height)

        elif 300.0 <= t < 322.0:
            # Shot 37 (05:00 - 05:22): Hard Cut to Sterile Exit 8 Corridor + EXIT 0 Signage
            st = t - 300.0
            exit8_f = get_video_frame_at(os.path.join("assets", "stage2_videos", "S2_02_exit8_matrix_corridor.mp4"), st, width, height)
            frame[:] = exit8_f if exit8_f is not None else self.get_plate("aerial_crossroads", width, height)
            v2_director.draw_exit0_hud(frame, t, width, height, show_anomaly_card=False)

        elif 322.0 <= t < 338.0:
            # Shot 38 (05:22 - 05:38): Berlin Metro x Matrix Platform + Pale Businessman in Dark Suit
            st = t - 322.0
            biz_f = get_video_frame_at(os.path.join("assets", "v2_videos", "V2_03_berlin_businessman.mp4"), st, width, height)
            metro_f = get_video_frame_at(os.path.join("assets", "stage2_videos", "S2_01_berlin_matrix_subway.mp4"), st, width, height)
            if st >= 8.0 and biz_f is not None:
                frame[:] = biz_f
            elif metro_f is not None:
                frame[:] = metro_f
            else:
                frame[:] = self.get_plate("aerial_crossroads", width, height)
            v2_director.draw_exit0_hud(frame, t, width, height, show_anomaly_card=False)

        elif 338.0 <= t < 352.0:
            # Shot 39 (05:38 - 05:52): 05:38 TRAIN HONK -> Brief 3.5s Warm-Sepia Dream Flash, then Cold Berlin Subway
            st = t - 338.0
            metro_f = get_video_frame_at(os.path.join("assets", "stage2_videos", "S2_01_berlin_matrix_subway.mp4"), st + 12.0, width, height)
            if st < 3.5:
                # Brief warm old-day dream flash (3.5s max)
                train_f = get_video_frame_at(os.path.join("assets", "haunted_archive_videos", "F_pather_train_never_arrives.mp4"), st, width, height)
                if train_f is not None:
                    # Warm golden-sepia dream tint ("warm old day")
                    warm = train_f.astype(np.float32)
                    warm[:, :, 0] = np.clip(warm[:, :, 0] * 1.15 + 14, 0, 255)
                    warm[:, :, 1] = np.clip(warm[:, :, 1] * 1.04 + 6, 0, 255)
                    warm[:, :, 2] = np.clip(warm[:, :, 2] * 0.82, 0, 255)
                    warm_u8 = warm.astype(np.uint8)
                    frame[:] = cv2.addWeighted(metro_f, 0.30, warm_u8, 0.70, 0) if metro_f is not None else warm_u8
                elif metro_f is not None:
                    frame[:] = metro_f
            else:
                frame[:] = metro_f if metro_f is not None else self.get_plate("aerial_crossroads", width, height)
            v2_director.draw_crimson_point(frame, t, cx=int(width * 0.94), cy=int(height * 0.075), radius=4)

        else:
            # Shot 40 (05:52 - 06:00): Goofy Sci-Fi Creature + First Anomaly Prompt
            st = t - 352.0
            creat_f = get_video_frame_at(os.path.join("assets", "stage2_videos", "S2_03_goofy_scifi_creature.mp4"), st, width, height)
            frame[:] = creat_f if creat_f is not None else self.get_plate("cosmic_eye", width, height)
            v2_director.draw_exit0_hud(frame, t, width, height, show_anomaly_card=(st >= 4.0))

        # Apply siren/beep reactive visual pulses + analog CRT channel-switch bursts
        frame = apply_siren_beep_pulse(frame, t, audio_features)
        frame = apply_shot_transition(frame, t)

        # =========================================================================
        # UNIFIED CRT & VHS POST-PROCESSING PIPELINE
        # =========================================================================
        # Check if frame is a high-readability text card, rule card, slate, or credits
        is_text_card = (
            (t < 9.0) or
            (37.0 <= t < 45.0) or
            (53.0 <= t < 60.0) or
            (74.0 <= t < 80.0) or
            (97.0 <= t < 104.0) or
            (112.0 <= t < 117.0) or
            (125.0 <= t < 129.0) or
            (132.0 <= t < 140.0) or
            (147.0 <= t < 154.0) or
            (162.0 <= t < 169.0) or
            (181.0 <= t < 194.0)
        )

        # Clean institutional / sterile V2 layers (zero forced VHS glitches or chromatic split)
        is_clean_v2_layer = (
            is_text_card or
            (9.0 <= t < 14.0) or
            (22.0 <= t < 25.5) or
            (45.0 <= t < 53.0) or
            (169.0 <= t < 172.5) or
            (300.0 <= t < 338.0)
        )

        if is_clean_v2_layer:
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
