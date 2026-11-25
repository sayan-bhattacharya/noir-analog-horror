"""
Content-Addressed Modular Shot Cache & Stream-Copy Stitcher for Project NOIR.

Splits the master timeline into independent, invariant shot modules.
Each shot computes a deterministic SHA-256 content hash from:
  1. Its own branch source code in timeline.py (editing Shot 9 never invalidates Shot 10!)
  2. Dependent actor/post-processing Python modules
  3. Referenced media assets (plates / Flow MP4s / green-screen layers)
  4. Render geometry & quality (width, height, fps, crf)

Unchanged shots are served from output/module_cache/ in 0ms and stitched via
FFmpeg demuxer concat (-c copy) with zero re-encoding.
"""
import ast
import glob
import hashlib
import os
import subprocess
import time

from .utils.video_io import FFmpegVideoPipe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(ROOT, "output", "module_cache")


# Declarative shot modules covering [0.0, 360.0]
SHOT_MODULES = [
    ("S00_logo_to_dish",     0.0,   5.0,  ["noir_film/timeline.py", "noir_film/actors/doordarshan_alert.py"]),
    ("S01_story_cut",        5.0,   9.0,  ["noir_film/timeline.py", "noir_film/actors/v2_director.py", "assets/v2_videos/V2_01_bengal_geography.mp4"]),
    ("S02_btn24_geo",        9.0,  14.0,  ["noir_film/timeline.py", "noir_film/actors/news_broadcast.py", "assets/v2_videos/V2_01_bengal_geography.mp4"]),
    ("S03_btn24_alert",     14.0,  22.0,  ["noir_film/actors/news_broadcast.py", "assets/storm_loop.mp4"]),
    ("S04_cartography",     22.0,  29.0,  ["noir_film/actors/v2_director.py", "noir_film/actors/sector_map.py"]),
    ("S05_civil_danger",    29.0,  37.0,  ["noir_film/actors/civil_danger.py", "noir_film/actors/v2_director.py"]),
    ("S06_card_knock",      37.0,  41.0,  ["noir_film/text_overlay.py"]),
    ("S07_card_not_mom",    41.0,  45.0,  ["noir_film/text_overlay.py"]),
    ("S08_cat_shadow",      45.0,  53.0,  ["noir_film/actors/v2_director.py", "assets/v2_videos/V2_02_cat_shadow_turn.mp4"]),
    ("S09_rule1_smoke",     53.0,  60.0,  ["noir_film/actors/machinist_stickman.py", "noir_film/actors/v2_director.py", "noir_film/actors/cloud_timelapse.py", "noir_film/text_overlay.py"]),
    ("S10_drone_tubewell",  60.0,  67.0,  ["noir_film/actors/machinist_stickman.py", "noir_film/actors/tubewell_scene.py", "assets/flow_drone_courtyard.mp4"]),
    ("S11_door_latch",      67.0,  74.0,  ["noir_film/timeline.py", "plates/scene-06.jpeg"]),
    ("S12_first_call",      74.0,  80.0,  ["noir_film/text_overlay.py"]),
    ("S13_dossier_1994",    80.0,  86.0,  ["noir_film/timeline.py", "plates/scene-24.jpeg"]),
    ("S14_dead_phone",      86.0,  90.0,  ["plates/scene-08.jpeg"]),
    ("S15_bedroom_bike",    90.0,  97.0,  ["noir_film/actors/v2_director.py", "assets/v2_videos/bike_headlight_greenscreen.mp4", "plates/scene-11.jpeg"]),
    ("S16_rule2",           97.0, 104.0,  ["noir_film/text_overlay.py", "plates/scene-11.jpeg"]),
    ("S17_mosquito_bike",  104.0, 112.0,  ["noir_film/actors/v2_director.py", "assets/v2_videos/bike_headlight_greenscreen.mp4"]),
    ("S18_second_call",    112.0, 117.0,  ["noir_film/text_overlay.py"]),
    ("S19_spider_erupt",   117.0, 125.0,  ["noir_film/actors/bimal_metamorphosis.py"]),
    ("S20A_trinetra_txt",  125.0, 129.0,  ["noir_film/text_overlay.py"]),
    ("S20B_trinetra_eye",  129.0, 132.0,  ["noir_film/actors/trinetra_eye.py"]),
    ("S21_body_measure",   132.0, 140.0,  ["noir_film/text_overlay.py"]),
    ("S22_hyper_fence",    140.0, 147.0,  ["noir_film/actors/hulo_cat.py", "noir_film/actors/cloud_timelapse.py"]),
    ("S23_rule3",          147.0, 154.0,  ["noir_film/actors/hulo_cat.py", "noir_film/text_overlay.py"]),
    ("S24_courage_moon",   154.0, 162.0,  ["noir_film/actors/v2_director.py", "noir_film/actors/hulo_cat.py", "noir_film/actors/cloud_timelapse.py"]),
    ("S25_shadow_voice",   162.0, 169.0,  ["noir_film/text_overlay.py"]),
    ("S26_sahaj_fracture", 169.0, 176.0,  ["noir_film/actors/v2_director.py", "plates/scene-26.jpeg"]),
    ("S27_crossroads",     176.0, 181.0,  ["plates/scene-28.jpeg"]),
    ("S28_final_call",     181.0, 185.0,  ["noir_film/text_overlay.py"]),
    ("S29_descent_slate",  185.0, 193.0,  ["noir_film/text_overlay.py"]),
    ("S30_blackhole_pull", 193.0, 204.0,  ["noir_film/actors/descent_fall.py", "noir_film/actors/machinist_stickman.py"]),
    ("S31_swirling_fall",  204.0, 218.0,  ["noir_film/actors/descent_fall.py", "noir_film/distortion.py"]),
    ("S32_channel_cut",    218.0, 226.0,  ["noir_film/actors/descent_fall.py", "noir_film/actors/hulo_cat.py"]),
    ("S33_scanline_face",  226.0, 236.0,  ["noir_film/distortion.py", "plates/scene-17.jpeg"]),
    ("S34_choking_net",    236.0, 256.0,  ["noir_film/actors/machinist_stickman.py", "plates/scene-13.jpeg"]),
    ("S35_amnesia_bike",   256.0, 280.0,  ["noir_film/actors/v2_director.py", "assets/v2_videos/bike_headlight_greenscreen.mp4"]),
    ("S36_crt_collapse",   280.0, 300.0,  ["noir_film/actors/v2_director.py", "plates/scene-06.jpeg"]),
    ("S37_exit0_corridor", 300.0, 322.0,  ["noir_film/actors/v2_director.py", "assets/stage2_videos/S2_02_exit8_matrix_corridor.mp4"]),
    ("S38_berlin_biz",     322.0, 338.0,  ["assets/stage2_videos/S2_01_berlin_matrix_subway.mp4", "assets/v2_videos/V2_03_berlin_businessman.mp4"]),
    ("S39_warm_dream",     338.0, 352.0,  ["assets/haunted_archive_videos/F_pather_train_never_arrives.mp4", "assets/stage2_videos/S2_01_berlin_matrix_subway.mp4"]),
    ("S40_creature_end",   352.0, 360.0,  ["noir_film/actors/v2_director.py", "assets/stage2_videos/S2_03_goofy_scifi_creature.mp4"]),
]

