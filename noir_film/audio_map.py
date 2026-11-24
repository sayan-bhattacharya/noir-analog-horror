"""
Audio Analysis and Visual Hyperparameter Mapping for Project NOIR / Between the Notes.
Extracts speech cadence, RMS energy, conversational bursts, and sub-bass transients
from BetweenTheNotes_Podcast_5min.wav, Noir.wav, or Between the notes podcast audio.m4a.
"""
import os
import soundfile as sf
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_default_audio_path():
    """Finds the most appropriate master audio file in project hierarchy."""
    candidates = [
        os.path.join(ROOT, "audio", "BetweenTheNotes_Podcast_5min.wav"),
        os.path.join(ROOT, "audio", "Noir.wav"),
        os.path.join(ROOT, "Noir.wav"),
        r"E:\betweenthenotes\transcription\podcast_opening_5min.wav",
        r"E:\betweenthenotes\Between the notes podcast audio.m4a"
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


class AudioMapper:
    """Analyzes audio and maps acoustic and speech features to visual hyperparameters."""
    def __init__(self, audio_path: str = None):
        self.audio_path = audio_path or find_default_audio_path()
        self.samples = None
        self.sr = 44100
        self.has_audio = False

        if self.audio_path and os.path.exists(self.audio_path):
            try:
                data, sr = sf.read(self.audio_path, always_2d=True)
                self.sr = sr
                # Downmix to mono
                self.samples = np.mean(data, axis=1)
                self.has_audio = True
                print(f"[AudioMapper] Loaded master track: {self.audio_path} ({len(self.samples)/sr:.1f}s @ {sr}Hz)")
            except Exception as e:
                print(f"[AudioMapper] Warning: Could not read audio {self.audio_path}: {e}")

    def get_features_at(self, t: float, window_ms: int = 250) -> dict:
        """Returns normalized sub_bass, rms, and transient values at timestamp t."""
        if not self.has_audio or self.samples is None:
            # Deterministic synthetic profile fallback
            sub = 0.2 + 0.15 * np.sin(t * 1.5)
            rms = 0.25 + 0.10 * np.cos(t * 0.8)
            return {"sub_bass": float(sub), "rms": float(rms), "transient": False}

        center_idx = int(t * self.sr)
        win_size = int((window_ms / 1000.0) * self.sr)
        start_idx = max(0, center_idx - win_size // 2)
        end_idx = min(len(self.samples), center_idx + win_size // 2)

        if start_idx >= end_idx:
            return {"sub_bass": 0.1, "rms": 0.1, "transient": False}

        chunk = self.samples[start_idx:end_idx]
        rms = float(np.sqrt(np.mean(chunk**2)))

        # Speech envelope / dynamic sub-bass proxy
        sub_bass = float(np.mean(np.abs(chunk))) * 3.5
        transient = bool(rms > 0.35)

        return {
            "sub_bass": min(1.0, max(0.0, sub_bass)),
            "rms": min(1.0, max(0.0, rms)),
            "transient": transient
        }
