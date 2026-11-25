"""
Post-Credits Hallucinatory 'SHE' Dream Motif, Bipolar (Depression <-> Mania),
and End-to-End Neurological Seizure Progression Actor.

Phases (normalized progress p in [0.0, 1.0]):
- 0.00 - 0.25 | DEPRESSION & AURA: Dreamy desaturated ash-cyan haze, ghostly 'SHE' memory fragments, narrowing tunnel.
- 0.25 - 0.50 | MANIA SURGE: Over-exposed blinding white/amber strobes, hyper-speed scanline drift.
- 0.50 - 0.72 | TONIC PHASE: Locked 18Hz CRT vibration + blood-crimson glitch tears flashing 'SHE'.
- 0.72 - 0.90 | CLONIC PHASE: Violent rhythmic RGB split & frame convulsions.
- 0.90 - 1.00 | POST-ICTAL: Sudden collapse into washed-out pale silence & slow breathing vignette.
"""
import os
import math
import cv2
import numpy as np
from .. import text_overlay

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DREAM_PLATE_PATH = os.path.join(ROOT, "assets", "noir_mel_spectrogram_bg.png")
_DREAM_CACHE = None


def _get_she_plate(w: int, h: int) -> np.ndarray:
    global _DREAM_CACHE
    if _DREAM_CACHE is None and os.path.exists(DREAM_PLATE_PATH):
        bgr = cv2.imread(DREAM_PLATE_PATH)
        if bgr is not None:
            _DREAM_CACHE = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    if _DREAM_CACHE is not None:
        if _DREAM_CACHE.shape[1] != w or _DREAM_CACHE.shape[0] != h:
            return cv2.resize(_DREAM_CACHE, (w, h), interpolation=cv2.INTER_AREA)
        return _DREAM_CACHE.copy()
    return np.full((h, w, 3), 18, dtype=np.uint8)


def draw_she_bipolar_seizure_motif(frame: np.ndarray,
                                   t: float,
                                   p: float,
                                   sub_bass: float = 0.2) -> np.ndarray:
    """
    Renders the hallucinatory 'SHE' dream memory + bipolar depression/mania + end-to-end seizure arc.
    p: normalized progress [0.0 -> 1.0] across the post-credits sequence.
    """
    h, w = frame.shape[:2]
    she_bg = _get_she_plate(w, h).astype(np.float32)

    # Dreamy hallucination soft-focus bloom
    dream_blur = cv2.GaussianBlur(she_bg, (25, 25), 0)
    hallucination = cv2.addWeighted(she_bg, 0.55, dream_blur, 0.45, 0)

    if p < 0.25:
        # 1. DEPRESSION + AURA: cold ash-blue, slow sinking drift, peripheral narrowing
        phase_label = "PHASE I // DEPRESSION & AURA"
        gray = cv2.cvtColor(hallucination.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
        cold = np.stack([gray * 0.65, gray * 0.78, gray * 0.92], axis=2)
        frame[:] = np.clip(cold * 0.85, 0, 255).astype(np.uint8)

    elif p < 0.50:
        # 2. MANIA SURGE: over-exposed blinding amber/white flashes & racing energy
        phase_label = "PHASE II // MANIA"
        strobe = 0.5 + 0.5 * math.sin(t * 22.0)
        bright = hallucination * (1.1 + 0.7 * strobe)
        frame[:] = np.clip(bright, 0, 255).astype(np.uint8)

    elif p < 0.72:
        # 3. TONIC SEIZURE PHASE: high-frequency 18Hz lock + bloody crimson glitch tears
        phase_label = "PHASE III // TONIC LOCK"
        jitter_x = int(math.sin(t * 110.0) * 8)
        jitter_y = int(math.cos(t * 95.0) * 5)
        shifted = np.roll(hallucination.astype(np.uint8), (jitter_y, jitter_x), axis=(0, 1)).astype(np.float32)
        # Blood-crimson tint
        shifted[:, :, 0] = np.clip(shifted[:, :, 0] * 1.45 + 45, 0, 255)
        shifted[:, :, 1] *= 0.45
        shifted[:, :, 2] *= 0.45
        frame[:] = shifted.astype(np.uint8)

        # Bloody horizontal glitch tears
        rng = np.random.default_rng(int(t * 30))
        for _ in range(6):
            ty = int(rng.integers(0, h - 10))
            cv2.rectangle(frame, (0, ty), (w, ty + int(rng.integers(3, 12))), (215, 20, 25), -1)

    elif p < 0.90:
        # 4. CLONIC SEIZURE PHASE: violent rhythmic RGB separation convulsions
        phase_label = "PHASE IV // CLONIC CONVULSION"
        pulse = math.sin(t * 32.0)
        shift = int(18 * pulse + 8 * sub_bass)
        base_u8 = hallucination.astype(np.uint8)
        r_ch = np.roll(base_u8[:, :, 0], shift, axis=1)
        g_ch = base_u8[:, :, 1]
        b_ch = np.roll(base_u8[:, :, 2], -shift, axis=1)
        frame[:] = np.stack([r_ch, g_ch, b_ch], axis=2)

    else:
        # 5. POST-ICTAL EXHAUSTION: sudden pale washed-out stillness
        phase_label = "PHASE V // POST-ICTAL SILENCE"
        fade = max(0.05, 1.0 - (p - 0.90) / 0.10)
        frame[:] = np.clip(hallucination * 0.45 * fade, 0, 255).astype(np.uint8)

    # Subtle dreamy 'NOIR' hallucination telemetry
    text_overlay.draw_text(
        frame, f"NOIR // DREAM & SEIZURE  |  {phase_label}",
        (int(w * 0.04), int(h * 0.07)),
        font_size=int(h * 0.022), fill_color=(245, 90, 90), anchor="lm"
    )
    return frame