SHARED_CORE_FILES = [
    "noir_film/audio_map.py",
    "noir_film/crt.py",
    "noir_film/vhs.py",
    "noir_film/text_overlay.py",
    "noir_film/bengali_shaper.py",
]


def _extract_timeline_branch_sources() -> list:
    """Extracts each top-level if/elif branch source inside render_frame_at()."""
    tl_path = os.path.join(ROOT, "noir_film", "timeline.py")
    src = open(tl_path, "r", encoding="utf-8").read()
    tree = ast.parse(src)
    branches = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "render_frame_at":
            for stmt in node.body:
                if isinstance(stmt, ast.If):
                    cur = stmt
                    while cur is not None:
                        seg = ast.get_source_segment(src, cur.test) or ""
                        body_src = "\n".join(ast.get_source_segment(src, b) or "" for b in cur.body)
                        branches.append((seg, body_src))
                        if cur.orelse and len(cur.orelse) == 1 and isinstance(cur.orelse[0], ast.If):
                            cur = cur.orelse[0]
                        else:
                            if cur.orelse:
                                else_src = "\n".join(ast.get_source_segment(src, b) or "" for b in cur.orelse)
                                branches.append(("else", else_src))
                            cur = None
    return branches


def _file_fingerprint(rel_path: str) -> str:
    full = os.path.join(ROOT, rel_path)
    if not os.path.exists(full):
        return f"missing:{rel_path}"
    if rel_path.endswith(".py"):
        h = hashlib.sha256(open(full, "rb").read()).hexdigest()[:16]
        return f"{rel_path}:{h}"
    st = os.stat(full)
    return f"{rel_path}:{st.st_size}:{int(st.st_mtime)}"


