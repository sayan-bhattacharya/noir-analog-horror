#!/usr/bin/env python3
"""Render the NOIR revision checklist beats as five-second, audio-synced previews."""
from __future__ import annotations

import html
import json
import sys
import subprocess
import wave
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
OUT = PROJECT / "output"
SAMPLE_DIR = OUT / "revision_samples"
sys.path.insert(0, str(PROJECT))

from noir_film.timeline import NoirTimeline
from noir_film.utils.config_loader import load_global_config
from noir_film.utils.video_io import FFmpegVideoPipe

FPS = 24
WIDTH, HEIGHT = 1280, 720
DURATION = 5.0
CLIPS = [
    {"start": 0.0, "file": "NOIR_opening_0000-0005.mp4", "title": "Current NOIR opening · score-synced preview", "caption": "00:00–00:05 · existing compositor cut, with the matching Noir.wav excerpt", "poster_at": 1.2},
    {"start": 29.0, "file": "NOIR_civil_warning_0029-0034.mp4", "title": "Blue civil-danger card", "caption": "00:29–00:34 · Bengali-led checkered warning bands", "poster_at": 2.6},
    {"start": 60.0, "file": "NOIR_tubewell_continuity_0100-0105.mp4", "title": "One tube-well, continuous take", "caption": "01:00–01:05 · same-source courtyard move into the pump", "poster_at": 4.8},
    {"start": 184.0, "file": "NOIR_signal_question_0304-0309.mp4", "title": "Crimson intercepted signal", "caption": "03:04–03:09 · one red question mark + Morse-style waveform at 03:06", "poster_at": 2.3},
    {"start": 197.0, "file": "NOIR_blackhole_step_0317-0322.mp4", "title": "Shot 30: Small violet-purple neon LED portal in foreground", "caption": "03:17-03:22 | Noir.wav excerpt; Bimal slips and falls into compact violet-neon portal", "poster_at": 3.8},
    {"start": 352.0, "file": "NOIR_alien_first_peek_0552-0557.mp4", "title": "Alien first glimpse — current asset", "caption": "05:52–05:57 · existing creature footage before redesign", "poster_at": 2.0},
]

CHECKLIST = [
    ("00:00–00:06", "Song opening: black droplet, amber ring, BTN emblem resolves", "INCONSISTENT", "The 30:22 master script calls for a quiet droplet/ring image resolving into the BTN emblem by 00:06. The current compositor instead morphs the emblem into a satellite dish and cuts to geography at 00:02. This is the current cut, not a faithful render of the master-script opening."),
    ("Full runtime", "Music video synchronized to Noir.wav (30:22)", "INCONSISTENT", "The source track and screenplay are 30:22. The compositor config is 360 seconds, and the latest named master is only a 14-second, 640×360 preview. No complete music-video master render is present in the project."),
    ("00:30–00:36", "Blue warning; Bengali primary; text inside horizontal bands", "UPDATED", "The current screen was blood-red with English first. It is now deep blue with a subtle check pattern, three inset bands, large Bengali, and smaller English."),
    ("~00:48", "Slow clouds reveal an ambiguous sky object", "UPDATED", "A soft-edged, partially obscured silhouette now appears over the field-camera shot from 00:47–00:52."),
    ("Throughout", "Grounded stick-figure posture; remove jitter", "UPDATED", "Removed stepped 12-fps tremble; added a very small breathing motion and reduced arm/leg sway."),
    ("01:00–01:07", "Tube-well continuity across two angles", "UPDATED", "The source clips showed different pump designs. The cut now stays on one courtyard source clip and moves closer with a digital crop, so the wider and tighter views are demonstrably the same pump."),
    ("01:07–01:14", "Rust flakes and subtle locked-door vibration", "UPDATED", "Added a restrained one-pixel latch shiver and deterministic falling rust flecks over the existing macro plate."),
    ("01:20–01:26", "Readable Bengali newspaper headline", "UPDATED", "The source plate already had Bengali, but not the requested wording. The shot now overlays ‘নিকোজ গ্রামবাসীদের খোঁজে’ with a small English gloss."),
    ("01:31 / 01:44", "Passing bike light casts moving room/net shadows", "ALREADY PRESENT", "Both bedroom passages already composite the passing-bike layer and a sweeping amber beam with window-bar shadows; retained."),
    ("01:37 onward", "Rules as large, numbered broadcast infographics", "ALREADY PRESENT", "The existing cards have numbered rule IDs, bilingual large type, a crimson institutional header, and a framed dark slate; retained."),
    ("02:02", "Spider fills frame with legs, synchronized to swell", "ALREADY PRESENT", "The actor already draws eight legs and ramps from tiny to 2.55× after the 02:02 cue over 1.6 seconds; retained."),
    ("02:19 onward", "Second cloud transition slower and less repetitive", "UPDATED", "Cloud timing now supports explicit speed, reverse direction, and phase. The return is slowed and reversed; the later sky pass is also eased down."),
    ("02:36", "Cat-like object grows with controlled scale", "UPDATED", "Changed linear growth to a smooth eased curve and capped the stretch at 0.72."),
    ("03:06–03:07", "One strong red question mark + Morse waveform", "UPDATED", "Added a 1.5-second full-frame intercepted-signal interruption inside the descent slate."),
    ("03:14–03:24", "Shot 30: spilled oil widens into the hole; Bimal walks hypnotized and steps in", "UPDATED", "Aligned this passage to NOIR_30MIN_MASTER_SCRIPT.md: kept the cat and celestial eye out of Shot 30, removed the doorway emergence and orbit, and staged a direct approach and sink into the tar opening. Preview audio is the matching Noir.wav excerpt."),
    ("05:52 onward", "Redesign goofy alien with Dr. Hajra-inspired traits", "PROMPT READY", "Saved a reference-led, original cosmic-creature prompt. Current film still uses the existing creature video; generation awaits review of the revised prompt."),
    ("Shot 33 face plate", "Restyle the single crying face as a Bengali woman", "GENERATED / DOWNLOAD BLOCKED", "Edited plates/scene-17.jpeg in Artlist and saved it in the NOIR folder at no generation cost. The current Artlist plan blocks downloading AI generations, so this image is not yet integrated; source plate remains unchanged."),
]


