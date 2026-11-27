#!/usr/bin/env python3
"""NOIR still-generation runner with timestamped console and file logs.

Default behavior is a CPU/GPU preflight only. Generating images requires
--mode generate, an explicit batch, and an interactive typed approval.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.util
import json
import logging
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "storyboard_pipeline" / "lightning_noir_assets_v01"
QUEUE_PATH = PACKAGE / "generation_queue_v01.json"
OUTPUT_ROOT = ROOT / "output" / "lightning_assets_v01"
LOG_ROOT = OUTPUT_ROOT / "logs"
SELECTED_BIMAL = PACKAGE / "selected" / "BIMAL_FACE_ANCHOR_selected.png"
LOG = logging.getLogger("noir_gpu")
ACTIVE_STEPS = 0


def make_logger() -> Path:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = LOG_ROOT / f"noir_run_{stamp}.log"
    LOG.setLevel(logging.INFO)
    LOG.handlers.clear()
    formatter = logging.Formatter("%(asctime)sZ | %(levelname)s | %(message)s", "%Y-%m-%dT%H:%M:%S")
    formatter.converter = time.gmtime
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    LOG.addHandler(stream)
    LOG.addHandler(file_handler)
    return log_path


def load_queue() -> dict[str, Any]:
    if not QUEUE_PATH.is_file():
        raise FileNotFoundError(f"Queue is missing: {QUEUE_PATH}")
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    if not queue.get("jobs") or not queue.get("batches"):
        raise ValueError("Queue has no jobs or batches.")
    return queue


def verify_inputs(queue: dict[str, Any]) -> list[Path]:
    paths: set[Path] = set()
    for job in queue["jobs"]:
        for key in ("reference_file", "layout_reference_file", "identity_reference_file"):
            if job.get(key):
                paths.add(PACKAGE / "references" / Path(job[key]).name)
    missing = sorted(path for path in paths if not path.is_file())
    if missing:
        raise FileNotFoundError("Missing packaged references:\n" + "\n".join(map(str, missing)))
    return sorted(paths)


def dependency_report() -> list[str]:
    modules = ("diffusers", "transformers", "accelerate", "safetensors", "peft", "PIL")
    missing = [name for name in modules if importlib.util.find_spec(name) is None]
    LOG.info("Inference dependencies: %s", "all present" if not missing else "missing " + ", ".join(missing))
    return missing


def gpu_report(require_gpu: bool = False):
    try:
        import torch
    except ImportError:
        LOG.warning("PyTorch is not installed in this environment.")
        if require_gpu:
            raise RuntimeError("Install the notebook's inference dependencies first; preserve Lightning's CUDA PyTorch build.")
        return None

    LOG.info("Python %s | PyTorch %s | compiled CUDA %s", platform.python_version(), torch.__version__, torch.version.cuda or "none")
    if not torch.cuda.is_available():
        message = (
            "CUDA is not available to Python. Switch this Lightning Studio to a GPU in its hardware selector, "
            "wait for it to restart, and rerun. Python cannot provision the Studio GPU."
        )
        if require_gpu:
            raise RuntimeError(message)
        LOG.warning(message)
        return torch

    torch.cuda.init()
    count = torch.cuda.device_count()
    torch.cuda.set_device(0)
    for index in range(count):
        props = torch.cuda.get_device_properties(index)
        LOG.info("Visible GPU %d: %s | %.1f GiB VRAM", index, props.name, props.total_memory / 1024**3)
    LOG.info("Selected GPU 0; this runner processes one image at a time and does not distribute work across GPUs.")
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.set_float32_matmul_precision("high")
    return torch


def print_queue(queue: dict[str, Any]) -> None:
    LOG.info("Queue %s | status=%s | jobs=%d", queue.get("queue_id"), queue.get("status"), len(queue["jobs"]))
    for batch in queue["batches"]:
        jobs = [job for job in queue["jobs"] if job["batch_id"] == batch["batch_id"]]
        LOG.info("--- %s (%d images) ---", batch["batch_id"], len(jobs))
        LOG.info("Review checkpoint: %s", batch["review_checkpoint"])
        for job in jobs:
            LOG.info("JOB %s | mode=%s | seed=%s | output=%s.png", job["job_id"], job["mode"], job["seed"], job["output_stem"])
            LOG.info("Reference: %s", job["reference_file"])
            LOG.info("Prompt: %s", job["prompt"])
            LOG.info("Negative prompt: %s", job.get("negative_prompt", ""))


def write_mask_previews(queue: dict[str, Any]) -> None:
    from PIL import Image, ImageOps
    preview_dir = OUTPUT_ROOT / "mask_previews_v01"
    preview_dir.mkdir(parents=True, exist_ok=True)
    for job in queue["jobs"]:
        if job["mode"] != "inpaint_existing_candidate":
            continue
        source_path = PACKAGE / "references" / Path(job["reference_file"]).name
        source = Image.open(source_path).convert("RGB")
        mask = make_mask(source.size, job["mask_rects_norm_xyxy"])
        tint = Image.new("RGBA", source.size, (255, 32, 32, 0))
        tint.putalpha(mask.point(lambda value: round(value * 0.45)))
        preview = Image.alpha_composite(source.convert("RGBA"), tint).convert("RGB")
        target = preview_dir / f"{job['output_stem']}_mask_preview.jpg"
        if target.exists():
            LOG.info("Mask preview already exists; keeping it unchanged: %s", target)
            continue
        preview.save(target, format="JPEG", quality=92)
        LOG.info("Mask preview saved (red = inpaint area): %s", target)


def create_contact_sheet(records: list[dict[str, Any]], batch_dir: Path) -> Path:
    from PIL import Image, ImageDraw, ImageOps
    cards = []
    for record in records:
        source = Image.open(ROOT / record["output"]).convert("RGB")
        thumb = ImageOps.contain(source, (480, 360))
        card = Image.new("RGB", (500, 410), (20, 20, 24))
        card.paste(thumb, ((500 - thumb.width) // 2, 12))
        ImageDraw.Draw(card).text((12, 382), record["job_id"], fill=(238, 238, 238))
        cards.append(card)
    sheet = Image.new("RGB", (500 * len(cards), 410), (20, 20, 24))
    for index, card in enumerate(cards):
        sheet.paste(card, (500 * index, 0))
    target = batch_dir / "contact_sheet.jpg"
    sheet.save(target, format="JPEG", quality=92)
    return target


def unique_output(directory: Path, stem: str) -> Path:
    target = directory / f"{stem}.png"
    number = 2
    while target.exists():
        target = directory / f"{stem}_run{number:02d}.png"
        number += 1
    return target


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_mask(size: tuple[int, int], rects: list[list[float]], feather: int = 8):
    from PIL import Image, ImageDraw, ImageFilter
    width, height = size
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for x0, y0, x1, y1 in rects:
        draw.rectangle((round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height)), fill=255)
    return mask.filter(ImageFilter.GaussianBlur(feather))


def make_face_crop(image, box: list[float]):
    from PIL import Image
    width, height = image.size
    x0, y0, x1, y1 = box
    crop = image.crop((round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height)))
    side = max(crop.size)
    square = Image.new("RGB", (side, side), (32, 28, 24))
    square.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
    return square.resize((512, 512), Image.Resampling.LANCZOS)


def load_pipeline(queue: dict[str, Any], batch_id: str, torch):
    from diffusers import StableDiffusionXLPipeline, StableDiffusionXLInpaintPipeline
    models = queue["models"]
    dtype = torch.float16
    vram_gib = torch.cuda.get_device_properties(0).total_memory / 1024**3
    started = time.perf_counter()
    if batch_id == "B01":
        from transformers import CLIPVisionModelWithProjection
        adapter_repo = models["face_adapter_repo"]
        LOG.info("Loading IP-Adapter image encoder; first run may download model weights.")
        encoder = CLIPVisionModelWithProjection.from_pretrained(
            adapter_repo, subfolder="models/image_encoder", torch_dtype=dtype, use_safetensors=True
        )
        LOG.info("Loading SDXL base model: %s", models["base"])
        pipe = StableDiffusionXLPipeline.from_pretrained(
            models["base"], torch_dtype=dtype, variant="fp16", use_safetensors=True, image_encoder=encoder
        )
        LOG.info("Loading face adapter weights: %s", models["face_adapter_weight"])
        pipe.load_ip_adapter(
            adapter_repo, subfolder=models["face_adapter_subfolder"], weight_name=models["face_adapter_weight"]
        )
        pipe.set_ip_adapter_scale(0.65)
    else:
        LOG.info("Loading SDXL inpaint model: %s", models["inpaint"])
        pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
            models["inpaint"], torch_dtype=dtype, variant="fp16", use_safetensors=True
        )

    pipe.enable_vae_slicing()
    pipe.vae.enable_tiling()
    if vram_gib < 18:
        LOG.info("GPU has %.1f GiB VRAM; enabling model CPU offload to avoid an out-of-memory failure.", vram_gib)
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda:0")
    pipe.set_progress_bar_config(disable=False)
    LOG.info("Pipeline ready in %.1f seconds.", time.perf_counter() - started)
    return pipe


def step_callback(pipe, step: int, timestep, callback_kwargs: dict[str, Any]):
    current = step + 1
    total = ACTIVE_STEPS
    if current == 1 or current % 5 == 0 or (total and current == total):
        LOG.info("Denoising step %d%s", current, f"/{total}" if total else "")
    return callback_kwargs


def run_job(pipe, job: dict[str, Any], batch_dir: Path, queue: dict[str, Any], torch) -> dict[str, Any]:
    global ACTIVE_STEPS
    from PIL import Image
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats(0)
    generator = torch.Generator(device="cpu").manual_seed(int(job["seed"]))
    common = {
        "prompt": job["prompt"],
        "negative_prompt": job.get("negative_prompt", ""),
        "guidance_scale": 5.0,
        "generator": generator,
        "callback_on_step_end": step_callback,
    }
    if job["mode"] == "text2img_with_face_adapter":
        ACTIVE_STEPS = 32
        image = Image.open(PACKAGE / "references" / Path(job["reference_file"]).name).convert("RGB")
        face = make_face_crop(image, job["face_crop_norm_xyxy"])
        result = pipe(
            **common,
            ip_adapter_image=face,
            width=int(job["width"]), height=int(job["height"]),
            num_inference_steps=32, num_images_per_prompt=1,
        ).images[0]
    elif job["mode"] == "inpaint_existing_candidate":
        ACTIVE_STEPS = 30
        source_path = PACKAGE / "references" / Path(job["reference_file"]).name
        source = Image.open(source_path).convert("RGB")
        mask = make_mask(source.size, job["mask_rects_norm_xyxy"])
        result = pipe(
            **common,
            image=source, mask_image=mask,
            width=source.width, height=source.height,
            strength=0.92, num_inference_steps=30,
        ).images[0]
    else:
        raise ValueError(f"Unknown job mode: {job['mode']}")

    output = unique_output(batch_dir, job["output_stem"])
    temporary = output.with_name(output.stem + ".partial.png")
    result.save(temporary, format="PNG", optimize=True)
    temporary.replace(output)
    elapsed = time.perf_counter() - started
    peak = torch.cuda.max_memory_reserved(0) / 1024**3
    LOG.info("Saved %s in %.1f sec | peak reserved VRAM %.2f GiB | SHA256 %s", output, elapsed, peak, sha256(output))
    return {
        "job_id": job["job_id"], "batch_id": job["batch_id"],
        "output": output.relative_to(ROOT).as_posix(), "sha256": sha256(output),
        "seed": int(job["seed"]), "prompt": job["prompt"],
        "negative_prompt": job.get("negative_prompt", ""),
        "reference": job["reference_file"], "gpu": torch.cuda.get_device_name(0),
        "vram_gib": round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
        "peak_reserved_vram_gib": round(peak, 2), "elapsed_seconds": round(elapsed, 2),
    }


def generate_batch(queue: dict[str, Any], batch_id: str, torch) -> None:
    batch = next((item for item in queue["batches"] if item["batch_id"] == batch_id), None)
    if batch is None:
        raise ValueError(f"Unknown batch {batch_id!r}. Choose B01 or B02.")
    jobs = [job for job in queue["jobs"] if job["batch_id"] == batch_id]
    if not jobs or len(jobs) > 3 or len(jobs) != int(batch["count"]):
        raise RuntimeError("Queue integrity check failed; each batch must contain 1?3 images.")
    if batch_id == "B02" and not SELECTED_BIMAL.is_file():
        raise RuntimeError(f"B02 is blocked. Review B01 and save your selected face anchor to: {SELECTED_BIMAL}")

    print_queue({**queue, "jobs": jobs, "batches": [batch]})
    LOG.info("This batch will run sequentially on GPU 0; outputs are candidates, not selected assets.")
    approval = input(f"Type APPROVE {batch_id} to download/load weights and spend GPU time: ").strip()
    if approval != f"APPROVE {batch_id}":
        LOG.warning("Approval did not match. No models were loaded and no images were generated.")
        return

    run_id = datetime.now(timezone.utc).strftime(f"{batch_id}_%Y%m%dT%H%M%SZ")
    batch_dir = OUTPUT_ROOT / run_id
    batch_dir.mkdir(parents=True, exist_ok=False)
    LOG.info("Starting %s | output directory: %s", batch_id, batch_dir)
    pipe = load_pipeline(queue, batch_id, torch)
    records = []
    try:
        for index, job in enumerate(jobs, start=1):
            LOG.info("Starting image %d/%d: %s", index, len(jobs), job["job_id"])
            records.append(run_job(pipe, job, batch_dir, queue, torch))
    finally:
        del pipe
        gc.collect()
        torch.cuda.empty_cache()
        LOG.info("Released model memory from GPU.")

    manifest = {"run_id": run_id, "batch_id": batch_id, "gpu": torch.cuda.get_device_name(0), "jobs": records}
    manifest_path = batch_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    sheet_path = create_contact_sheet(records, batch_dir)
    LOG.info("Batch complete. Manifest: %s", manifest_path)
    LOG.info("Review contact sheet: %s", sheet_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="NOIR still generation with progress logs; defaults to safe preflight.")
    parser.add_argument("--mode", choices=("preflight", "queue", "generate"), default="preflight")
    parser.add_argument("--batch", choices=("B01", "B02"), help="Required when --mode generate")
    args = parser.parse_args()
    log_path = make_logger()
    LOG.info("NOIR runner started | mode=%s | project=%s", args.mode, ROOT)
    LOG.info("Session log: %s", log_path)
    try:
        queue = load_queue()
        refs = verify_inputs(queue)
        LOG.info("Queue loaded; %d references verified; output path: %s", len(refs), OUTPUT_ROOT)
        missing = dependency_report()
        torch = gpu_report(require_gpu=args.mode == "generate")
        if args.mode == "generate" and missing:
            raise RuntimeError("Install missing inference dependencies before generation: " + ", ".join(missing))
        if args.mode == "queue":
            print_queue(queue)
            if "PIL" in missing:
                LOG.warning("Pillow is missing; skipping visual mask previews. Install the documented dependencies and rerun queue mode.")
            else:
                write_mask_previews(queue)
            LOG.info("Open the mask previews and check each red area before approving B02.")
            return 0
        if args.mode == "generate":
            if not args.batch:
                parser.error("--mode generate requires --batch B01 or --batch B02")
            if torch is None:
                raise RuntimeError("PyTorch is required for generation.")
            generate_batch(queue, args.batch, torch)
            return 0
        LOG.info("Preflight complete. No model downloads or image generation were started.")
        LOG.info("For the complete prompt list run: python -u %s --mode queue", Path(__file__).name)
        return 0
    except KeyboardInterrupt:
        LOG.warning("Interrupted by user. No further jobs will run.")
        return 130
    except Exception:
        LOG.exception("Stopped with an error")
        LOG.info("Full exception details are in %s", log_path)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
