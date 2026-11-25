"""
Authentic Rural Bengal Tube-Well (Chapa-Kol) & Time-Lapse Night Sky Actor for Project NOIR.
Renders around the 1:07 mark (01:00 - 01:14):
1. Left-hand side cast iron tube-well (chapa-kol) dripping thick, viscous black fluid frame-by-frame.
2. Controlled droplet physics: viscous bead formation, filament stretch, tear-off drop, falling, and puddle ripple.
3. Time-lapse moonlit clouds moving continuously across the sky, obstructing and revealing the pale moon.
"""
import math
import cv2
import numpy as np


def draw_moon_and_clouds(frame: np.ndarray, t: float, width: int, height: int):
    """
    Renders continuous time-lapse clouds drifting across the midnight moon.
    Obstructs the moon and reveals it in a cyclic atmospheric time-lapse.
    """
    moon_cx = int(width * 0.76)
    moon_cy = int(height * 0.20)
    moon_r = int(height * 0.055)

    # 1. Base Pale Moon
    # Lunar Corona Glow
    for r_glow, alpha in [(moon_r * 3, 0.08), (moon_r * 2, 0.15), (int(moon_r * 1.3), 0.25)]:
        overlay = frame.copy()
        cv2.circle(overlay, (moon_cx, moon_cy), int(r_glow), (210, 220, 230), -1)
        cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

    # Moon Disc with crater mare shading
    cv2.circle(frame, (moon_cx, moon_cy), moon_r, (230, 235, 240), -1, cv2.LINE_AA)
    # Subtle dark lunar maria
    cv2.ellipse(frame, (moon_cx - int(moon_r * 0.2), moon_cy - int(moon_r * 0.1)),
                (int(moon_r * 0.35), int(moon_r * 0.25)), -20, 0, 360, (190, 195, 200), -1)
    cv2.ellipse(frame, (moon_cx + int(moon_r * 0.25), moon_cy + int(moon_r * 0.15)),
                (int(moon_r * 0.30), int(moon_r * 0.20)), 15, 0, 360, (195, 200, 205), -1)

    # 2. Time-Lapse Cloud Bands Drifting across the sky
    # Multiple layers moving at different time-lapse speeds
    cloud_speed = 35.0  # px per second
    cloud_overlay = frame.copy()

    for layer_idx, speed_mult, y_base, opacity in [
        (1, 1.0, int(height * 0.16), 0.75),
        (2, 0.65, int(height * 0.22), 0.60),
        (3, 1.3, int(height * 0.10), 0.50)
    ]:
        cloud_x_offset = (t * cloud_speed * speed_mult) % (width + 600) - 300
        # Draw elongated, fluffy cloud puffs
        for puff in range(8):
            px = int(cloud_x_offset + puff * 160)
            py = int(y_base + math.sin(t * 0.8 + puff * 1.2) * 12)
            pw = int(140 + 30 * math.sin(puff * 1.5))
            ph = int(45 + 15 * math.cos(puff * 2.0))

            # If near moon, highlight cloud edges with lunar silver silver scattering
            dist_to_moon = math.hypot(px - moon_cx, py - moon_cy)
            if dist_to_moon < moon_r * 2.8:
                col = (140, 148, 160)  # Silver illuminated cloud
            else:
                col = (18, 22, 28)    # Dark nocturnal silhouette cloud

            cv2.ellipse(cloud_overlay, (px, py), (pw, ph), 0, 0, 360, col, -1)

    cv2.addWeighted(cloud_overlay, 0.65, frame, 0.35, 0, frame)