def find_audio_path() -> Path | None:
    # Never silently substitute one of the project's podcast mixes for the NOIR score.
    candidates = [PROJECT / "Noir.wav", PROJECT / "audio" / "Noir.wav"]
    return next((p for p in candidates if p.is_file()), None)


class AudioFeatures:
    """Small stdlib WAV reader that supplies the compositor's audio envelopes."""
    def __init__(self, path: Path | None):
        self.path = path
        self.samples = None
        self.sr = 44100
        if path and path.suffix.lower() == ".wav":
            with wave.open(str(path), "rb") as wf:
                channels, width, self.sr = wf.getnchannels(), wf.getsampwidth(), wf.getframerate()
                raw = wf.readframes(wf.getnframes())
            if width == 2:
                vals = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
            elif width == 4:
                vals = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
            else:
                raise ValueError(f"Unsupported WAV sample width: {width} bytes")
            self.samples = vals.reshape(-1, channels).mean(axis=1)

    def get_features_at(self, t: float, window_ms: int = 250) -> dict:
        if self.samples is None:
            return {"sub_bass": .2, "rms": .25, "transient": False}
        center = int(t * self.sr)
        half = int(window_ms * self.sr / 2000)
        chunk = self.samples[max(0, center - half):min(len(self.samples), center + half)]
        if not len(chunk):
            return {"sub_bass": .1, "rms": .1, "transient": False}
        rms = float(np.sqrt(np.mean(chunk * chunk)))
        return {"sub_bass": min(1.0, max(0.0, float(np.mean(np.abs(chunk))) * 3.5)),
                "rms": min(1.0, max(0.0, rms)), "transient": rms > .35}


