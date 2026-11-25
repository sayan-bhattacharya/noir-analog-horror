"""
Act V: 'DESCENT...' — Black Gluey Meta-Object & Infinite Rotating Fall Actor.
Portrays the Truman-Show-like surveillance feed ('CH 07 // DESCENT') where the
protagonist wakes to the Nishir Daak, falls into a viscous black gluey meta-object
hole, and rotates endlessly downward through the void.
"""
import math
import cv2
import numpy as np
from .. import text_overlay


def draw_gluey_meta_hole(frame: np.ndarray, t: float, progress: float = 1.0,
                         sub_bass: float = 0.2,
                         center: tuple[int, int] | None = None,
                         max_width: float = 0.30,
                         max_height: float = 0.18,
                         tendril_strength: float = 1.0) -> np.ndarray:
    """
    Renders a viscous, pitch-black gluey meta-object portal opening up,
    with glossy tar-like rim highlights and stretching sticky tendrils.
    """
    h, w = frame.shape[:2]
    cx, cy = center if center is not None else (w // 2, int(h * 0.56))

    # Expand hole radius smoothly with progress
    max_rx = int(w * max_width * progress)
    max_ry = int(h * max_height * progress)
    if max_rx < 8 or max_ry < 6:
        return frame

    # Subtle organic wobble around the perimeter of the gluey hole
    num_pts = 64
    pts = []
    for i in range(num_pts):
        ang = (i / num_pts) * 2.0 * math.pi
        wobble = 1.0 + 0.08 * math.sin(ang * 5.0 + t * 3.2) + 0.05 * math.cos(ang * 9.0 - t * 2.1)
        wobble += sub_bass * 0.06 * math.sin(ang * 3.0 + t * 8.0)
        px = int(cx + math.cos(ang) * max_rx * wobble)
        py = int(cy + math.sin(ang) * max_ry * wobble)
        pts.append([px, py])

    pts_arr = np.array(pts, np.int32)

    # Diffused violet-purple neon from discrete perimeter lamps.
    saffron = (190, 72, 216)  # BGR: neon violet-purple rim
    lamp_glow = np.zeros_like(frame)
    lamp_count = 32
    for j in range(lamp_count):
        ang = (j / lamp_count) * 2.0 * math.pi
        wobble = 1.0 + 0.08 * math.sin(ang * 5.0 + t * 3.2) + 0.05 * math.cos(ang * 9.0 - t * 2.1)
        lx = int(cx + math.cos(ang) * max_rx * wobble)
        ly = int(cy + math.sin(ang) * max_ry * wobble)
        pulse = 0.28 + 0.72 * max(0.0, math.sin(t * 4.2 - j * 0.73))
        lamp_color = tuple(int(min(255, c * pulse * 1.18)) for c in saffron)
        cv2.circle(lamp_glow, (lx, ly), max(2, int(9 * progress)), lamp_color, -1, cv2.LINE_AA)
    diffuse = cv2.GaussianBlur(lamp_glow, (0, 0), sigmaX=max(2.0, 10.0 * progress))
    cv2.addWeighted(frame, 1.0, diffuse, 0.42, 0, frame)

    # Outer dark tar seepage halo with a faint warm edge.
    halo = frame.copy()
    cv2.fillPoly(halo, [pts_arr], (6, 5, 8))
    cv2.polylines(halo, [pts_arr], True, (34, 18, 48), max(4, int(14 * progress)), cv2.LINE_AA)
    cv2.addWeighted(halo, 0.85, frame, 0.15, 0, frame)

    # Pitch-black meta-object core
    cv2.fillPoly(frame, [pts_arr], (2, 2, 3))

    # Animated violet-purple LED beads, with a few pale glassy glints.
    for j in range(lamp_count):
        ang = (j / lamp_count) * 2.0 * math.pi
        wobble = 1.0 + 0.08 * math.sin(ang * 5.0 + t * 3.2) + 0.05 * math.cos(ang * 9.0 - t * 2.1)
        lx = int(cx + math.cos(ang) * max_rx * wobble)
        ly = int(cy + math.sin(ang) * max_ry * wobble)
        pulse = 0.36 + 0.64 * (0.5 + 0.5 * math.sin(t * 4.2 - j * 0.73))
        color = tuple(int(min(255, c * pulse * 1.18)) for c in saffron)
        cv2.circle(frame, (lx, ly), max(1, int(3.2 * progress)), color, -1, cv2.LINE_AA)

    # High-speed charged particles: a luminous purple radiation trace skims the rim.
    # Short fading dots make the motion legible without turning the hole into a solid neon ring.
    orbit = np.zeros_like(frame)
    cv2.ellipse(orbit, (cx, cy), (max(1, int(max_rx * 1.035)), max(1, int(max_ry * 1.06))),
                0, 0, 360, (112, 42, 160), max(1, int(2.2 * progress)), cv2.LINE_AA)
    cv2.addWeighted(frame, 1.0, cv2.GaussianBlur(orbit, (0, 0), sigmaX=5.0), 0.34, 0, frame)
    for particle in range(3):
        ang = t * 15.0 + particle * (2.0 * math.pi / 3.0)
        px = int(cx + math.cos(ang) * max_rx * 1.035)
        py = int(cy + math.sin(ang) * max_ry * 1.06)
        for tail in range(1, 5):
            ta = ang - tail * 0.055
            tx = int(cx + math.cos(ta) * max_rx * 1.035)
            ty = int(cy + math.sin(ta) * max_ry * 1.06)
            alpha = (5 - tail) / 5.0
            cv2.circle(frame, (tx, ty), max(1, int((4.5 - tail * 0.7) * progress)),
                       (int(170 * alpha), int(82 * alpha), int(245 * alpha)), -1, cv2.LINE_AA)
        cv2.circle(frame, (px, py), max(2, int(4.5 * progress)), (235, 192, 255), -1, cv2.LINE_AA)

    # Glossy wet-glue detail catching the violet portal light.
    for i in range(0, num_pts, 4):
        ang = (i / num_pts) * 2.0 * math.pi
        if math.sin(ang * 2.0 + t * 1.5) > 0.2:
            hx = int(cx + math.cos(ang) * max_rx * 0.94)
            hy = int(cy + math.sin(ang) * max_ry * 0.94)
            cv2.circle(frame, (hx, hy), max(1, int(2 * progress)), (208, 150, 235), -1, cv2.LINE_AA)

    # Sticky black gluey tendrils reaching inward/outward
    for k in range(10):
        base_ang = k * (2.0 * math.pi / 10.0) + math.sin(t * 0.7 + k) * 0.15
        sx = int(cx + math.cos(base_ang) * max_rx * 0.95)
        sy = int(cy + math.sin(base_ang) * max_ry * 0.95)
        ex = int(cx + math.cos(base_ang + 0.2) * max_rx * (0.45 + 0.2 * math.sin(t * 2.0 + k)))
        ey = int(cy + math.sin(base_ang + 0.2) * max_ry * (0.45 + 0.2 * math.cos(t * 2.0 + k)))
        mx = (sx + ex) // 2 + int(12 * math.sin(t * 3.0 + k))
        my = (sy + ey) // 2 + int(10 * math.cos(t * 2.5 + k))
        strand = np.array([[sx, sy], [mx, my], [ex, ey]], np.int32)
        if tendril_strength > 0.01:
            thickness = max(1, int(5 * progress * tendril_strength))
            cv2.polylines(frame, [strand], False, (12, 12, 16), thickness, cv2.LINE_AA)
            cv2.polylines(frame, [strand], False, (55, 58, 68), 1, cv2.LINE_AA)

    return frame


def _draw_articulated_falling_man(canvas: np.ndarray, cx: int, cy: int, scale: float, t: float):
    """Draws a crisp high-contrast silhouette of a falling man with flailing limbs."""
    col = (210, 212, 218)
    edge = (40, 42, 48)
    s = scale

    # Head
    cv2.circle(canvas, (cx, int(cy - 42 * s)), max(3, int(11 * s)), col, -1, cv2.LINE_AA)
    # Torso
    torso = np.array([
        [cx - int(12 * s), int(cy - 30 * s)],
        [cx + int(12 * s), int(cy - 30 * s)],
        [cx + int(9 * s), int(cy + 14 * s)],
        [cx - int(9 * s), int(cy + 14 * s)],
    ], np.int32)
    cv2.fillPoly(canvas, [torso], col)

    # Flailing arms
    arm_wave = math.sin(t * 6.5) * 18 * s
    cv2.line(canvas, (cx - int(11 * s), int(cy - 26 * s)),
             (cx - int(36 * s), int(cy - 42 * s + arm_wave)), col, max(2, int(6 * s)), cv2.LINE_AA)
    cv2.line(canvas, (cx + int(11 * s), int(cy - 26 * s)),
             (cx + int(38 * s), int(cy - 36 * s - arm_wave)), col, max(2, int(6 * s)), cv2.LINE_AA)

    # Flailing legs
    leg_wave = math.cos(t * 5.5) * 16 * s
    cv2.line(canvas, (cx - int(6 * s), int(cy + 13 * s)),
             (cx - int(18 * s), int(cy + 52 * s + leg_wave)), col, max(2, int(7 * s)), cv2.LINE_AA)
    cv2.line(canvas, (cx + int(6 * s), int(cy + 13 * s)),
             (cx + int(20 * s), int(cy + 48 * s - leg_wave)), col, max(2, int(7 * s)), cv2.LINE_AA)

    # Subtle dark rim for separation against bright spiral rings
    cv2.circle(canvas, (cx, int(cy - 42 * s)), max(3, int(11 * s)), edge, 1, cv2.LINE_AA)


def draw_rotating_descent(frame: np.ndarray, t: float, st: float,
                          plate_bg: np.ndarray = None,
                          sub_bass: float = 0.2,
                          show_hud: bool = True) -> np.ndarray:
    """
    Renders the endless rotating fall inside the black gluey meta-object void.
    - Rotates the falling figure continuously (360-deg tumble).
    - Draws rushing upward viscous black tar streaks to convey endless downward velocity.
    - Overlays Truman-Show style surveillance telemetry ('CH 07 // DESCENT FEED').
    """
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2

    if plate_bg is not None:
        # Rotate and slowly breathe the background vortex plate
        angle = (st * 22.0) % 360.0
        scale = 1.15 + 0.08 * math.sin(st * 1.8) + sub_bass * 0.04
        M = cv2.getRotationMatrix2D((cx, cy), angle, scale)
        frame[:] = cv2.warpAffine(plate_bg, M, (w, h), borderMode=cv2.BORDER_REFLECT_101)
        # Darken slightly for void depth
        frame[:] = (frame.astype(np.float32) * 0.72).astype(np.uint8)
    else:
        frame[:, :] = [5, 5, 8]

    # Concentric black gluey void rings rushing outward (illusion of falling deep into hole)
    num_rings = 9
    for i in range(num_rings):
        phase = ((st * 0.85 + i / num_rings) % 1.0)
        r = int((phase ** 1.7) * max(w, h) * 0.75)
        if r > 10:
            thickness = max(1, int(phase * 14))
            shade = int(12 + 28 * (1.0 - phase))
            cv2.ellipse(frame, (cx, cy), (r, int(r * 0.78)), (st * 35.0 + i * 25.0) % 360.0,
                        0, 360, (shade, shade, shade + 6), thickness, cv2.LINE_AA)

    # Viscous black gluey streaks rushing upward past the lens
    rng = np.random.default_rng(42)
    for k in range(22):
        sx = int(rng.uniform(0.05, 0.95) * w)
        speed = rng.uniform(420.0, 780.0)
        sy = int((h - ((st * speed + k * 97) % (h + 180))) + 90)
        length = int(rng.uniform(45, 130))
        cv2.line(frame, (sx, sy), (sx, sy + length), (10, 10, 14), 4, cv2.LINE_AA)
        cv2.line(frame, (sx + 1, sy), (sx + 1, sy + length // 2), (75, 80, 92), 1, cv2.LINE_AA)

    # Rotating falling man silhouette on transparent layer, then warped onto frame
    man_layer = np.zeros((h, w, 3), dtype=np.uint8)
    man_mask = np.zeros((h, w), dtype=np.uint8)
    # Depth oscillation (falling closer/further while tumbling)
    man_scale = max(0.55, 1.35 - 0.04 * st + 0.12 * math.sin(st * 1.4))
    _draw_articulated_falling_man(man_layer, cx, cy, man_scale, t)
    _draw_articulated_falling_man(man_mask, cx, cy, man_scale, t)

    rot_angle = -(st * 58.0) % 360.0
    M_man = cv2.getRotationMatrix2D((cx, cy), rot_angle, 1.0)
    rot_man = cv2.warpAffine(man_layer, M_man, (w, h))
    rot_mask = cv2.warpAffine(man_mask, M_man, (w, h))

    mask_bool = rot_mask > 20
    frame[mask_bool] = rot_man[mask_bool]

    if show_hud:
        # Truman-Show surveillance channel overlay ('CH 07 // DESCENT')
        alt_m = -int(120 + st * 185)
        cv2.rectangle(frame, (int(w * 0.04), int(h * 0.06)), (int(w * 0.34), int(h * 0.13)), (15, 15, 22), -1)
        cv2.rectangle(frame, (int(w * 0.04), int(h * 0.06)), (int(w * 0.34), int(h * 0.13)), (210, 55, 55), 1)
        text_overlay.draw_text(
            frame, "CH 07 // LIVE DESCENT CAM",
            (int(w * 0.055), int(h * 0.095)),
            font_size=int(h * 0.026), fill_color=(245, 70, 70), anchor="lm"
        )
        text_overlay.draw_text(
            frame, f"SUBJECT: BIMAL  |  ALT: {alt_m}m  |  ROT: {int(abs(rot_angle))}°",
            (int(w * 0.04), int(h * 0.92)),
            font_size=int(h * 0.022), fill_color=(180, 235, 185), anchor="lm"
        )

    return frame
