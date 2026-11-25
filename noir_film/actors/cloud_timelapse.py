"""
Night Sky Cloud Time-Lapse Engine for Project NOIR / Between the Notes.
Renders continuous photorealistic cinematic time-lapse cloud motion across the midnight moon.
Supports both full-screen nocturnal sky and locked-off foreground compositing
(keeping huts, trees, fences, and characters completely still while only the sky races).
"""
import os
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VIDEO_LOOP_PATH = os.path.join(ROOT, "assets", "cloud_timelapse_loop.mp4")

_CACHED_FRAMES = None
_TOTAL_FRAMES = 0
_FPS = 24.0


def _load_cached_frames():
    global _CACHED_FRAMES, _TOTAL_FRAMES
    if _CACHED_FRAMES is not None:
        return _CACHED_FRAMES

    if os.path.exists(VIDEO_LOOP_PATH):
        cap = cv2.VideoCapture(VIDEO_LOOP_PATH)
        frames = []
        while True:
            ret, f = cap.read()
            if not ret or f is None:
                break
            frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
        cap.release()
        if len(frames) > 0:
            _CACHED_FRAMES = frames
            _TOTAL_FRAMES = len(frames)
            print(f"[CloudTimelapse] Cached {_TOTAL_FRAMES} frames from {VIDEO_LOOP_PATH}")
            return _CACHED_FRAMES

    _CACHED_FRAMES = []
    _TOTAL_FRAMES = 0
    return _CACHED_FRAMES


def get_sky_frame_at(t: float, width: int, height: int) -> np.ndarray:
    """Returns the looped cloud time-lapse sky frame at timestamp t."""
    frames = _load_cached_frames()
    if frames and len(frames) > 0:
        frame_idx = int((t * _FPS)) % len(frames)
        sky = frames[frame_idx]
        if sky.shape[1] != width or sky.shape[0] != height:
            sky = cv2.resize(sky, (width, height), interpolation=cv2.INTER_AREA)
        return sky.copy()

    plate_path = os.path.join(ROOT, "plates", "optic_cosmic_moon.jpg")
    if os.path.exists(plate_path):
        plate = cv2.imread(plate_path)
        if plate is not None:
            return cv2.resize(plate, (width, height), interpolation=cv2.INTER_AREA)

    sky = np.zeros((height, width, 3), dtype=np.uint8)
    sky[:, :] = [18, 14, 10]
    return sky


def composite_sky_timelapse_on_plate(plate: np.ndarray, t: float, sky_cutoff: float = 0.44) -> np.ndarray:
    """
    Locked-off camera time-lapse compositor:
    Keeps all foreground objects (hut, roof, bamboo fence, ground fog) completely still
    while replacing the upper sky region with the moving cloud time-lapse loop.
    """
    h, w = plate.shape[:2]
    sky = get_sky_frame_at(t, w, h)

    # Vertical sky gradient mask: 1.0 at top sky, smoothly fading to 0.0 at horizon/roofline
    y_coords = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, np.newaxis]
    vert_mask = np.clip((sky_cutoff - y_coords) / 0.16, 0.0, 1.0)

    # Luminance/edge protection so dark foreground silhouettes (roofs, palm fronds) stay intact
    gray = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    # Very dark silhouettes (< 0.12) in the upper region belong to trees/roofs; preserve them
    fg_silhouette = np.clip((gray - 0.08) / 0.18, 0.0, 1.0)

    alpha = (vert_mask * fg_silhouette)
    alpha = cv2.GaussianBlur(alpha, (15, 15), 0)[:, :, np.newaxis]

    out = plate.astype(np.float32) * (1.0 - alpha) + sky.astype(np.float32) * alpha
    return np.clip(out, 0, 255).astype(np.uint8)


def render_cloud_timelapse_sky(frame: np.ndarray,
                                t: float,
                                width: int = 1280,
                                height: int = 720,
                                moon_pos: tuple = None,
                                cloud_speed: float = 40.0,
                                density: float = 1.0) -> np.ndarray:
    """
    Renders full-screen photorealistic cloud time-lapse nocturnal sky across the moon.
    """
    sky = get_sky_frame_at(t, width, height)
    if np.mean(frame) < 15:
        frame[:] = sky
    else:
        mask = (np.mean(frame, axis=2) < 25)[:, :, np.newaxis]
        frame[:] = np.where(mask, sky, frame)
    return frame
