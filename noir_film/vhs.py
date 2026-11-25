"""
VHS Tape tracking, horizontal tear, and dropout degradation for Project NOIR.
"""
import math
import cv2
import numpy as np


def apply_vhs_tracking(frame: np.ndarray,
                       t: float,
                       tear_strength: float = 0.25,
                       tracking_prob: float = 0.08,
                       sub_bass: float = 0.0) -> np.ndarray:
    """
    Applies authentic VCR tape tracking jitter and horizontal tears.
    """
    h, w, c = frame.shape
    out = frame.copy()

    # Sub-bass impact creates violent horizontal tracking tearing
    effective_tear = tear_strength + sub_bass * 0.65

    if effective_tear > 0.3 or np.random.uniform(0, 1) < tracking_prob:
        tear_y = int((math.sin(t * 8.3) * 0.5 + 0.5) * (h - 50))
        tear_h = int(10 + effective_tear * 35)
        tear_shift = int(np.random.choice([-1, 1]) * (8 + effective_tear * 40))
        y2 = min(h, tear_y + tear_h)
        out[tear_y:y2, :] = np.roll(out[tear_y:y2, :], tear_shift, axis=1)

    # Color smearing on tape horizontal edges
    if effective_tear > 0.4:
        blurred_chroma = cv2.GaussianBlur(out[:, :, [0, 2]], (9, 1), 0)
        out[:, :, 0] = cv2.addWeighted(out[:, :, 0], 0.6, blurred_chroma[:, :, 0], 0.4, 0)
        out[:, :, 2] = cv2.addWeighted(out[:, :, 2], 0.6, blurred_chroma[:, :, 1], 0.4, 0)

    return out


def apply_tape_dropout(frame: np.ndarray, t: float, frequency: float = 0.04) -> np.ndarray:
    """Simulates oxide flaking causing white speckle dropout streaks."""
    if np.random.uniform(0, 1) < frequency:
        h, w = frame.shape[:2]
        out = frame.copy()
        y = np.random.randint(0, h)
        x = np.random.randint(0, w - 80)
        length = np.random.randint(20, 80)
        out[y, x:x+length] = [230, 230, 220]
        return out
    return frame
