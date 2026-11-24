"""
Corrupted Television News Broadcast Overlay Engine — Between the Notes Network.
80% Believable News Channel • 20% Creeping Cosmic Horror.

Layout Hierarchy:
- Top-Left: Angled Red Parallelogram 'BREAKING NEWS // BETWEEN THE NOTES' banner
- Top-Right: Official Between the Notes Channel Bug with 1.2s pulsing '• LIVE' -> changes to 'RECORDED'
- Signal Integrity: Telemetry indicator ('SIGNAL INTEGRITY: 97%' -> dropping to 12%)
- Information Icon: Rotating 3D wireframe globe on left (morphs into dilated cosmic pupil)
- Primary Headline: Bold Bengali high-contrast headline ('গ্রামের জঙ্গল রহস্য, জেলায় ছড়াল আতঙ্ক')
- Sub-Headline: Charcoal bar with secondary line ('বাঁশবনে অদ্ভুত শব্দ, এলাকায় চাঞ্চল্য')
- Upper Pill: '(রাত্রি ৩:১২ | ০০০৩)'
- Transmission Metadata: Weather ('24°C') & steady digital clock ('03:12 AM') that ticks normally
- Ticker: Smoothly scrolling bottom ribbon with Between the Notes promotional and horror bulletins
"""
import math
import os
import cv2
import numpy as np
from .. import text_overlay

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(ROOT, "assets", "logo-circle.png")
_CACHED_LOGO = None


def get_logo_image():
    global _CACHED_LOGO
    if _CACHED_LOGO is None and os.path.exists(LOGO_PATH):
        try:
            _CACHED_LOGO = cv2.imread(LOGO_PATH, cv2.IMREAD_UNCHANGED)
        except Exception:
            _CACHED_LOGO = None
    return _CACHED_LOGO


def draw_wireframe_globe(frame: np.ndarray, cx: int, cy: int, radius: int, t: float, corrupted: bool = False):
    """
    Draws rotating 3D wireframe globe.
    When corrupted, it morphs into an unholy dilated pupil that stares out of the screen.
    """
    if corrupted:
        # Eye / Cosmic Pupil anomaly
        cv2.circle(frame, (cx, cy), radius, (230, 230, 235), 2, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), radius - 2, (18, 12, 16), -1)
        # Dilating red iris
        iris_r = int(radius * (0.55 + 0.15 * math.sin(t * 8.0)))
        cv2.circle(frame, (cx, cy), iris_r, (235, 45, 45), -1, cv2.LINE_AA)
        # Pitch black slit pupil
        cv2.ellipse(frame, (cx, cy), (max(2, int(iris_r * 0.25)), int(iris_r * 0.85)), 0, 0, 360, (0, 0, 0), -1, cv2.LINE_AA)
        return

    # Normal procedural 3D wireframe globe
    color = (240, 235, 230)
    cv2.circle(frame, (cx, cy), radius, color, 1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), radius - 1, (110, 24, 28), -1)

    for lat_deg in [-45, 0, 45]:
        r_lat = radius * math.cos(math.radians(lat_deg))
        y_offset = int(radius * math.sin(math.radians(lat_deg)) * 0.45)
        axes = (max(2, int(r_lat)), max(1, int(radius * 0.22)))
        cv2.ellipse(frame, (cx, cy + y_offset), axes, 0, 0, 360, color, 1, cv2.LINE_AA)

    rot = (t * 1.6) % math.pi
    for m_idx in range(4):
        ang = rot + m_idx * (math.pi / 4.0)
        x_squash = math.sin(ang)
        if abs(x_squash) > 0.06:
            axes = (max(2, int(radius * abs(x_squash))), radius)
            cv2.ellipse(frame, (cx, cy), axes, 0, 0, 360, color, 1, cv2.LINE_AA)


