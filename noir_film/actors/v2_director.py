"""
Director's Edition V2 Visual Modules for Project NOIR / Nishidak.

Implements the Three Visual Layers & Five-Channel Architecture:
- Persistent Crimson Point continuity signature across all 5 channels & Berlin
- Clean 1994 Institutional Broadcast HUDs (CH 03, CH 07, CH 09, CH 11, BTN 24)
- Vintage Cartographic Map of Nistobdhopur (22.9868 N, 87.8550 E) with extra silhouette
- Sahaj Path / Nandalal Bose style linocut CH 11 diagram (intact -> fractured)
- Horizontal CRT phosphor-line collapse & snap-open transition
- Berlin EXIT 0 & Nistobdhopur Anomaly Poster overlay
"""
import math
import cv2
import numpy as np
from .. import text_overlay


def draw_crimson_point(frame: np.ndarray, t: float, cx: int = None, cy: int = None,
                       radius: int = 4, pulse_hz: float = 1.4):
    """Draws the subtle Crimson Point continuity signature (small red LED + soft bloom)."""
    h, w = frame.shape[:2]
    if cx is None:
        cx = int(w * 0.94)
    if cy is None:
        cy = int(h * 0.08)

    pulse = 0.55 + 0.45 * math.sin(t * pulse_hz * 2.0 * math.pi)
    overlay = frame.copy()
    cv2.circle(overlay, (cx, cy), max(6, radius * 3), (180, 20, 28), -1)
    cv2.addWeighted(overlay, 0.25 * pulse, frame, 1.0 - 0.25 * pulse, 0, frame)
    cv2.circle(frame, (cx, cy), radius, (245, 42, 50), -1)
    cv2.circle(frame, (cx, cy), max(1, radius // 2), (255, 195, 195), -1)


def draw_channel_hud(frame: np.ndarray, channel_label: str, t: float,
                     color=(90, 235, 120), sub_label: str = None,
                     show_crimson_point: bool = True):
    """Draws clean, functional 1994 institutional broadcast corner telemetry."""
    h, w = frame.shape[:2]
    pad_x = int(w * 0.04)
    pad_y = int(h * 0.075)

    # Subtle dark pill behind channel tag for 100% legibility
    box_w = int(w * 0.30)
    box_h = int(h * (0.085 if sub_label else 0.052))
    overlay = frame.copy()
    cv2.rectangle(overlay, (pad_x - 10, pad_y - 20), (pad_x + box_w, pad_y + box_h - 20), (8, 10, 12), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    text_overlay.draw_text(
        frame, channel_label, (pad_x, pad_y),
        font_size=int(h * 0.023), fill_color=color, anchor="lm"
    )
    if sub_label:
        text_overlay.draw_text(
            frame, sub_label, (pad_x, pad_y + int(h * 0.036)),
            font_size=int(h * 0.019), fill_color=(215, 222, 215), anchor="lm"
        )

    if show_crimson_point:
        draw_crimson_point(frame, t, cx=int(w * 0.94), cy=int(h * 0.075), radius=4)


def draw_vintage_map_contradiction(frame: np.ndarray, t: float, st: float, width: int, height: int):
    """
    Renders an authentic 1994 vintage cartographic survey map zooming slowly
    toward Nistobdhopur, marking a settlement, pond, tube-well, and one small
    unexplained extra silhouette near the bamboo fence.
    """
    # Warm aged parchment / Survey of India paper base
    frame[:, :] = [212, 202, 178]

    # Subtle paper fiber texture (deterministic)
    rng = np.random.default_rng(1994)
    grain = rng.integers(-8, 9, (height, width, 1), dtype=np.int16)
    frame[:] = np.clip(frame.astype(np.int16) + grain, 0, 255).astype(np.uint8)

    zoom = 1.0 + 0.14 * min(1.0, st / 10.0)
    cx, cy = width // 2, height // 2

    def pt(nx, ny):
        return (int(cx + (nx - 0.5) * width * zoom), int(cy + (ny - 0.5) * height * zoom))

    # Grid lines (lat/lon cartographic graticule)
    grid_col = (168, 158, 136)
    for gx in np.linspace(0.1, 0.9, 9):
        p1, p2 = pt(gx, 0.05), pt(gx, 0.95)
        cv2.line(frame, p1, p2, grid_col, 1)
    for gy in np.linspace(0.1, 0.9, 6):
        p1, p2 = pt(0.05, gy), pt(0.95, gy)
        cv2.line(frame, p1, p2, grid_col, 1)

    # Winding Bengal river across the map
    river_pts = np.array([
        pt(0.05, 0.72), pt(0.24, 0.62), pt(0.42, 0.68),
        pt(0.58, 0.48), pt(0.76, 0.52), pt(0.95, 0.34)
    ], np.int32)
    cv2.polylines(frame, [river_pts], False, (108, 142, 156), max(6, int(14 * zoom)), cv2.LINE_AA)

    # Village pond (পুকুর)
    pond_c = pt(0.46, 0.50)
    cv2.ellipse(frame, pond_c, (int(42 * zoom), int(26 * zoom)), 12, 0, 360, (116, 148, 160), -1)
    cv2.ellipse(frame, pond_c, (int(42 * zoom), int(26 * zoom)), 12, 0, 360, (58, 52, 44), 2)

    # Narrow railway line with cross-ties
    rail_pts = np.array([pt(0.12, 0.25), pt(0.50, 0.28), pt(0.88, 0.20)], np.int32)
    cv2.polylines(frame, [rail_pts], False, (70, 62, 54), 2, cv2.LINE_AA)

    # Tube-well symbol & settlement square
    tw_c = pt(0.55, 0.56)
    cv2.circle(frame, tw_c, int(8 * zoom), (45, 40, 36), 2)
    cv2.circle(frame, tw_c, int(3 * zoom), (45, 40, 36), -1)

    # The extra anomalous mark near the bamboo fence (matches the black cat coordinate)
    cat_c = pt(0.64, 0.62)
    cv2.circle(frame, cat_c, int(16 * zoom), (185, 38, 42), 1, cv2.LINE_AA)
    draw_crimson_point(frame, t, cx=cat_c[0], cy=cat_c[1], radius=4)

    # Clean institutional labels
    text_overlay.draw_text(
        frame, "SURVEY ARCHIVE // NISTOBDHOPUR", (int(width * 0.05), int(height * 0.90)),
        font_size=int(height * 0.025), fill_color=(42, 36, 30), anchor="lm"
    )
    text_overlay.draw_text(
        frame, "22.9868° N, 87.8550° E", (int(width * 0.95), int(height * 0.90)),
        font_size=int(height * 0.024), fill_color=(165, 32, 36), anchor="rm"
    )


def draw_cat_shadow_turn_scene(frame: np.ndarray, t: float, st: float, width: int, height: int):
    """
    Fallback/composite locked-off scene: ordinary black cat sitting completely still
    on a split-bamboo fence while ONLY its cast shadow slowly turns its head.
    """
    # Dusk rural courtyard palette
    frame[:, :] = [24, 28, 30]
    mud_y = int(height * 0.42)
    cv2.rectangle(frame, (0, mud_y), (width, height), (46, 42, 38), -1)

    # Cast shadow on the mud wall behind the fence (subtle, low contrast)
    sh_x = int(width * 0.54)
    sh_y = int(height * 0.64)
    head_turn = math.sin(min(1.0, st / 6.0) * math.pi * 0.5) * 18.0
    cv2.ellipse(frame, (sh_x, sh_y + 24), (24, 42), 0, 0, 360, (22, 20, 18), -1)
    sh_hx = int(sh_x + head_turn)
    sh_hy = int(sh_y - 24)
    cv2.circle(frame, (sh_hx, sh_hy), 16, (22, 20, 18), -1)
    cv2.fillPoly(frame, [np.array([[sh_hx - 14, sh_hy - 8], [sh_hx - 10, sh_hy - 26], [sh_hx - 2, sh_hy - 12]])], (22, 20, 18))
    cv2.fillPoly(frame, [np.array([[sh_hx + 14, sh_hy - 8], [sh_hx + 10, sh_hy - 26], [sh_hx + 2, sh_hy - 12]])], (22, 20, 18))

    # Split-bamboo fence
    fence_y = int(height * 0.72)
    for bx in range(0, width, 44):
        cv2.rectangle(frame, (bx, fence_y - 30), (bx + 14, height), (58, 52, 40), -1)
    cv2.rectangle(frame, (0, fence_y), (width, fence_y + 14), (72, 64, 48), -1)

    # Ordinary black cat sitting completely motionless (facing away/profile)
    cx = int(width * 0.50)
    cy = fence_y - 2
    cv2.ellipse(frame, (cx, cy - 26), (18, 30), 0, 0, 360, (10, 10, 12), -1)
    cv2.circle(frame, (cx, cy - 62), 13, (10, 10, 12), -1)
    cv2.fillPoly(frame, [np.array([[cx - 11, cy - 68], [cx - 8, cy - 82], [cx - 2, cy - 70]])], (10, 10, 12))
    cv2.fillPoly(frame, [np.array([[cx + 11, cy - 68], [cx + 8, cy - 82], [cx + 2, cy - 70]])], (10, 10, 12))
    cv2.line(frame, (cx + 12, cy - 6), (cx + 34, cy + 16), (10, 10, 12), 5, cv2.LINE_AA)


def draw_sahaj_path_yantra(frame: np.ndarray, t: float, st: float, width: int, height: int, fractured: bool = False):
    """
    CH 11 Educational Programming: Sahaj Path / Nandalal Bose style bold linocut
    protective yantra & Trinetra geometry on cream paper, fracturing cleanly at 02:49.
    """
    # Cream archival linocut paper
    frame[:, :] = [232, 226, 210]
    cx, cy = width // 2, int(height * 0.47)
    r_outer = int(height * 0.24)

    # Bold woodcut border frame
    pad = int(height * 0.08)
    cv2.rectangle(frame, (pad, pad), (width - pad, height - pad), (18, 18, 18), 4)
    cv2.rectangle(frame, (pad + 10, pad + 10), (width - pad - 10, height - pad - 10), (18, 18, 18), 1)

    # Protective yantra circles + triangles
    shift = int(min(1.0, st / 3.0) * 16) if fractured else 0
    cv2.circle(frame, (cx - shift, cy), r_outer, (20, 20, 20), 4, cv2.LINE_AA)
    cv2.circle(frame, (cx + shift, cy), int(r_outer * 0.72), (175, 30, 35), 3, cv2.LINE_AA)

    tri1 = np.array([[cx, cy - int(r_outer * 0.68)], [cx - int(r_outer * 0.58), cy + int(r_outer * 0.34)], [cx + int(r_outer * 0.58), cy + int(r_outer * 0.34)]], np.int32)
    tri2 = np.array([[cx, cy + int(r_outer * 0.68)], [cx - int(r_outer * 0.58), cy - int(r_outer * 0.34)], [cx + int(r_outer * 0.58), cy - int(r_outer * 0.34)]], np.int32)
    cv2.polylines(frame, [tri1], True, (20, 20, 20), 3, cv2.LINE_AA)
    cv2.polylines(frame, [tri2], True, (20, 20, 20), 3, cv2.LINE_AA)

    if fractured:
        # Clean diagonal fracture crack across the diagram
        crack = np.array([[cx - 180, cy - 160], [cx - 40, cy - 20], [cx + 25, cy + 30], [cx + 190, cy + 170]], np.int32)
        cv2.polylines(frame, [crack], False, (232, 226, 210), 10, cv2.LINE_AA)
        cv2.polylines(frame, [crack], False, (175, 30, 35), 2, cv2.LINE_AA)

    draw_crimson_point(frame, t, cx=cx, cy=cy, radius=5)


def draw_crt_collapse_open(frame: np.ndarray, t: float, st: float, width: int, height: int):
    """
    04:40 - 05:00 False Ending: Horizontal CRT collapse to single phosphor line,
    pitch black, then snaps back open at 04:58 (st=18.0) as the door opens.
    """
    if st < 6.0:
        # Collapse vertically into a single horizontal glowing line
        p = min(1.0, st / 5.0)
        band_h = max(2, int(height * (1.0 - p)))
        y0 = (height - band_h) // 2
        if band_h > 4:
            shrunk = cv2.resize(frame, (width, band_h), interpolation=cv2.INTER_AREA)
            frame[:, :] = [2, 2, 4]
            frame[y0:y0 + band_h, :] = shrunk
        else:
            frame[:, :] = [2, 2, 4]
            cv2.line(frame, (0, height // 2), (width, height // 2), (225, 240, 235), 2)
    elif st < 18.0:
        # Pitch black void with single faint Crimson Point telemetry dot
        frame[:, :] = [2, 2, 4]
        if 8.0 <= st < 17.5:
            draw_crimson_point(frame, t, cx=width // 2, cy=height // 2, radius=3, pulse_hz=0.8)
    else:
        # 04:58 Snap open into blinding cool-white EXIT 0 light
        open_p = min(1.0, (st - 18.0) / 1.5)
        band_h = max(4, int(height * open_p))
        y0 = (height - band_h) // 2
        frame[:, :] = [2, 2, 4]
        frame[y0:y0 + band_h, :] = [225, 240, 232]


def draw_exit0_hud(frame: np.ndarray, t: float, width: int, height: int, show_anomaly_card: bool = False):
    """Overlays crisp German/Matrix EXIT 0 signage and persistent Crimson Point."""
    # Top-center clean EXIT 0 badge
    bx1, by1 = int(width * 0.43), int(height * 0.05)
    bx2, by2 = int(width * 0.57), int(height * 0.12)
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (18, 28, 24), -1)
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (215, 245, 225), 2)
    text_overlay.draw_text(
        frame, "EXIT 0", (width // 2, (by1 + by2) // 2),
        font_size=int(height * 0.032), fill_color=(235, 250, 240), anchor="mm"
    )
    draw_crimson_point(frame, t, cx=int(width * 0.94), cy=int(height * 0.075), radius=4)

    if show_anomaly_card:
        text_overlay.draw_text(
            frame, "একটা জিনিস বদলে গেছে। দেখতে পেলেন?",
            (width // 2, int(height * 0.88)),
            font_size=int(height * 0.032), fill_color=(240, 245, 235), anchor="mm"
        )