def render_clip(timeline: NoirTimeline, audio: AudioFeatures, clip: dict) -> Path:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    dest = SAMPLE_DIR / clip["file"]
    silent = SAMPLE_DIR / (dest.stem + ".silent.mp4")
    pipe = FFmpegVideoPipe(str(silent), WIDTH, HEIGHT, FPS, crf=18)
    poster = None
    for i in range(int(DURATION * FPS)):
        t = clip["start"] + i / FPS
        frame = timeline.render_frame_at(t, WIDTH, HEIGHT, audio.get_features_at(t))
        pipe.write_frame(frame)
        if i == int(clip.get("poster_at", 2.6) * FPS):
            poster = frame.copy()
    pipe.close()

    audio_path = audio.path
    if audio_path:
        segment = SAMPLE_DIR / (dest.stem + ".audio.m4a")
        subprocess.run(["ffmpeg", "-y", "-ss", str(clip["start"]), "-i", str(audio_path),
                        "-t", str(DURATION), "-vn", "-c:a", "aac", "-b:a", "192k", str(segment)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-i", str(silent), "-i", str(segment), "-t", str(DURATION),
                        "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", str(dest)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segment.unlink(missing_ok=True)
        silent.unlink(missing_ok=True)
    else:
        silent.replace(dest)

    if poster is not None:
        Image.fromarray(poster).save(SAMPLE_DIR / (dest.stem + ".jpg"), quality=88)
    print(f"Rendered {dest}", flush=True)
    return dest


def build_review() -> None:
    rows = "".join(
        f'<tr><td>{html.escape(time)}</td><td>{html.escape(item)}</td><td class="status {status.lower().replace(" ", "-")}">{html.escape(status)}</td><td>{html.escape(detail)}</td></tr>'
        for time, item, status, detail in CHECKLIST
    )
    videos = "".join(
        f'<article class="clip"><div class="clip-head"><div><span class="eyebrow">{html.escape(clip["caption"])}</span><h2>{html.escape(clip["title"])}</h2></div><a href="revision_samples/{html.escape(Path(clip["file"]).stem)}.mp4">Open MP4 ↗</a></div><video controls preload="metadata" poster="revision_samples/{html.escape(Path(clip["file"]).stem)}.jpg" src="revision_samples/{html.escape(clip["file"])}"></video></article>'
        for clip in CLIPS
    )
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NOIR · Revision review</title><style>
:root{{--bg:#11120f;--panel:#1a1b17;--line:#37382f;--ink:#eee9dc;--muted:#aaa695;--gold:#d5ba7c;--green:#a4b39d;--red:#c96558}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 50% -20%,#373326,transparent 55%),var(--bg);color:var(--ink);font:15px/1.55 Inter,Segoe UI,Arial,sans-serif}}.shell{{width:min(1400px,calc(100% - 40px));margin:auto}}header{{padding:44px 0 28px;border-bottom:1px solid var(--line)}}.eyebrow,th,.status{{font:10px ui-monospace,Consolas,monospace;text-transform:uppercase;letter-spacing:.09em}}.eyebrow{{color:var(--gold)}}h1{{font:500 clamp(38px,6vw,70px)/1 Georgia,serif;margin:14px 0}}h2{{font:24px Georgia,serif;margin:9px 0}}p{{color:var(--muted);max-width:900px}}a{{color:var(--gold)}}.links{{display:flex;gap:16px;margin-top:18px}}.clips{{display:grid;grid-template-columns:1fr;gap:18px;margin:26px 0 46px}}.clip{{background:var(--panel);border:1px solid var(--line);padding:16px}}.clip-head{{display:flex;justify-content:space-between;gap:18px;align-items:center;margin-bottom:12px}}video{{width:100%;max-height:74vh;background:#050505;display:block}}table{{width:100%;border-collapse:collapse;margin:20px 0 50px}}th,td{{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--line)}}th{{color:var(--gold)}}td{{font-size:13px}}td:first-child{{white-space:nowrap;color:#d7cfbc}}.status{{white-space:nowrap;color:var(--green)}}.status.updated{{color:#9dc2a1}}.status.already-present{{color:var(--gold)}}.status.partial,.status.inconsistent{{color:#e1a477}}.small{{font-size:12px;color:var(--muted)}}@media(max-width:750px){{.shell{{width:calc(100% - 20px)}}.clip-head{{align-items:flex-start;flex-direction:column}}table{{display:block;overflow-x:auto}}td{{min-width:170px}}}}
</style></head><body><header><div class="shell"><div class="eyebrow">PROJECT NOIR / 05:52 IMPLEMENTED CUT / REVISION PASS</div><h1>Checklist → rendered evidence</h1><p>The current implemented film timeline ends at 05:52; the master screenplay and score are 30:22. This review compares the pasted notes against its actual timeline, avoids redoing work already present, and includes five-second excerpts from Noir.wav at each matching film timecode. Podcast audio is never used as a NOIR soundtrack.</p><div class="links"><a href="NOIR_storyboard.html">← Storyboard</a><a href="NOIR_asset_explorer.html">Image library ↗</a></div></div></header><main class="shell"><section class="clips">{videos}</section><h2>Checklist audit</h2><p class="small">“Already present” means the implementation was found in source and retained. “Updated” means code has been changed in this revision pass. The rendered clips show the time-critical transitions; the remaining updates are in the compositor timeline.</p><table><thead><tr><th>Time</th><th>Requested change</th><th>Result</th><th>What I found / changed</th></tr></thead><tbody>{rows}</tbody></table><p class="small">The scene-source clips for the two tube-well angles still need a side-by-side visual continuity check; they are kept in one continuous 7-second beat. The 30:22 screenplay is not yet fully implemented; this revision pass rendered only five-second excerpts.</p></main></body></html>'''
    (OUT / "NOIR_revision_review.html").write_text(page, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["opening", "warning", "tube_well", "signal", "blackhole", "alien_peek"], help="Rerender one preview clip only")
    args = parser.parse_args()
    config = load_global_config()
    timeline = NoirTimeline(config)
    audio_path = find_audio_path()
    audio = AudioFeatures(audio_path)
    selection = {"opening": 0, "warning": 1, "tube_well": 2, "signal": 3, "blackhole": 4, "alien_peek": 5}
    clips = [CLIPS[selection[args.only]]] if args.only else CLIPS
    print(f"Rendering {len(clips)} clips × {DURATION:.0f}s @ {WIDTH}×{HEIGHT}/{FPS}fps; audio: {audio_path or 'none'}", flush=True)
    for clip in clips:
        render_clip(timeline, audio, clip)
    build_review()
    print(f"Review: {OUT / 'NOIR_revision_review.html'}", flush=True)


if __name__ == "__main__":
    main()
