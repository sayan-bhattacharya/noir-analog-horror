"""
Multi-worker rendering engine for PROJECT NOIR.
Renders 720p HD analog horror film synchronized 100% EXCLUSIVELY with Atandra's track 'Noir.wav'.
No synthetic siren headers or external audio injected. Pure original music only.
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

WIDTH = 1280
HEIGHT = 720
FPS = 24


def render_preview(duration=60.0, start_offset=0.0):
    """
    Renders the 720p story master of NOIR with 100% PURE 'Noir.wav' audio.
    """
    from .frame import load_plates, render_noir_frame

    print(f"Loading Bengali analog horror plates for NOIR ({duration:.1f}s, {int(duration * FPS)} frames)...", flush=True)
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
        # Sub-bass proxy based on timeline
        sub_bass = 0.15 if t < 12.0 else (0.25 if t < 30.0 else (0.45 if t < 55.0 else 0.35))
        frame = render_noir_frame(plates, t, width=WIDTH, height=HEIGHT, sub_bass=sub_bass)
        pipe.stdin.write(frame.tobytes())

        if f_idx % 120 == 0:
            print(f"  Rendered {f_idx}/{total_frames} frames ({t:.1f}s)...", flush=True)

    pipe.stdin.close()
    pipe.wait()

    # Mux 100% PURE Noir.wav directly into the video container
    print(f"Muxing pure original audio from {AUDIO} into {OUTPUT_720P}...", flush=True)
    cmd = [
        "ffmpeg", "-y", "-i", raw_video,
        "-ss", str(start_offset), "-i", AUDIO, "-t", str(duration),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
        OUTPUT_720P
    ]
    subprocess.check_call(cmd)

    # Cleanup temp raw video
    if os.path.exists(raw_video):
        os.remove(raw_video)

    print(f"[SUCCESS] Pure Noir Master: {OUTPUT_720P} ({os.path.getsize(OUTPUT_720P) / 1024 / 1024:.1f} MB)", flush=True)
    return True


if __name__ == "__main__":
    duration = 60.0
    start_offset = 0.0
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        duration = float(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        start_offset = float(sys.argv[2])
    render_preview(duration=duration, start_offset=start_offset)
