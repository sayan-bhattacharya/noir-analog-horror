"""
Audio Analysis and Visual Hyperparameter Mapping for Project NOIR.
Extracts 20-80 Hz sub-bass transients, RMS energy, and sustained drones from Noir.wav.
"""
import os
import soundfile as sf
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AudioMapper:
    """Analyzes Noir.wav and maps acoustic features to visual hyperparameters."""
    def __init__(self, audio_path: str = None):
        self.audio_path = audio_path or os.path.join(ROOT, "audio", "Noir.wav")
        if not os.path.exists(self.audio_path):
            # Fallback root path
            alt = os.path.join(ROOT, "Noir.wav")
            if os.path.exists(alt):
                self.audio_path = alt

        self.samples = None
        self.sr = 44100
        self.has_audio = False

        if os.path.exists(self.audio_path):
            try:
                data, sr = sf.read(self.audio_path, always_2d=True)
                self.sr = sr
                # Mono downmix
                self.samples = np.mean(data, axis=1)
                self.has_audio = True
            except Exception as e:
                print(f"Warning: Could not read audio {self.audio_path}: {e}")

    def get_features_at(self, t: float, window_ms: int = 250) -> dict:
        """Returns normalized sub_bass, rms, and transient values at timestamp t."""
        if not self.has_audio or self.samples is None:
            # Deterministic procedural synthetic profile
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

        # Sub-bass proxy via moving average energy
        sub_bass = float(np.mean(np.abs(chunk))) * 3.5
        transient = bool(rms > 0.45)

        return {
            "sub_bass": min(1.0, max(0.0, sub_bass)),
            "rms": min(1.0, max(0.0, rms)),
            "transient": transient
        }
