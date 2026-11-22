"""
Color Palette and CRT Phosphor definitions for Project NOIR / Nishidak.
All colors are in RGB format for PIL / NumPy / OpenCV pipeline.
"""
import numpy as np

# Core 1994 Doordarshan CRT palette
SHADOW_TINT = np.array([8, 12, 18], dtype=np.uint8)
HIGHLIGHT_TINT = np.array([220, 235, 205], dtype=np.uint8)
EMERGENCY_RED = np.array([178, 24, 24], dtype=np.uint8)
DD_GOLD = np.array([212, 175, 55], dtype=np.uint8)
COSMIC_SULFUR = np.array([214, 197, 65], dtype=np.uint8)
VOID_BLACK = np.array([4, 4, 6], dtype=np.uint8)
OSD_GREEN = np.array([94, 220, 120], dtype=np.uint8)
CRT_NAVY = np.array([18, 15, 48], dtype=np.uint8)
BONE_WHITE = np.array([220, 214, 202], dtype=np.uint8)

# Color tuples for PIL ImageDraw (R, G, B)
COLOR_TUPLES = {
    "shadow_tint": (8, 12, 18),
    "highlight_tint": (220, 235, 205),
    "emergency_red": (178, 24, 24),
    "dd_gold": (212, 175, 55),
    "cosmic_sulfur": (214, 197, 65),
    "void_black": (4, 4, 6),
    "osd_green": (94, 220, 120),
    "crt_navy": (18, 15, 48),
    "bone_white": (220, 214, 202),
    "white": (255, 255, 255),
}