def draw_dripping_fluid(frame: np.ndarray,
                        spout_x: int,
                        spout_y: int,
                        puddle_y: int,
                        t: float,
                        scale: float = 1.0):
    """
    Renders deterministic frame-by-frame dripping black fluid physics:
    - Phase 1: Bead formation at the mouth of the spout.
    - Phase 2: Elongation into viscous teardrop with thin stretching filament.
    - Phase 3: Droplet free-fall detachment.
    - Phase 4: Puddle impact splash & concentric ripple expansion.
    """
    black_fluid_col = (4, 4, 6)
    fluid_highlight = (35, 35, 45)  # Specular gloss on viscous black oil

    cycle_period = 1.4  # seconds per drop
    phase = (t % cycle_period) / cycle_period

    drop_radius = int(5 * scale)

    # 1. Puddle at the bottom
    puddle_cx = spout_x + int(2 * scale)
    puddle_rx = int(38 * scale)
    puddle_ry = int(12 * scale)
    cv2.ellipse(frame, (puddle_cx, puddle_y), (puddle_rx, puddle_ry), 0, 0, 360, black_fluid_col, -1)
    # Glossy surface reflection on puddle
    cv2.ellipse(frame, (puddle_cx - int(6 * scale), puddle_y - int(2 * scale)),
                (int(18 * scale), int(4 * scale)), 0, 0, 360, (50, 52, 65), -1)

    # 2. Cycle Simulation
    if phase < 0.45:
        # Phase 1: Viscous bead growing at the rim
        grow_frac = phase / 0.45
        r_curr = max(2, int(drop_radius * grow_frac))
        cv2.circle(frame, (spout_x, spout_y + r_curr), r_curr, black_fluid_col, -1)
        cv2.circle(frame, (spout_x - 1, spout_y + r_curr - 1), max(1, r_curr // 3), fluid_highlight, -1)

    elif phase < 0.68:
        # Phase 2: Teardrop elongation with stretching filament
        stretch_frac = (phase - 0.45) / 0.23
        hang_y = spout_y + int(drop_radius + stretch_frac * 28 * scale)
        # Filament
        cv2.line(frame, (spout_x, spout_y), (spout_x, hang_y), black_fluid_col, max(1, int(2 * scale)), cv2.LINE_AA)
        # Stretched teardrop
        cv2.ellipse(frame, (spout_x, hang_y), (int(drop_radius * 0.8), int(drop_radius * 1.4)), 0, 0, 360, black_fluid_col, -1)
        cv2.circle(frame, (spout_x - 1, hang_y - 1), 1, fluid_highlight, -1)

    elif phase < 0.90:
        # Phase 3: Droplet free-fall
        fall_frac = (phase - 0.68) / 0.22
        # Accelerating gravity: s = 0.5 * g * t^2
        dist_total = puddle_y - spout_y - drop_radius
        fall_y = int(spout_y + drop_radius + 28 * scale + dist_total * (fall_frac ** 2.0))
        fall_y = min(puddle_y, fall_y)

        cv2.ellipse(frame, (spout_x, fall_y), (drop_radius, int(drop_radius * 1.3)), 0, 0, 360, black_fluid_col, -1)
        cv2.circle(frame, (spout_x - 1, fall_y - 1), 1, fluid_highlight, -1)

    else:
        # Phase 4: Impact & Concentric Puddle Ripples
        impact_frac = (phase - 0.90) / 0.10
        max_ripple_r = int(32 * scale)

        for rip_idx, delay in [(1, 0.0), (2, 0.35)]:
            local_rip = max(0.0, impact_frac - delay) / (1.0 - delay)
            if local_rip > 0:
                rip_r = int(local_rip * max_ripple_r)
                rip_alpha = 1.0 - local_rip
                rip_col = (int(80 * rip_alpha), int(85 * rip_alpha), int(100 * rip_alpha))
                cv2.ellipse(frame, (puddle_cx, puddle_y), (rip_r, max(2, int(rip_r * 0.32))), 0, 0, 360, rip_col, 1, cv2.LINE_AA)


def draw_tubewell_left(frame: np.ndarray,
                       cx: int,
                       base_y: int,
                       t: float,
                       scale: float = 1.0) -> tuple:
    """
    Renders an authentic 1990s rural Indian cast-iron handpump (chapa-kol)
    anchored firmly on the LEFT side of the frame.
    Returns (spout_x, spout_y, puddle_y) for dripping fluid coordination.
    """
    iron_col = (26, 28, 34)       # Weathered dark cast iron
    rust_col = (42, 32, 26)       # Oxidation patina
    highlight_col = (65, 70, 80)  # Cold silvery moonlight reflection on rim

    # 1. Concrete / Mud base platform
    plat_w = int(120 * scale)
    plat_h = int(24 * scale)
    cv2.rectangle(frame, (cx - int(50 * scale), base_y), (cx + plat_w, base_y + plat_h), (20, 22, 26), -1)
    cv2.rectangle(frame, (cx - int(50 * scale), base_y), (cx + plat_w, base_y + plat_h), (35, 38, 44), 1)

    # 2. Main vertical cylindrical pipe
    col_w = int(26 * scale)
    col_h = int(160 * scale)
    top_y = base_y - col_h

    cv2.rectangle(frame, (cx, top_y), (cx + col_w, base_y), iron_col, -1)
    # Rust texture streaks
    cv2.line(frame, (cx + 4, top_y + 10), (cx + 4, base_y - 10), rust_col, 2)
    cv2.line(frame, (cx + col_w - 3, top_y + 5), (cx + col_w - 3, base_y - 5), highlight_col, 1)

    # Flange rings
    for ring_y in [top_y + int(col_h * 0.3), top_y + int(col_h * 0.65), base_y - 6]:
        cv2.rectangle(frame, (cx - 3, ring_y), (cx + col_w + 3, ring_y + 6), (36, 40, 48), -1)

    # 3. Top Pump Head cap
    cap_h = int(28 * scale)
    cv2.rectangle(frame, (cx - 4, top_y - cap_h), (cx + col_w + 4, top_y), iron_col, -1)
    cv2.circle(frame, (cx + col_w // 2, top_y - cap_h), int(col_w // 2 + 4), iron_col, -1)

    # 4. Spout extending towards the RIGHT
    spout_len = int(46 * scale)
    spout_y_mid = top_y + int(col_h * 0.42)
    spout_h = int(16 * scale)

    pts_spout = np.array([
        [cx + col_w, spout_y_mid - spout_h // 2],
        [cx + col_w + spout_len, spout_y_mid - spout_h // 3],
        [cx + col_w + spout_len, spout_y_mid + spout_h // 2],
        [cx + col_w, spout_y_mid + spout_h // 2]
    ], np.int32)
    cv2.fillPoly(frame, [pts_spout], iron_col)
    cv2.polylines(frame, [pts_spout], True, highlight_col, 1, cv2.LINE_AA)

    spout_x = cx + col_w + spout_len - 2
    spout_y = spout_y_mid + spout_h // 2

    # 5. Long Pump Handle extending to the LEFT
    handle_pivot_x = cx + 4
    handle_pivot_y = top_y - int(cap_h * 0.4)
    # Subtle eerie handle vibration synchronized to sub-bass / creak
    creak_angle = math.sin(t * 1.8) * 0.08 - 0.28  # Angled upward/leftward

    handle_len = int(140 * scale)
    hx_end = int(handle_pivot_x - handle_len * math.cos(creak_angle))
    hy_end = int(handle_pivot_y - handle_len * math.sin(creak_angle))

    cv2.line(frame, (handle_pivot_x, handle_pivot_y), (hx_end, hy_end), iron_col, int(6 * scale), cv2.LINE_AA)
    # Heavy cast-iron counterweight knob at end of handle
    cv2.circle(frame, (hx_end, hy_end), int(10 * scale), iron_col, -1)
    cv2.circle(frame, (hx_end - 2, hy_end - 2), int(3 * scale), highlight_col, -1)

    puddle_y = base_y + int(10 * scale)
    return spout_x, spout_y, puddle_y


def draw_tubewell_scene_0107(frame: np.ndarray, t: float, width: int = 1280, height: int = 720) -> np.ndarray:
    """
    Renders the complete master scene for the 1:07 mark:
    - Time-lapse sky with moon and moving clouds.
    - Left-hand side authentic cast-iron tube-well (no right-hand tap!).
    - Frame-by-frame dripping viscous black fluid into dark puddle with ripples.
    """
    # 1. Sky & Cloud time-lapse
    draw_moon_and_clouds(frame, t, width, height)

    # 2. Tube-well on left
    cx = int(width * 0.22)
    base_y = int(height * 0.82)
    scale = max(0.8, height / 720.0 * 1.15)

    spout_x, spout_y, puddle_y = draw_tubewell_left(frame, cx, base_y, t, scale=scale)

    # 3. Dripping Black Fluid
    draw_dripping_fluid(frame, spout_x, spout_y, puddle_y, t, scale=scale)

    return frame


def draw_oil_drip_closeup(frame: np.ndarray, t: float, width: int = 1280, height: int = 720) -> np.ndarray:
    """
    Close-up angle facing the rusted cast-iron tube-well spout:
    renders thick, glossy viscous black oil forming, stretching, and dripping drop-by-drop.
    """
    spout_x = int(width * 0.48)
    spout_y = int(height * 0.48)
    puddle_y = int(height * 0.88)
    scale = max(1.2, height / 720.0 * 1.9)
    draw_dripping_fluid(frame, spout_x, spout_y, puddle_y, t, scale=scale)
    return frame
