"""
Authentic Indian & Bengali Analog Horror Character Actors & Graphic Shaders for PROJECT NOIR.
Doordarshan (দূরদর্শন) Emergency Alert, Kafka's Metamorphosis in Bengal (বিমলবাবুর রূপান্তর),
Courage the Cowardly Dog in Rural Bengal with Banana Trees (কলা গাছ), and the Elongated Black Tomcat (কালো হুলো বেড়াল).
"""
import math
import cv2
import numpy as np


def draw_doordarshan_logo(frame, cx, cy, radius=55, t=0.0):
    """
    Renders the iconic Doordarshan swirling spiral eye emblem,
    subtly pulsating and distorting with CRT scanline static.
    """
    # Outer central eye pupil
    pulse = 1.0 + 0.08 * math.sin(t * 5.0)
    r = int(radius * pulse)
    
    # Stylized Doordarshan eye spirals
    color_gold = (60, 215, 245)  # Phosphor gold/amber
    color_dark = (20, 15, 25)

    # Central eye core
    cv2.circle(frame, (cx, cy), int(12 * pulse), color_gold, -1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), int(6 * pulse), color_dark, -1, cv2.LINE_AA)

    # Symmetrical spiral arms
    for angle_offset in [0.0, math.pi]:
        pts = []
        for a in np.linspace(0, 1.4 * math.pi, 30):
            ang = a + angle_offset + t * 0.4
            dist = 14 + (a / (1.4 * math.pi)) * (r - 14)
            px = int(cx + math.cos(ang) * dist)
            py = int(cy + math.sin(ang) * dist * 0.82)
            pts.append([px, py])
        if len(pts) > 1:
            cv2.polylines(frame, [np.array(pts, np.int32)], False, color_gold, 4, cv2.LINE_AA)


