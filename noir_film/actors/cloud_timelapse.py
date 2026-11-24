"""
Night Sky Cloud Time-Lapse Engine for Project NOIR / Between the Notes.
Renders continuous photorealistic cinematic time-lapse cloud motion across the midnight moon.
Loads from the seamless 24fps high-definition video loop 'assets/cloud_timelapse_loop.mp4'.
"""
import os
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
            frames.append(f)
        cap.release()
        if len(frames) > 0:
            _CACHED_FRAMES = frames
            _TOTAL_FRAMES = len(frames)
            print(f"[CloudTimelapse] Cached {_TOTAL_FRAMES} frames from {VIDEO_LOOP_PATH}")
            return _CACHED_FRAMES

    _CACHED_FRAMES = []
    _TOTAL_FRAMES = 0
    return _CACHED_FRAMES


def render_cloud_timelapse_sky(frame: np.ndarray,
                                t: float,
                                width: int = 1280,
                                height: int = 720,
                                moon_pos: tuple = None,
                                cloud_speed: float = 40.0,
                                density: float = 1.0) -> np.ndarray:
    """
    Renders the photorealistic cloud time-lapse nocturnal sky across the moon:
    - Queries the seamless video loop matching timestamp t.
    - Fits/resizes seamlessly into (height, width).
    - Blends into frame preserving silhouettes.
    """
    frames = _load_cached_frames()
    if frames and len(frames) > 0:
        frame_idx = int((t * _FPS)) % len(frames)
        sky = frames[frame_idx]
        if sky.shape[1] != width or sky.shape[0] != height:
            sky = cv2.resize(sky, (width, height), interpolation=cv2.INTER_AREA)

        # Direct blit onto frame
        if np.mean(frame) < 15:
            frame[:] = sky
        else:
            # Alpha composite where frame is dark / night background
            mask = (np.mean(frame, axis=2) < 25)[:, :, np.newaxis]
            frame[:] = np.where(mask, sky, frame)
        return frame

    # Fallback to high-contrast nocturnal background if video not found
    plate_path = os.path.join(ROOT, "plates", "optic_cosmic_moon.jpg")
    if os.path.exists(plate_path):
        plate = cv2.imread(plate_path)
        if plate is not None:
            sky = cv2.resize(plate, (width, height), interpolation=cv2.INTER_AREA)
            frame[:] = sky
            return frame

    frame[:, :] = [18, 14, 10]
    return frame
