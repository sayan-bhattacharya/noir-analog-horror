"""
Video and Audio I/O utilities for Project NOIR.
Lightweight FFmpeg sub-process pipeline with robust fallback.
"""
import os
import subprocess
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_placeholder_plate(width: int = 1280, height: int = 720, label: str = "PLACEHOLDER") -> np.ndarray:
    """Creates a dark atmospheric vignette placeholder plate if an image is missing."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    ys, xs = np.indices((height, width), dtype=np.float32)
    norm_x = (xs - width * 0.5) / (width * 0.5)
    norm_y = (ys - height * 0.5) / (height * 0.5)
    r = np.sqrt(norm_x**2 + norm_y**2)

    # Dark blue-indigo gradient
    vignette = np.clip(1.0 - 0.7 * r, 0.0, 1.0)
    img[:, :, 0] = (25 * vignette).astype(np.uint8)
    img[:, :, 1] = (18 * vignette).astype(np.uint8)
    img[:, :, 2] = (45 * vignette).astype(np.uint8)

    # Subtle placeholder label
    cv2.putText(img, f"[{label}]", (width // 2 - 140, height // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (140, 135, 130), 2, cv2.LINE_AA)
    return img


class FFmpegVideoPipe:
    """High-throughput RGB24 rawvideo pipe into FFmpeg."""
    def __init__(self, output_path: str, width: int = 1280, height: int = 720, fps: int = 24, crf: int = 18):
        self.output_path = output_path
        self.width = width
        self.height = height
        self.fps = fps
        self.cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{width}x{height}", "-pix_fmt", "rgb24", "-r", str(fps),
            "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
            "-pix_fmt", "yuv420p", output_path
        ]
        self.process = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def write_frame(self, frame_rgb: np.ndarray):
        if self.process and self.process.stdin:
            self.process.stdin.write(frame_rgb.tobytes())

    def close(self):
        if self.process:
            if self.process.stdin:
                self.process.stdin.close()
            self.process.wait()
            self.process = None


def mux_audio(video_path: str, audio_path: str, output_path: str, duration: float = None):
    """Muxes audio into the final MP4 container using stream copying."""
    if not os.path.exists(audio_path):
        # If no audio file, simply move video
        if os.path.exists(video_path) and video_path != output_path:
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(video_path, output_path)
        return

    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-stream_loop", "-1", "-i", audio_path,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k"
    ]
    if duration is not None:
        cmd.extend(["-t", str(duration)])
    cmd.append(output_path)

    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(video_path) and video_path != output_path:
        os.remove(video_path)