def draw_doordarshan_alert(frame, t):
    """
    Renders an authentic 1990s Doordarshan (দূরদর্শন) Emergency Interruption.
    Features the Doordarshan spiral logo, Bengali alert typography, and English translation.
    """
    h, w = frame.shape[:2]
    # Deep Doordarshan midnight blue / black CRT raster
    frame[:, :] = [45, 18, 12]  # Dark indigo blue

    # Corrupted Doordarshan logo in upper center
    draw_doordarshan_logo(frame, w // 2, 95, radius=48, t=t)

    # Red emergency banner
    cv2.rectangle(frame, (60, 170), (w - 60, 230), (25, 20, 195), -1)
    cv2.putText(frame, "DOORDARSHAN EMERGENCY BROADCAST -- WEST BENGAL SECTOR",
                (w // 2 - 420, 210), cv2.FONT_HERSHEY_DUPLEX, 0.85, (245, 245, 245), 2, cv2.LINE_AA)

    # Bengali & English dual-language emergency warnings
    lines = [
        "Joruri Sotorkobarta (Emergency Advisory):",
        "Nistobdhopur & Adjacent Rural Districts (Midnapore / Birbhum Border).",
        "",
        "MANDATORY PROCEDURES (COMPLIANCE STRICT):",
        "1. DO NOT ANSWER FAMILIAR VOICES CALLING FROM THE BANANA GROVE (NISHIDAK).",
        "2. EXTINGUISH ALL HURRICANE LANTERNS AND COAL CHULLAHS.",
        "3. IF CHITINOUS BEETLE LIMBS EMERGE FROM YOUR CHEST:",
        "   REMAIN STATIONARY ON THE RED FLOOR. DO NOT RESIST THE EXOSKELETON.",
        "4. DO NOT LOOK DIRECTLY AT THE LUNAR APERTURE IN THE SKY.",
        "",
        "SAMPROCHAR SAMAPTO HOBE NA (THIS BROADCAST WILL NOT CONCLUDE)."
    ]

    chars_to_show = int(t * 38)
    total_chars = 0
    y_pos = 285

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
            is_header = "Joruri" in disp_line or "MANDATORY" in disp_line
            col = (65, 235, 125) if is_header else (225, 225, 225)
            font_scale = 0.68 if is_header else 0.60
            thickness = 2 if is_header else 1
            cv2.putText(frame, disp_line, (90, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, col, thickness, cv2.LINE_AA)
        y_pos += 36


def draw_bengal_banana_trees(frame, t, cx=1100, cy=580, scale=1.0):
    """
    Renders the silhouette of rural Bengal banana trees (kola gachh)
    with their characteristic broad curved leaves and a creaking handpump (tubewell).
    """
    color = (15, 12, 18)

    # Main trunk of the banana plant
    trunk_w = int(18 * scale)
    trunk_h = int(190 * scale)
    cv2.rectangle(frame, (cx - trunk_w // 2, cy - trunk_h), (cx + trunk_w // 2, cy), color, -1)

    # Wide, drooping banana fronds (kola pata)
    frond_configs = [
        (-65, 160, 0.3),
        (-35, 200, 0.8),
        (10, 190, 0.4),
        (50, 180, 0.9),
        (80, 140, 0.2)
    ]
    top_y = cy - trunk_h
    for angle_deg, length, wind_phase in frond_configs:
        sway = math.sin(t * 1.5 + wind_phase) * 6.0
        rad = math.radians(angle_deg + sway)
        end_x = int(cx + math.sin(rad) * length * scale)
        end_y = int(top_y - math.cos(rad) * length * scale * 0.45 + (length * 0.35 * scale))

        # Leaf midrib curve
        ctrl_x = int((cx + end_x) * 0.5 + (20 if angle_deg > 0 else -20) * scale)
        ctrl_y = int(top_y - 45 * scale)

        # Draw leaf blade (ellipse-like curved polygon)
        leaf_pts = [
            [cx, top_y],
            [ctrl_x - int(18 * scale), ctrl_y],
            [end_x, end_y],
            [ctrl_x + int(18 * scale), ctrl_y + int(10 * scale)]
        ]
        cv2.fillPoly(frame, [np.array(leaf_pts, np.int32)], color)

    # Rural Bengal Handpump (Tube-well / চাপাকল) next to the trees
    pump_x = cx - int(120 * scale)
    pump_y = cy
    # Base cylinder
    cv2.rectangle(frame, (pump_x - int(10 * scale), pump_y - int(95 * scale)),
                  (pump_x + int(10 * scale), pump_y), color, -1)
    # Pump handle (angles down)
    handle_sway = int(math.sin(t * 2.0) * 4 * scale)
    cv2.line(frame, (pump_x, pump_y - int(80 * scale)),
             (pump_x - int(55 * scale), pump_y - int(60 * scale) + handle_sway), color, int(4 * scale), cv2.LINE_AA)
    # Water spout
    cv2.line(frame, (pump_x, pump_y - int(45 * scale)),
             (pump_x + int(30 * scale), pump_y - int(45 * scale)), color, int(4 * scale), cv2.LINE_AA)
    # Phantom water drip
    if int(t * 3) % 3 == 0:
        cv2.circle(frame, (pump_x + int(30 * scale), pump_y - int(25 * scale)), 2, (180, 220, 240), -1)


def draw_bimal_kafka_bengal(frame, t, cx=520, cy=560, stage=0.0):
    """
    Renders Bimal Babu's Kafkaesque Metamorphosis:
      - Trapped in an ancestral room over a red-oxide floor ('laal mejhe').
      - Sprouts segmented beetle/scorpion limbs in stop-motion jitter.
    """
    color = (18, 14, 22)
    jitter = math.sin(t * 32.0) * (3.5 * stage)

    # Mosquito net frame above (মশারি)
    moshari_y = cy - 220
    cv2.line(frame, (cx - 160, moshari_y), (cx + 160, moshari_y), (140, 140, 160), 1, cv2.LINE_AA)
    # Drooping fabric lines
    for off in [-120, -60, 0, 60, 120]:
        cv2.line(frame, (cx + off, moshari_y), (cx + off + int(math.sin(t + off) * 4), cy - 40),
                 (70, 65, 80), 1, cv2.LINE_AA)

    # Torso (swelling from human clerk in dhoti to segmented insect carapace)
    torso_w = int(24 + 38 * stage)
    torso_h = int(55 + 24 * stage)
    cv2.ellipse(frame, (int(cx + jitter), int(cy)), (torso_w, torso_h),
                int(12 * math.sin(t * 2.5)), 0, 360, color, -1)

    # Chitin segment ridges across carapace
    if stage > 0.3:
        for ridge_i in range(4):
            ry = int(cy - torso_h * 0.6 + ridge_i * (torso_h * 0.35))
            cv2.ellipse(frame, (int(cx + jitter), ry), (int(torso_w * 0.85), 4), 0, 0, 180, (40, 35, 50), 2)

    # Head (Bimal Babu / Gregor)
    head_y = int(cy - torso_h - 16)
    cv2.circle(frame, (int(cx + jitter), head_y), int(16 + 5 * stage), color, -1)

    # Glowing red cataract / third-eye in the forehead
    if stage > 0.2:
        eye_col = (40, 30, 235)  # Crimson
        cv2.circle(frame, (int(cx + jitter), head_y - 6), 3, eye_col, -1)
        cv2.circle(frame, (int(cx + jitter - 6), head_y + 1), 2, eye_col, -1)
        cv2.circle(frame, (int(cx + jitter + 6), head_y + 1), 2, eye_col, -1)

    # Multi-jointed cockroach/scorpion limbs (পা)
    num_legs = 2 if stage < 0.2 else (6 if stage < 0.6 else 8)
    for leg_i in range(num_legs):
        side = -1 if (leg_i % 2 == 0) else 1
        leg_row = leg_i // 2
        base_y = int(cy - torso_h * 0.4 + leg_row * (torso_h * 0.38))
        base_x = int(cx + side * (torso_w * 0.75))

        # Twitching motion
        twitch = math.sin(t * 22.0 + leg_i * 1.8) * (18.0 * max(0.3, stage))
        knee_x = int(base_x + side * (55 + twitch))
        knee_y = int(base_y - (30 + twitch * 0.4))
        foot_x = int(knee_x + side * (32 - twitch * 0.4))
        foot_y = int(cy + 52 + math.cos(t * 14.0 + leg_i) * 12)

        # Segment 1 & Segment 2
        cv2.line(frame, (base_x, base_y), (knee_x, knee_y), color, 3, cv2.LINE_AA)
        cv2.line(frame, (knee_x, knee_y), (foot_x, foot_y), color, 2, cv2.LINE_AA)
        # Claw tip
        cv2.circle(frame, (foot_x, foot_y), 2, (30, 25, 40), -1)


def draw_bengal_hulo_cat(frame, t, cx=980, cy=600, stretch=0.0):
    """
    Renders the rural Bengal Black Tomcat (কালো হুলো বেড়াল)
    perched on a rustic bamboo fence (বাঁশের বেড়া) near the banana trees.
    Its neck stretches unnaturally into the purple sky.
    """
    color = (12, 10, 16)

    # Rural Bamboo Fence (বাঁশের বেড়া)
    for fx in range(cx - 90, cx + 110, 30):
        cv2.line(frame, (fx, cy), (fx, cy + 140), (45, 38, 28), 5, cv2.LINE_AA)
    cv2.line(frame, (cx - 100, cy + 35), (cx + 120, cy + 35), (55, 45, 32), 4, cv2.LINE_AA)
    cv2.line(frame, (cx - 100, cy + 85), (cx + 120, cy + 85), (55, 45, 32), 4, cv2.LINE_AA)

    # Cat body on the bamboo rail
    body_y = int(cy + 18)
    cv2.ellipse(frame, (cx, body_y), (24, 16), -8, 0, 360, color, -1)

    # Curled feline tail
    tail_pts = []
    for i in range(14):
        tx = int(cx - 24 - i * 3 + math.sin(t * 4.5 + i * 0.25) * 5)
        ty = int(body_y - i * 2 + math.cos(t * 3.5 + i * 0.2) * 4)
        tail_pts.append([tx, ty])
    if len(tail_pts) > 1:
        cv2.polylines(frame, [np.array(tail_pts, np.int32)], False, color, 3, cv2.LINE_AA)

    # Elastic Elongated Neck rising into the sky
    head_y = int(body_y - 28 - stretch * 360)
    neck_w = int(max(4, 15 - stretch * 9))
    cv2.line(frame, (cx, body_y - 10), (cx, head_y + 10), color, neck_w, cv2.LINE_AA)

    # Cat Head & Pointed Ears
    cv2.circle(frame, (cx, head_y), 18, color, -1)
    ear_l = np.array([[cx - 14, head_y - 4], [cx - 6, head_y - 24], [cx - 2, head_y - 10]], np.int32)
    ear_r = np.array([[cx + 14, head_y - 4], [cx + 6, head_y - 24], [cx + 2, head_y - 10]], np.int32)
    cv2.fillPoly(frame, [ear_l, ear_r], color)

    # Glowing Toxic Yellow Cat Eyes (Maa Shasthi omen)
    eye_glow = (45, 235, 245)  # Eerie phosphorescent amber/yellow
    cv2.ellipse(frame, (cx - 6, head_y - 2), (4, 7), 10, 0, 360, eye_glow, -1)
    cv2.ellipse(frame, (cx + 6, head_y - 2), (4, 7), -10, 0, 360, eye_glow, -1)
    # Slit pupils
    cv2.line(frame, (cx - 6, head_y - 7), (cx - 6, head_y + 3), (10, 10, 10), 2)
    cv2.line(frame, (cx + 6, head_y - 7), (cx + 6, head_y + 3), (10, 10, 10), 2)
