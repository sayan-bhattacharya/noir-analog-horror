"""
Master CLI Rendering Engine for Project NOIR / Nishidak.
Supports full 180s renders, fast previews, single scene renders, and quality selection.
"""
import os
import sys
import time
import argparse
import yaml
import soundfile as sf
import numpy as np

from .utils.config_loader import load_global_config, load_yaml
from .utils.video_io import FFmpegVideoPipe, mux_audio
from .timeline import NoirTimeline
from .audio_map import AudioMapper

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")
AUDIO_FILE = os.path.join(ROOT, "audio", "Noir.wav")
if not os.path.exists(AUDIO_FILE):
    alt_audio = os.path.join(ROOT, "Noir.wav")
    if os.path.exists(alt_audio):
        AUDIO_FILE = alt_audio


def render(args):
    global_cfg = load_global_config()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Resolution and FPS parameters
    if args.preview:
        width = int(global_cfg["render"]["width"] * global_cfg["render"]["preview_scale"])
        height = int(global_cfg["render"]["height"] * global_cfg["render"]["preview_scale"])
        fps = 12
    else:
        width = global_cfg["render"]["width"]
        height = global_cfg["render"]["height"]
        fps = global_cfg["render"]["fps"]

    crf = 16 if args.quality == "final" else (24 if args.preview else 18)

    # Scene duration and start time determination
    scene_ranges = {
        1: (0.0, 15.0),
        2: (15.0, 35.0),
        3: (35.0, 65.0),
        4: (65.0, 95.0),
        5: (95.0, 125.0),
        6: (125.0, 165.0),
        7: (165.0, 180.0)
    }

    if args.scene is not None:
        if args.scene not in scene_ranges:
            print(f"Error: scene must be between 1 and 7, got {args.scene}")
            return
        start_t, end_t = scene_ranges[args.scene]
        duration = end_t - start_t
        out_name = f"scene_{args.scene:02d}_{'preview' if args.preview else 'render'}.mp4"
    elif args.config is not None:
        custom_cfg = load_yaml(args.config)
        start_t = custom_cfg.get("start_time", 0.0)
        duration = custom_cfg.get("duration", 15.0)
        end_t = start_t + duration
        code = custom_cfg.get("scene_code", "custom")
        out_name = f"{code}_{'preview' if args.preview else 'render'}.mp4"
    else:
        # Full render
        start_t = 0.0
        duration = float(args.duration or global_cfg["render"]["duration_seconds"])
        end_t = start_t + duration
        out_name = f"noir_master_{int(duration)}s_{'preview' if args.preview else 'final'}.mp4"

    raw_output = os.path.join(OUTPUT_DIR, f"temp_{out_name}")
    final_output = os.path.join(OUTPUT_DIR, out_name)

    print(f"===========================================================")
    print(f"  PROJECT NOIR / NISHIDAK VISUAL ENGINE")
    print(f"  Rendering: {out_name}")
    print(f"  Time Window: {start_t:.1f}s -> {end_t:.1f}s ({duration:.1f}s)")
    print(f"  Dimensions: {width}x{height} @ {fps} fps (CRF: {crf})")
    print(f"===========================================================")

    timeline = NoirTimeline(global_cfg)
    audio_mapper = AudioMapper(AUDIO_FILE) if not args.no_audio else None

    pipe = FFmpegVideoPipe(raw_output, width=width, height=height, fps=fps, crf=crf)

    total_frames = int(duration * fps)
    start_wall = time.time()

    for f_idx in range(total_frames):
        local_t = f_idx / fps
        t = start_t + local_t

        audio_features = audio_mapper.get_features_at(t) if audio_mapper else {"sub_bass": 0.1, "rms": 0.1}
        frame = timeline.render_frame_at(t, width=width, height=height, audio_features=audio_features)
        pipe.write_frame(frame)

        if f_idx % (fps * 2) == 0 or f_idx == total_frames - 1:
            elapsed = time.time() - start_wall
            pct = (f_idx + 1) / total_frames * 100.0
            fps_render = (f_idx + 1) / max(0.001, elapsed)
            print(f"  Progress: {pct:5.1f}% | Frame: {f_idx+1:4d}/{total_frames} | Speed: {fps_render:4.1f} fps", flush=True)

    pipe.close()

    # Audio Muxing
    if not args.no_audio and os.path.exists(AUDIO_FILE):
        print(f"Muxing soundtrack from {AUDIO_FILE}...")
        mux_audio(raw_output, AUDIO_FILE, final_output, duration=duration)
    else:
        if os.path.exists(raw_output):
            if os.path.exists(final_output):
                os.remove(final_output)
            os.rename(raw_output, final_output)

    total_time = time.time() - start_wall
    file_size_mb = os.path.getsize(final_output) / (1024 * 1024) if os.path.exists(final_output) else 0
    print(f"[SUCCESS] Master exported to: {final_output} ({file_size_mb:.2f} MB in {total_time:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="Project NOIR / Nishidak Analog Horror Cinema Engine")
    parser.add_argument("--preview", action="store_true", help="Fast low-res 640x360 12fps render")
    parser.add_argument("--full", action="store_true", help="Render full duration master")
    parser.add_argument("--scene", type=int, choices=range(1, 8), help="Render a specific scene (1-7)")
    parser.add_argument("--config", type=str, help="Render from custom scene yaml configuration")
    parser.add_argument("--duration", type=float, help="Custom duration in seconds")
    parser.add_argument("--no-audio", action="store_true", help="Render silent video without audio track")
    parser.add_argument("--quality", choices=["draft", "preview", "final"], default="preview", help="Render encoding quality")

    args = parser.parse_args()

    # Legacy positional argument compatibility (e.g. `python -m noir_film.render_noir 15`)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        args.duration = float(sys.argv[1])
        args.full = True

    render(args)


if __name__ == "__main__":
    main()
