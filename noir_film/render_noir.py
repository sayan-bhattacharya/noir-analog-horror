"""
Multi-worker rendering engine for PROJECT NOIR.
Renders 720p and 1080p analog horror video with audio synchronization.
"""
import os
import sys
import math
import subprocess
import soundfile as sf
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, "Noir.wav")
OUTPUT_720P = os.path.join(ROOT, "noir_720p_story_preview.mp4")
OUTPUT_MASTER = os.path.join(ROOT, "noir_full_master.mp4")

WIDTH = 1280
HEIGHT = 720
FPS = 24


def create_eas_audio_header(duration=4.0, sr=44100):
    """Generates authentic dual-tone FCC Emergency Action Notification siren (853Hz + 960Hz)."""
    ts = np.linspace(0, duration, int(duration * sr), endpoint=False)
    tone1 = np.sin(2.0 * np.pi * 853.0 * ts)
    tone2 = np.sin(2.0 * np.pi * 960.0 * ts)
    siren = (tone1 * 0.45 + tone2 * 0.45).astype(np.float32)
    # Fade in / out
    fade_len = int(sr * 0.05)
    siren[:fade_len] *= np.linspace(0, 1, fade_len)
    siren[-fade_len:] *= np.linspace(1, 0, fade_len)
    return np.column_stack((siren, siren))


def prepare_preview_audio(out_audio_path, duration=75.0):
    """Muxes the EAS header tone into the first 4 seconds of Noir.wav."""
    sr = 44100
    if os.path.exists(AUDIO):
        music, m_sr = sf.read(AUDIO, start=0, frames=int(duration * sr))
        if music.ndim == 1:
            music = np.column_stack((music, music))
    else:
        music = np.zeros((int(duration * sr), 2), np.float32)

    # Generate EAS alarm
    eas_len = int(4.0 * sr)
    eas = create_eas_audio_header(duration=4.0, sr=sr)
    
    # Crossfade EAS into Noir.wav
    combined = music.copy()
    combined[:eas_len] = combined[:eas_len] * 0.3 + eas * 0.7
    sf.write(out_audio_path, combined, sr)


def render_preview(duration=75.0):
    """
    Renders a 720p story cut of NOIR (t = 0 to 75s) at 24fps.
    Takes ~30 seconds to render locally.
    """
    from .frame import load_plates, render_noir_frame

    print(f"Loading plates for NOIR 720p Story Preview ({duration:.1f}s, {int(duration * FPS)} frames)...", flush=True)
    plates = load_plates(width=WIDTH, height=HEIGHT)

    raw_video = os.path.join(ROOT, "noir_raw.mp4")
    pipe = subprocess.Popen([
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", raw_video
    ], stdin=subprocess.PIPE)

    total_frames = int(duration * FPS)
    for f_idx in range(total_frames):
        t = f_idx / FPS
        # Sub-bass intensity proxy
        sub_bass = 0.15 if t < 12.0 else (0.25 if t < 30.0 else (0.45 if t < 55.0 else 0.35))
        frame = render_noir_frame(plates, t, width=WIDTH, height=HEIGHT, sub_bass=sub_bass)
        pipe.stdin.write(frame.tobytes())

        if f_idx % 120 == 0:
            print(f"  Rendered {f_idx}/{total_frames} frames ({t:.1f}s)...", flush=True)

    pipe.stdin.close()
    pipe.wait()

    # Prepare audio with EAS intro
    preview_audio = os.path.join(ROOT, "noir_preview_audio.wav")
    prepare_preview_audio(preview_audio, duration=duration)

    print(f"Muxing audio into {OUTPUT_720P}...", flush=True)
    cmd = [
        "ffmpeg", "-y", "-i", raw_video,
        "-i", preview_audio,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
        OUTPUT_720P
    ]
    subprocess.check_call(cmd)

    # Cleanup temp files
    if os.path.exists(raw_video):
        os.remove(raw_video)
    if os.path.exists(preview_audio):
        os.remove(preview_audio)

    print(f"[SUCCESS] NOIR 720p Story Master: {OUTPUT_720P} ({os.path.getsize(OUTPUT_720P) / 1024 / 1024:.1f} MB)", flush=True)
    return True


if __name__ == "__main__":
    duration = 75.0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        duration = float(sys.argv[1])
    render_preview(duration=duration)