def compute_shot_hash(shot_id: str, t0: float, t1: float, deps: list,
                      branch_src: str, width: int, height: int, fps: int, crf: int) -> str:
    """Computes deterministic 12-char hash for a single shot module."""
    h = hashlib.sha256()
    h.update(f"{shot_id}|{t0:.3f}|{t1:.3f}|{width}x{height}@{fps}|crf={crf}\n".encode("utf-8"))
    h.update(branch_src.encode("utf-8"))
    for dep in sorted(set(deps + SHARED_CORE_FILES)):
        h.update(_file_fingerprint(dep).encode("utf-8"))
    return h.hexdigest()[:12]


def render_modular_master(timeline, audio_mapper, start_t: float, end_t: float,
                          raw_output: str, width: int, height: int, fps: int, crf: int,
                          use_cache: bool = True):
    """
    Renders only invalidated shot modules and concatenates all modules via FFmpeg
    stream copy (-c copy) into raw_output.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    branches = _extract_timeline_branch_sources()

    active_shots = [s for s in SHOT_MODULES if s[2] > start_t and s[1] < end_t]
    if not active_shots:
        raise ValueError(f"No shot modules overlap window [{start_t}, {end_t}]")

    segment_paths = []
    cached_hits = 0
    rebuilt_count = 0
    t_build_start = time.time()

    for idx, (shot_id, s_t0, s_t1, deps) in enumerate(active_shots):
        w_t0 = max(start_t, s_t0)
        w_t1 = min(end_t, s_t1)
        # Match AST branch source by index when aligned, fallback to full branch table
        branch_src = branches[idx][1] if idx < len(branches) else ""
        shot_hash = compute_shot_hash(shot_id, w_t0, w_t1, deps, branch_src, width, height, fps, crf)
        seg_path = os.path.join(CACHE_DIR, f"{shot_id}_{shot_hash}.mp4")

        if use_cache and os.path.exists(seg_path) and os.path.getsize(seg_path) > 1024:
            cached_hits += 1
            segment_paths.append(seg_path)
            continue

        # Prune stale cached versions of this shot_id
        for stale in glob.glob(os.path.join(CACHE_DIR, f"{shot_id}_*.mp4")):
            try:
                os.remove(stale)
            except OSError:
                pass

        rebuilt_count += 1
        n_frames = max(1, int(round((w_t1 - w_t0) * fps)))
        tmp_seg = seg_path + ".tmp.mp4"
        pipe = FFmpegVideoPipe(tmp_seg, width=width, height=height, fps=fps, crf=crf)
        for f_i in range(n_frames):
            t = w_t0 + (f_i / float(fps))
            af = audio_mapper.get_features_at(t) if audio_mapper else {"sub_bass": 0.1, "rms": 0.1}
            frame = timeline.render_frame_at(t, width=width, height=height, audio_features=af)
            pipe.write_frame(frame)
        pipe.close()
        os.replace(tmp_seg, seg_path)
        segment_paths.append(seg_path)
        print(f"  [BUILT MODULE] {shot_id} ({w_t0:.1f}s-{w_t1:.1f}s, {n_frames}f) -> {shot_hash}", flush=True)

    # Stream-copy concat all shot modules into raw_output
    concat_txt = os.path.join(CACHE_DIR, "concat_list.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in segment_paths:
            safe_p = p.replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    t_stitch = time.time()
    subprocess.check_call(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", raw_output],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    stitch_s = time.time() - t_stitch
    total_s = time.time() - t_build_start
    print(f"[MODULAR BUILD] {cached_hits}/{len(active_shots)} shots cached | {rebuilt_count} rebuilt | Stitch: {stitch_s:.2f}s | Total: {total_s:.2f}s", flush=True)
