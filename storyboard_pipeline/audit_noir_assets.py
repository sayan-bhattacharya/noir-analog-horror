#!/usr/bin/env python3
"""Inventory NOIR project assets and resolve Episode 0 source paths.

Uses Pillow when installed for image dimensions and ffprobe when available for
audio/video metadata. It never modifies source assets. Output defaults to a new
versioned CSV in storyboard_pipeline/.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from pathlib import Path


SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".exr"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".gif"}
AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
MODEL_EXTS = {".blend", ".blend1", ".glb", ".gltf", ".fbx", ".obj", ".stl"}


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in MODEL_EXTS:
        return "3d_asset_or_backup" if ext == ".blend1" else "3d_asset"
    if ext in {".ipynb", ".py", ".bat", ".sh"}:
        return "notebook_or_code"
    if ext in {".md", ".html", ".csv", ".json", ".yaml", ".yml", ".fountain", ".txt"}:
        return "production_document"
    return "other"


def ffprobe(path: Path, executable: str | None) -> dict[str, str]:
    if not executable or path.suffix.lower() not in VIDEO_EXTS | AUDIO_EXTS:
        return {}
    command = [
        executable,
        "-v", "error",
        "-show_entries",
        "format=duration,format_name:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(path),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=40)
        info = json.loads(result.stdout)
        streams = info.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio = next((s for s in streams if s.get("codec_type") == "audio"), {})
        duration = info.get("format", {}).get("duration", "")
        return {
            "duration_s": f"{float(duration):.3f}" if duration else "",
            "format": info.get("format", {}).get("format_name", ""),
            "video_codec": video.get("codec_name", ""),
            "width": str(video.get("width", "")),
            "height": str(video.get("height", "")),
            "fps": video.get("r_frame_rate", ""),
            "audio_codec": audio.get("codec_name", ""),
            "sample_rate": str(audio.get("sample_rate", "")),
            "audio_channels": str(audio.get("channels", "")),
            "probe_status": "ok",
        }
    except Exception as exc:  # Keep auditing even if one media file is malformed.
        return {"probe_status": f"error:{type(exc).__name__}"}


def image_size(path: Path) -> tuple[str, str, str]:
    if path.suffix.lower() not in IMAGE_EXTS:
        return "", "", ""
    try:
        from PIL import Image

        with Image.open(path) as image:
            return str(image.width), str(image.height), "ok"
    except ImportError:
        return "", "", "pillow_unavailable"
    except Exception as exc:
        return "", "", f"error:{type(exc).__name__}"


def safe_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        yield path


def shot_source_matches(root: Path) -> list[dict[str, str]]:
    shot_csv = root / "story_development" / "production" / "shot_list_EP0_v02.csv"
    if not shot_csv.exists():
        return []
    by_name: dict[str, list[Path]] = {}
    for path in safe_files(root):
        by_name.setdefault(path.name.casefold(), []).append(path)
    rows: list[dict[str, str]] = []
    with shot_csv.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            source = (row.get("Source") or "").strip()
            if not source or source.casefold() in {"black", "—", "-"}:
                rows.append({"shot_id": row.get("EP0 Shot ID", ""), "source": source, "status": "intentional_placeholder", "matches": ""})
                continue
            cleaned = source.replace(" (Blender)", "").strip()
            direct = root / cleaned
            matches = [direct] if direct.exists() else by_name.get(Path(cleaned.replace("\\", "/")).name.casefold(), [])
            rows.append({
                "shot_id": row.get("EP0 Shot ID", ""),
                "source": source,
                "status": "found" if matches else "missing",
                "matches": ";".join(p.relative_to(root).as_posix() for p in matches[:3]),
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "storyboard_pipeline" / "NOIR_ASSET_AUDIT_v01.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing audit report: {output}")
    probe_exe = shutil.which("ffprobe")

    fields = [
        "relative_path", "kind", "extension", "size_bytes", "width", "height",
        "duration_s", "format", "video_codec", "fps", "audio_codec", "sample_rate",
        "audio_channels", "image_probe_status", "probe_status",
    ]
    files = sorted(safe_files(root), key=lambda p: p.relative_to(root).as_posix().casefold())
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for path in files:
            width, height, image_status = image_size(path)
            row = {
                "relative_path": path.relative_to(root).as_posix(),
                "kind": classify(path),
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
                "width": width,
                "height": height,
                "image_probe_status": image_status,
            }
            row.update(ffprobe(path, probe_exe))
            writer.writerow(row)

    shot_rows = shot_source_matches(root)
    missing = [r for r in shot_rows if r["status"] == "missing"]
    counts: dict[str, int] = {}
    for path in files:
        kind = classify(path)
        counts[kind] = counts.get(kind, 0) + 1
    print(f"Root: {root}")
    print(f"Files inventoried: {len(files)}")
    print(f"ffprobe: {probe_exe or 'not found'}")
    print("Counts by kind:")
    for kind, count in sorted(counts.items()):
        print(f"  {kind}: {count}")
    print(f"Episode 0 shot rows: {len(shot_rows)}; missing source references: {len(missing)}")
    for row in missing:
        print(f"  {row['shot_id']}: {row['source']}")
    print(f"Audit CSV: {output}")


if __name__ == "__main__":
    main()
