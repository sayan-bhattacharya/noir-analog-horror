"""
Procedural surreal character actors and emergency graphics for PROJECT NOIR.
Stickman Kafka metamorphosis, Courage surreal windmill, elongated shadow cat, and EAS emergency cards.
"""
import math
import cv2
import numpy as np


def draw_eas_card(frame, t, phase=0.0):
    """
    Renders an authentic 1994 Emergency Action Notification (EAN) screen.
    Includes blue NOAA background, red warning header, and typewriter text.
    """
    h, w = frame.shape[:2]
    # Blue emergency card background
    frame[:, :] = [135, 30, 20]  # Deep blue in BGR

    # Red emergency header bar
    cv2.rectangle(frame, (40, 40), (w - 40, 110), (30, 20, 190), -1)
    cv2.putText(frame, "EMERGENCY ACTION NOTIFICATION", (w // 2 - 380, 85),
                cv2.FONT_HERSHEY_DUPLEX, 1.1, (240, 240, 240), 2, cv2.LINE_AA)

    lines = [
        "A CIVIL DANGER WARNING HAS BEEN ISSUED FOR:",
        "NOWHERE TOWNSHIP AND ADJACENT UNINHABITED SECTORS.",
        "",
        "MANDATORY PROCEDURES (COMPLIANCE STRICT):",
        "1. EXTINGUISH ALL LAMPS AND CANDLES.",
        "2. DO NOT COMMUNICATE WITH DOMESTIC ANIMALS.",
        "3. IF EXTRA SEGMENTED LIMBS GROW BENEATH YOUR RIBS:",
        "   DO NOT RESIST THE CHITIN. REMAIN FACING THE WALL.",
        "4. DO NOT LOOK UPON THE CELESTIAL EYE.",
        "",
        "THIS TRANSMISSION WILL REPEAT UNTIL TERMINATION."
    ]

    # Typewriter effect based on time
    chars_to_show = int(t * 35)
    total_chars = 0
    y_pos = 180

    for line in lines:
        if total_chars + len(line) <= chars_to_show:
            disp_line = line
            total_chars += len(line)
        elif total_chars < chars_to_show:
            disp_line = line[:chars_to_show - total_chars]
            total_chars = chars_to_show
        else:
            disp_line = ""

        if disp_line:
            cv2.putText(frame, disp_line, (70, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (230, 230, 230), 2, cv2.LINE_AA)
        y_pos += 42


def draw_windmill(frame, t, cx=1480, cy=640, scale=1.0):
    """Draws the iconic Courage the Cowardly Dog crooked iron windmill."""
    # Tower struts (black silhouette)
    w_top = int(14 * scale)
    w_bot = int(48 * scale)
    h_tower = int(260 * scale)

    pts = np.array([
        [cx - w_top, cy - h_tower],
        [cx + w_top, cy - h_tower],
        [cx + w_bot, cy],
        [cx - w_bot, cy]
    ], np.int32)
    cv2.fillPoly(frame, [pts], (15, 12, 18))

    # Cross beams
    for frac in [0.25, 0.5, 0.75]:
        y_beam = int(cy - h_tower * (1.0 - frac))
        x_left = int(cx - w_bot + (w_bot - w_top) * frac)
        x_right = int(cx + w_bot - (w_bot - w_top) * frac)
        cv2.line(frame, (x_left, y_beam), (x_right, y_beam), (12, 10, 15), max(1, int(2 * scale)))

    # Rotating blades (erratic, slightly bent)
    hub_x, hub_y = cx, cy - h_tower
    cv2.circle(frame, (hub_x, hub_y), int(10 * scale), (20, 15, 25), -1)

    blade_len = int(120 * scale)
    angle_base = t * 1.8  # slow, eerie rotation
    for i in range(4):
        ang = angle_base + i * (math.pi / 2.0)
        # 3rd blade is missing/broken (Courage detail!)
        if i == 2:
            continue
        bx = int(hub_x + math.cos(ang) * blade_len)
        by = int(hub_y + math.sin(ang) * blade_len)
        cv2.line(frame, (hub_x, hub_y), (bx, by), (12, 10, 16), max(1, int(4 * scale)))
        # Blade fin
        cv2.circle(frame, (bx, by), int(14 * scale), (15, 12, 18), -1)


def draw_gregor_kafka(frame, t, cx=640, cy=720, stage=0.0):
    """
    Renders Gregor Samsa's stickman transformation:
      - stage 0.0: Vulnerable stickman lying on bed
      - stage 0.5: Torso swelling, multiple jointed legs twitching
      - stage 1.0: Full arachnid/centipede vermin scurrying across floor
    """
    color = (18, 15, 20)
    jitter = math.sin(t * 32.0) * (3.0 * stage)

    # Torso
    torso_w = int(24 + 40 * stage)
    torso_h = int(60 + 20 * stage)
    cv2.ellipse(frame, (int(cx + jitter), int(cy)), (torso_w, torso_h),
                int(15 * math.sin(t * 2.0)), 0, 360, color, -1)

    # Head
    head_y = int(cy - torso_h - 18)
    cv2.circle(frame, (int(cx + jitter), head_y), int(16 + 6 * stage), color, -1)

    # Glowing uncanny white/red pupil
    if stage > 0.3:
        eye_color = (40, 40, 240) if stage > 0.7 else (220, 220, 220)
        cv2.circle(frame, (int(cx + jitter - 5), head_y - 2), 3, eye_color, -1)
        cv2.circle(frame, (int(cx + jitter + 5), head_y - 2), 3, eye_color, -1)

    # Chitinous Legs (sprouts from 2 to 8 segmented legs)
    num_legs = 2 if stage < 0.2 else (4 if stage < 0.5 else 8)
    for leg_i in range(num_legs):
        side = -1 if (leg_i % 2 == 0) else 1
        leg_idx = leg_i // 2
        base_y = int(cy - torso_h * 0.5 + leg_idx * (torso_h / 2.0))
        base_x = int(cx + side * (torso_w * 0.8))

        # Leg twitching cycle
        twitch = math.sin(t * 18.0 + leg_i * 1.5) * (14.0 * max(0.2, stage))
        knee_x = int(base_x + side * (50 + twitch))
        knee_y = int(base_y - (25 + twitch * 0.5))
        foot_x = int(knee_x + side * (30 - twitch * 0.5))
        foot_y = int(cy + 45 + (10 * math.cos(t * 12.0 + leg_i)))

        # Segment 1 (Hip -> Knee)
        cv2.line(frame, (base_x, base_y), (knee_x, knee_y), color, 3, cv2.LINE_AA)
        # Segment 2 (Knee -> Foot)
        cv2.line(frame, (knee_x, knee_y), (foot_x, foot_y), color, 2, cv2.LINE_AA)
        # Foot claw point
        cv2.circle(frame, (foot_x, foot_y), 2, color, -1)


def draw_surreal_cat(frame, t, cx=1120, cy=740, stretch=0.0):
    """
    Renders the uncanny Courage black cat:
    Its neck stretches smoothly upwards into the sky while paws stay rooted.
    """
    color = (12, 10, 15)

    # Fence post
    cv2.rectangle(frame, (cx - 16, cy), (cx + 16, cy + 180), (25, 20, 30), -1)

    # Paws on the post
    cv2.ellipse(frame, (cx - 10, cy + 4), (8, 4), 0, 0, 360, color, -1)
    cv2.ellipse(frame, (cx + 10, cy + 4), (8, 4), 0, 0, 360, color, -1)

    # Body
    body_y = int(cy - 20)
    cv2.ellipse(frame, (cx, body_y), (22, 16), -10, 0, 360, color, -1)

    # Curled tail
    tail_pts = []
    for i in range(12):
        tx = int(cx - 20 - i * 3 + math.sin(t * 4.0 + i * 0.3) * 6)
        ty = int(body_y - i * 2 + math.cos(t * 3.0 + i * 0.2) * 4)
        tail_pts.append([tx, ty])
    if len(tail_pts) > 1:
        cv2.polylines(frame, [np.array(tail_pts, np.int32)], False, color, 3, cv2.LINE_AA)

    # Elastic Elongated Neck
    head_y = int(body_y - 25 - stretch * 380)  # Stretches up into the upper sky!
    neck_w = int(max(4, 14 - stretch * 8))
    cv2.line(frame, (cx, body_y - 10), (cx, head_y + 12), color, neck_w, cv2.LINE_AA)

    # Cat Head
    head_size = int(18)
    cv2.circle(frame, (cx, head_y), head_size, color, -1)

    # Pointed Cat Ears
    ear_l = np.array([[cx - 14, head_y - 4], [cx - 6, head_y - 22], [cx - 2, head_y - 10]], np.int32)
    ear_r = np.array([[cx + 14, head_y - 4], [cx + 6, head_y - 22], [cx + 2, head_y - 10]], np.int32)
    cv2.fillPoly(frame, [ear_l, ear_r], color)

    # Glowing Cathode Phosphor Eyes
    eye_glow = (50, 240, 180)  # Toxic phosphor green
    cv2.ellipse(frame, (cx - 6, head_y - 2), (4, 7), 10, 0, 360, eye_glow, -1)
    cv2.ellipse(frame, (cx + 6, head_y - 2), (4, 7), -10, 0, 360, eye_glow, -1)
    # Slit pupils
    cv2.line(frame, (cx - 6, head_y - 7), (cx - 6, head_y + 3), (10, 10, 10), 2)
    cv2.line(frame, (cx + 6, head_y - 7), (cx + 6, head_y + 3), (10, 10, 10), 2)


def draw_spider_swarm(frame, t, count=16):
    """Renders small procedural spiders scurrying across the CRT glass surface."""
    h, w = frame.shape[:2]
    for i in range(count):
        # Deterministic pseudo-random scurry based on index and time
        phase = i * 47.13
        sx = int(((phase * 123 + t * (60 + (i % 5) * 25)) % (w + 100)) - 50)
        sy = int(((phase * 89 + math.sin(t * 8.0 + i) * 35) % (h + 80)) - 40)

        # Micro body
        cv2.circle(frame, (sx, sy), 3, (12, 10, 15), -1)
        # Micro legs
        for leg_a in range(6):
            ang = leg_a * (math.pi / 3.0) + math.sin(t * 22.0 + leg_a) * 0.4
            lx = int(sx + math.cos(ang) * 8)
            ly = int(sy + math.sin(ang) * 8)
            cv2.line(frame, (sx, sy), (lx, ly), (12, 10, 15), 1)