def draw_corrupted_news_overlay(frame: np.ndarray,
                                t: float,
                                headline: str = "গ্রামের জঙ্গল রহস্য, জেলায় ছড়াল আতঙ্ক",
                                sub_headline: str = "বাঁশবনে অদ্ভুত শব্দ, এলাকায় চাঞ্চল্য",
                                ticker_text: str = "নিস্তব্ধপুরে সান্ধ্য আইন জারি  |  বাঁশবনে আলো জ্বালাবেন না  |  অচেনা কণ্ঠে সাড়া নিষেধ  |  Between the Notes এক্সক্লুসিভ লাইভ আপডেট",
                                sector_code: str = "রাত ৩:১২ | ০০০৩",
                                clock_str: str = "03:12 AM",
                                weather_str: str = "24°C",
                                channel_name: str = "Between the Notes",
                                signal_integrity: int = 97,
                                is_recorded: bool = False,
                                globe_corrupted: bool = False) -> np.ndarray:
    """
    Renders the complete 80/20 believable-to-corrupted news broadcast graphics package,
    featuring official Between the Notes channel branding for promotion and eerie realism.
    """
    h, w = frame.shape[:2]

    # Safe title margins
    margin_x = int(w * 0.04)
    margin_top = int(h * 0.06)
    margin_bottom = int(h * 0.05)

    # -------------------------------------------------------------------------
    # 1. TOP-LEFT: 'BREAKING NEWS // BETWEEN THE NOTES' Parallelogram Badge
    # -------------------------------------------------------------------------
    badge_w = int(w * 0.36)
    badge_h = int(h * 0.068)
    bx1 = margin_x
    by1 = margin_top

    shear = int(badge_h * 0.45)
    pts_badge = np.array([
        [bx1, by1],
        [bx1 + badge_w, by1],
        [bx1 + badge_w - shear, by1 + badge_h],
        [bx1 - shear, by1 + badge_h]
    ], np.int32)
    cv2.fillPoly(frame, [pts_badge], (185, 20, 25))
    cv2.polylines(frame, [pts_badge], True, (240, 240, 240), 1, cv2.LINE_AA)

    # White accent slashes
    cv2.line(frame, (bx1 + badge_w - shear - 10, by1 + 4), (bx1 + badge_w - shear * 2 - 10, by1 + badge_h - 4), (250, 250, 250), 2, cv2.LINE_AA)
    cv2.line(frame, (bx1 + badge_w - shear - 4, by1 + 4), (bx1 + badge_w - shear * 2 - 4, by1 + badge_h - 4), (250, 250, 250), 2, cv2.LINE_AA)

    text_overlay.draw_text(
        frame, "BREAKING NEWS // BETWEEN THE NOTES",
        (bx1 + int(badge_w * 0.44), by1 + badge_h // 2),
        font_size=int(badge_h * 0.44),
        fill_color=(255, 255, 255),
        anchor="mm"
    )

    # -------------------------------------------------------------------------
    # 2. TOP-RIGHT: Between the Notes Channel Bug & '• LIVE' / 'RECORDED'
    # -------------------------------------------------------------------------
    chan_w = int(w * 0.17)
    chan_h = int(h * 0.068)
    cx2 = w - margin_x
    cx1 = cx2 - chan_w
    cy1 = margin_top

    # Channel box with Between the Notes styling
    cv2.rectangle(frame, (cx1, cy1), (cx2, cy1 + chan_h), (18, 16, 42), -1)
    cv2.rectangle(frame, (cx1, cy1), (cx2, cy1 + chan_h), (235, 215, 60), 1)

    # Composite circular logo icon inside bug if available
    logo_img = get_logo_image()
    logo_icon_w = 0
    if logo_img is not None:
        icon_size = int(chan_h * 0.80)
        lx1 = cx1 + 6
        ly1 = cy1 + (chan_h - icon_size) // 2
        lx2 = lx1 + icon_size
        ly2 = ly1 + icon_size
        resized_icon = cv2.resize(logo_img, (icon_size, icon_size), interpolation=cv2.INTER_AREA)
        if resized_icon.shape[2] == 4:
            alpha = (resized_icon[:, :, 3] / 255.0)[:, :, np.newaxis]
            bgr = resized_icon[:, :, :3]
            frame[ly1:ly2, lx1:lx2] = (frame[ly1:ly2, lx1:lx2] * (1.0 - alpha) + bgr * alpha).astype(np.uint8)
        else:
            frame[ly1:ly2, lx1:lx2] = resized_icon
        logo_icon_w = icon_size + 8

    # Channel Name
    text_overlay.draw_text(
        frame, channel_name,
        (cx1 + logo_icon_w + (chan_w - logo_icon_w) // 2, cy1 + chan_h // 2),
        font_size=int(chan_h * 0.38),
        fill_color=(245, 215, 60),
        anchor="mm"
    )

    # Status pill underneath: switches from '• LIVE' to 'RECORDED' at chilling moments
    live_y = cy1 + chan_h + 4
    live_h = int(h * 0.034)

    if is_recorded:
        cv2.rectangle(frame, (cx1, live_y), (cx2, live_y + live_h), (50, 50, 55), -1)
        text_overlay.draw_text(
            frame, "RECORDED",
            (cx1 + chan_w // 2, live_y + live_h // 2),
            font_size=int(live_h * 0.50),
            fill_color=(220, 220, 225),
            anchor="mm"
        )
    else:
        # LIVE pill with 1.2s pulse cadence
        cv2.rectangle(frame, (cx1, live_y), (cx2, live_y + live_h), (185, 20, 25), -1)
        cycle_phase = (t % 1.2) / 1.2
        is_lit = cycle_phase < 0.65
        dot_color = (255, 255, 255) if is_lit else (140, 40, 45)
        cv2.circle(frame, (cx1 + int(chan_w * 0.28), live_y + live_h // 2), int(live_h * 0.22), dot_color, -1, cv2.LINE_AA)
        text_overlay.draw_text(
            frame, "LIVE",
            (cx1 + int(chan_w * 0.58), live_y + live_h // 2),
            font_size=int(live_h * 0.55),
            fill_color=(255, 255, 255),
            anchor="mm"
        )

    # Signal Integrity telemetry right below LIVE pill
    sig_y = live_y + live_h + 4
    sig_col = (90, 220, 110) if signal_integrity > 70 else ((240, 180, 50) if signal_integrity > 30 else (240, 60, 60))
    text_overlay.draw_text(
        frame, f"SIGNAL: {signal_integrity}%",
        (cx2, sig_y + 4),
        font_size=int(h * 0.019),
        fill_color=sig_col,
        anchor="rm"
    )

    # -------------------------------------------------------------------------
    # 3. LOWER-THIRD NEWS PACKAGE
    # -------------------------------------------------------------------------
    lt_bottom = h - margin_bottom
    ticker_h = int(h * 0.048)
    sub_h = int(h * 0.052)
    main_h = int(h * 0.082)
    total_lt_h = ticker_h + sub_h + main_h

    lt_y_start = lt_bottom - total_lt_h
    lt_x1 = margin_x
    lt_x2 = w - margin_x

    # 3A. Small Tag Pill: '(রাত্রি ৩ | ০০০০ ৩)'
    tag_w = int(w * 0.24)
    tag_h = int(h * 0.042)
    tag_y = lt_y_start - tag_h + 2
    pts_tag = np.array([
        [lt_x1 + 10, tag_y],
        [lt_x1 + tag_w, tag_y],
        [lt_x1 + tag_w - 12, tag_y + tag_h],
        [lt_x1, tag_y + tag_h]
    ], np.int32)
    cv2.fillPoly(frame, [pts_tag], (235, 235, 235))
    cv2.line(frame, (lt_x1 + 10, tag_y), (lt_x1, tag_y + tag_h), (185, 20, 25), 4)
    text_overlay.draw_text(
        frame, f"({sector_code})",
        (lt_x1 + tag_w // 2, tag_y + tag_h // 2),
        font_size=int(tag_h * 0.48),
        fill_color=(18, 18, 24),
        anchor="mm"
    )

    # 3B. Globe Icon Box
    globe_w = int(total_lt_h * 0.65)
    cv2.rectangle(frame, (lt_x1, lt_y_start), (lt_x1 + globe_w, lt_y_start + main_h + sub_h), (95, 12, 16), -1)
    cv2.rectangle(frame, (lt_x1, lt_y_start), (lt_x1 + globe_w, lt_y_start + main_h + sub_h), (190, 30, 35), 2)
    draw_wireframe_globe(frame, lt_x1 + globe_w // 2, lt_y_start + (main_h + sub_h) // 2, int(globe_w * 0.38), t, corrupted=globe_corrupted)

    # 3C. Right Side Telemetry Box (Weather + Digital Clock)
    telemetry_w = int(w * 0.125)
    tx1 = lt_x2 - telemetry_w
    tx2 = lt_x2

    # Weather Box
    cv2.rectangle(frame, (tx1, lt_y_start), (tx2, lt_y_start + main_h), (24, 26, 30), -1)
    cv2.rectangle(frame, (tx1, lt_y_start), (tx2, lt_y_start + main_h), (70, 75, 85), 1)

    wx_cx = tx1 + int(telemetry_w * 0.28)
    wx_cy = lt_y_start + main_h // 2
    cv2.circle(frame, (wx_cx, wx_cy), int(main_h * 0.18), (220, 225, 230), -1)
    cv2.circle(frame, (wx_cx - 8, wx_cy + 2), int(main_h * 0.14), (220, 225, 230), -1)
    cv2.circle(frame, (wx_cx + 8, wx_cy + 2), int(main_h * 0.14), (220, 225, 230), -1)
    for drop_x in [-6, 0, 6]:
        cv2.line(frame, (wx_cx + drop_x, wx_cy + 10), (wx_cx + drop_x - 2, wx_cy + 16), (90, 190, 240), 1, cv2.LINE_AA)

    text_overlay.draw_text(
        frame, weather_str,
        (tx1 + int(telemetry_w * 0.68), lt_y_start + main_h // 2),
        font_size=int(main_h * 0.38),
        fill_color=(245, 245, 245),
        anchor="mm"
    )

    # Clock Box
    cv2.rectangle(frame, (tx1, lt_y_start + main_h), (tx2, lt_y_start + main_h + sub_h), (180, 18, 22), -1)
    cv2.rectangle(frame, (tx1, lt_y_start + main_h), (tx2, lt_y_start + main_h + sub_h), (230, 230, 235), 1)
    text_overlay.draw_text(
        frame, clock_str,
        (tx1 + telemetry_w // 2, lt_y_start + main_h + sub_h // 2),
        font_size=int(sub_h * 0.52),
        fill_color=(255, 255, 255),
        anchor="mm"
    )

    # 3D. Primary Crimson Breaking News Headline Bar
    content_x1 = lt_x1 + globe_w
    content_x2 = tx1

    cv2.rectangle(frame, (content_x1, lt_y_start), (content_x2, lt_y_start + main_h), (170, 16, 20), -1)
    cv2.rectangle(frame, (content_x1, lt_y_start), (content_x2, lt_y_start + main_h), (220, 45, 50), 2)
    text_overlay.draw_text(
        frame, headline,
        (content_x1 + int((content_x2 - content_x1) * 0.03), lt_y_start + main_h // 2),
        font_size=int(main_h * 0.56),
        fill_color=(255, 255, 255),
        max_width=int((content_x2 - content_x1) * 0.94),
        anchor="lm"
    )

    # 3E. Dark Slate Sub-Headline Bar
    cv2.rectangle(frame, (content_x1, lt_y_start + main_h), (content_x2, lt_y_start + main_h + sub_h), (18, 20, 24), -1)
    cv2.rectangle(frame, (content_x1, lt_y_start + main_h), (content_x2, lt_y_start + main_h + sub_h), (50, 55, 60), 1)
    text_overlay.draw_text(
        frame, sub_headline,
        (content_x1 + int((content_x2 - content_x1) * 0.03), lt_y_start + main_h + sub_h // 2),
        font_size=int(sub_h * 0.54),
        fill_color=(240, 240, 240),
        max_width=int((content_x2 - content_x1) * 0.94),
        anchor="lm"
    )

    # -------------------------------------------------------------------------
    # 4. BOTTOM TICKER RIBBON ('BETWEEN THE NOTES // TOP STORIES')
    # -------------------------------------------------------------------------
    ticker_y = lt_y_start + main_h + sub_h
    cv2.rectangle(frame, (lt_x1, ticker_y), (lt_x2, ticker_y + ticker_h), (242, 242, 242), -1)
    cv2.rectangle(frame, (lt_x1, ticker_y), (lt_x2, ticker_y + ticker_h), (200, 200, 200), 1)

    # 'BETWEEN THE NOTES' Dark Navy header
    ts_w = int(w * 0.16)
    cv2.rectangle(frame, (lt_x1, ticker_y), (lt_x1 + ts_w, ticker_y + ticker_h), (18, 22, 38), -1)
    text_overlay.draw_text(
        frame, "BETWEEN THE NOTES",
        (lt_x1 + ts_w // 2, ticker_y + ticker_h // 2),
        font_size=int(ticker_h * 0.40),
        fill_color=(245, 215, 60),
        anchor="mm"
    )

    # Ticker text with subtle analog pause
    ticker_display_w = lt_x2 - (lt_x1 + ts_w + 10)
    text_overlay.draw_text(
        frame, ticker_text,
        (lt_x1 + ts_w + 12, ticker_y + ticker_h // 2),
        font_size=int(ticker_h * 0.44),
        fill_color=(25, 25, 30),
        max_width=ticker_display_w,
        anchor="lm"
    )

    return frame
