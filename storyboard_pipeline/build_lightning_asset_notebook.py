#!/usr/bin/env python3
"""Build the clean, unexecuted Lightning Studio notebook for NOIR Episode 0."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "NOIR_LIGHTNING_ASSET_GENERATOR_v01.ipynb"
if OUTPUT.exists():
    raise FileExistsError(f"Refusing to overwrite existing notebook: {OUTPUT}")


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(source).strip("\n").splitlines(keepends=True)}


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(source).strip("\n").splitlines(keepends=True),
    }


cells = [
    md(r"""
    # NOIR Episode 0 — GPU Asset Generation

    **Purpose:** create a photorealistic Bimal face anchor and repair three existing Episode 0 candidate plates. This notebook generates still images only. It does not create video, run Blender, use FFmpeg, or assemble the film.

    **Project:** 5:00 Episode 0 · 4:3 archival picture inside 16:9 · Bengali-first titles added later in post.

    The notebook starts with CPU-only file and GPU checks. It prints every prompt and reference before model download. Each batch requires typed approval and is limited to three images. Generated images remain candidates until manually reviewed and selected.

    > Do not use “Run All.” Work through the preflight and queue first. Start a GPU only for an approved generation batch.
    """),
    md(r"""
    ## 1. Bring the package into Lightning Studio

    The package is in the `codex/noir-lightning-assets-v01` branch of the NOIR repository once that branch has been published. In the Studio terminal, clone that branch and open this notebook:

    ```bash
    git clone --branch codex/noir-lightning-assets-v01 https://github.com/sayan-bhattacharya/noir-analog-horror.git
    cd noir-analog-horror
    ```

    Open `storyboard_pipeline/NOIR_LIGHTNING_ASSET_GENERATOR_v01.ipynb` from JupyterLab.

    Keep setup, Git, reference review, and package installation on the free CPU Studio. Switch to a single 24 GB GPU (L4 if available) only for the approved image batch. SDXL fits this single-image workflow; training a LoRA or using multiple GPUs would add cost without helping these four assets. Lightning Studio files and environments persist across sleep; sleep the Studio when idle.

    Check current instance availability and pricing in [Lightning AI pricing](https://lightning.ai/pricing) before selecting a machine. This notebook reports actual elapsed time and GPU memory; it cannot read your account balance or promise a credit cost.
    """),
    code(r"""
    from pathlib import Path
    import csv
    import json
    import os
    import platform
    import shutil
    import subprocess

    def find_noir_root(start: Path) -> Path:
        for candidate in (start, *start.parents):
            if (candidate / "storyboard_pipeline" / "lightning_noir_assets_v01" / "generation_queue_v01.json").is_file():
                return candidate
            if (candidate / "lightning_noir_assets_v01" / "generation_queue_v01.json").is_file():
                return candidate.parent
        raise FileNotFoundError(
            "NOIR generation package not found. Clone the package branch, cd into noir-analog-horror, "
            "then reopen this notebook."
        )

    PROJECT_ROOT = find_noir_root(Path.cwd().resolve())
    PACKAGE_ROOT = PROJECT_ROOT / "storyboard_pipeline" / "lightning_noir_assets_v01"
    REFERENCES = PACKAGE_ROOT / "references"
    SOURCES = PACKAGE_ROOT / "sources"
    QUEUE_PATH = PACKAGE_ROOT / "generation_queue_v01.json"
    OUTPUT_ROOT = PROJECT_ROOT / "output" / "lightning_assets_v01"
    SELECTED_BIMAL_ANCHOR = PACKAGE_ROOT / "selected" / "BIMAL_FACE_ANCHOR_selected.png"
    QUEUE = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))

    required = [PACKAGE_ROOT / p["reference_file"] for p in QUEUE["jobs"]]
    required += [PACKAGE_ROOT / p["layout_reference_file"] for p in QUEUE["jobs"] if p.get("layout_reference_file")]
    required += [PACKAGE_ROOT / p["identity_reference_file"] for p in QUEUE["jobs"] if p.get("identity_reference_file")]
    missing = sorted({str(p) for p in required if not p.is_file()})
    if missing:
        raise FileNotFoundError("Missing generation inputs:\n" + "\n".join(missing))

    print(f"NOIR root: {PROJECT_ROOT}")
    print(f"Queue: {QUEUE['queue_id']} ({QUEUE['status']})")
    print(f"Prepared images: {len(QUEUE['jobs'])}; batches: " + ", ".join(b["batch_id"] for b in QUEUE["batches"]))
    print(f"Output root (ignored by Git): {OUTPUT_ROOT}")
    print(f"Python: {platform.python_version()} | ffprobe: {shutil.which('ffprobe') or 'not found'}")

    try:
        import torch
        print(f"PyTorch: {torch.__version__} | CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            print(f"GPU: {props.name} | VRAM: {props.total_memory / 1024**3:.1f} GiB")
    except ImportError:
        print("PyTorch is not installed yet. Install the inference packages below; do not replace Lightning's CUDA PyTorch build.")

    print("\nAll source inputs exist in this clone. No model weights were downloaded and no generation was started.")
    """),
    md(r"""
    ## 2. Audit the source pack

    The original images and shot-plan files stay untouched. The versioned reference copies used by this notebook are in `storyboard_pipeline/lightning_noir_assets_v01/`. The complete 666-file workstation audit is in `storyboard_pipeline/NOIR_ASSET_AUDIT_v01.csv`.

    The source package contains a 50-row shot list and a separate 18-beat storyboard map. Their shot IDs differ; do not use this notebook to rewrite timings. Two specified road clips are absent from the local project: `15002113_3840_2160_60fps.mp4` and `20200549-uhd_2160_3840_60fps.mp4`. The 14-second low-resolution preview is not a replacement.

    Bimal already has a realistic face in the awakening still. The Trickster already has a visible human-like face in the doorway still. The five-minute cast list does not define another named man, so this pass reuses that Trickster reference instead of inventing another character.
    """),
    md(r"""
    ## 3. Install image inference dependencies on CPU

    Lightning provides the CUDA-enabled PyTorch build. Keep it; install only the model libraries. After installation, restart the notebook kernel if Jupyter asks.

    SDXL is under the CreativeML Open RAIL++-M license. The IP-Adapter project is Apache-2.0. Review the terms before using generated images in a monetized release. The notebook uses the face-cropped Plus adapter, not FaceID weights whose model documentation marks them research-only.
    """),
    code(r"""
    %pip install -q "diffusers>=0.35,<0.37" "transformers>=4.44,<5" "accelerate>=0.33" "safetensors>=0.4" "peft>=0.10"
    """),
    code(r"""
    import gc
    import hashlib
    import json
    import time
    from datetime import datetime, timezone
    from pathlib import Path

    import torch
    from PIL import Image, ImageDraw, ImageFilter, ImageOps
    from IPython.display import display, Markdown

    if not torch.cuda.is_available():
        raise RuntimeError("No CUDA GPU is active. Finish CPU setup, switch the Studio to a GPU, then rerun this cell.")

    GPU = torch.cuda.get_device_properties(0)
    VRAM_GIB = GPU.total_memory / 1024**3
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.set_float32_matmul_precision("high")
    DTYPE = torch.float16

    print(f"Active GPU: {GPU.name} | VRAM: {VRAM_GIB:.1f} GiB | dtype: fp16 | TF32: enabled")
    print("Batch size is fixed at 1. VAE slicing is enabled. No model training or video generation is performed.")
    """),
    md(r"""
    ## 4. Review the complete generation queue

    Read every prompt and reference below before loading model weights. The queue has one identity-anchor image in B01, followed by three localized plate repairs in B02. B02 is intentionally blocked until a Bimal anchor has been reviewed and saved to the selected path above.
    """),
    code(r"""
    for batch in QUEUE["batches"]:
        display(Markdown(f"## Batch {batch['batch_id']} — {batch['count']} image(s)"))
        display(Markdown(batch["review_checkpoint"]))
        for job in (j for j in QUEUE["jobs"] if j["batch_id"] == batch["batch_id"]):
            display(Markdown(
                f"### {job['job_id']}\n"
                f"- Mode: `{job['mode']}`\n"
                f"- Reference: `{job['reference_file']}`\n"
                f"- Output: `{job['output_stem']}.png`\n"
                f"- Seed: `{job['seed']}`\n\n"
                f"**Prompt**\n\n{job['prompt']}\n\n"
                f"**Negative prompt**\n\n{job['negative_prompt']}"
            ))
    """),
    code(r"""
    # Preview the source stills and the exact inpaint rectangles before spending GPU time.
    def make_mask(size, rects, feather=8):
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        width, height = size
        for x0, y0, x1, y1 in rects:
            draw.rectangle((round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height)), fill=255)
        return mask.filter(ImageFilter.GaussianBlur(feather))

    for job in QUEUE["jobs"]:
        if job["mode"] != "inpaint_existing_candidate":
            continue
        source = Image.open(PACKAGE_ROOT / job["reference_file"]).convert("RGB")
        mask = make_mask(source.size, job["mask_rects_norm_xyxy"])
        overlay = source.copy().convert("RGBA")
        tint = Image.new("RGBA", source.size, (255, 40, 40, 0))
        tint.putalpha(mask.point(lambda value: round(value * 0.45)))
        preview = Image.alpha_composite(overlay, tint).convert("RGB")
        display(Markdown(f"### {job['job_id']} — red regions will be repaired"))
        display(ImageOps.contain(preview, (900, 700)))
    """),
    md(r"""
    ## 5. Load SDXL only after queue review

    The notebook runs one image at a time. A single 24 GB GPU should be sufficient for 1024×768 SDXL inference. Smaller GPUs fall back to model CPU offload, which saves VRAM but is slower. No training is needed for this short sequence; the reviewed face reference is the identity condition.

    Image-to-image similarity is approximate. If the face anchor is not convincing, stop at B01 and revise the reference crop or prompt. Do not spend the B02 batch until the anchor is selected.
    """),
    code(r"""
    from diffusers import StableDiffusionXLPipeline, StableDiffusionXLInpaintPipeline
    from transformers import CLIPVisionModelWithProjection

    SDXL_ID = QUEUE["models"]["base"]
    INPAINT_ID = QUEUE["models"]["inpaint"]
    ADAPTER_REPO = QUEUE["models"]["face_adapter_repo"]

    def prepare_pipeline(pipe, adapter=False):
        if adapter:
            pipe.load_ip_adapter(
                ADAPTER_REPO,
                subfolder=QUEUE["models"]["face_adapter_subfolder"],
                weight_name=QUEUE["models"]["face_adapter_weight"],
            )
            pipe.set_ip_adapter_scale(0.65)
        pipe.enable_vae_slicing()
        if hasattr(pipe, "vae"):
            pipe.vae.enable_tiling()
        if VRAM_GIB < 18:
            pipe.enable_model_cpu_offload()
        else:
            pipe.to("cuda")
        return pipe

    def load_anchor_pipeline():
        image_encoder = CLIPVisionModelWithProjection.from_pretrained(
            ADAPTER_REPO,
            subfolder="models/image_encoder",
            torch_dtype=DTYPE,
            use_safetensors=True,
        )
        pipe = StableDiffusionXLPipeline.from_pretrained(
            SDXL_ID,
            torch_dtype=DTYPE,
            variant="fp16",
            use_safetensors=True,
            image_encoder=image_encoder,
        )
        return prepare_pipeline(pipe, adapter=True)

    def load_inpaint_pipeline():
        pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
            INPAINT_ID,
            torch_dtype=DTYPE,
            variant="fp16",
            use_safetensors=True,
        )
        return prepare_pipeline(pipe, adapter=False)

    print("Model loaders defined. Weights are not downloaded until an approved batch starts.")
    """),
    code(r"""
    def image_sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def unique_output_path(folder: Path, stem: str) -> Path:
        target = folder / f"{stem}.png"
        run = 2
        while target.exists():
            target = folder / f"{stem}_run{run:02d}.png"
            run += 1
        return target

    def square_face_crop(image: Image.Image, box):
        width, height = image.size
        x0, y0, x1, y1 = box
        crop = image.crop((round(x0 * width), round(y0 * height), round(x1 * width), round(y1 * height)))
        side = max(crop.size)
        square = Image.new("RGB", (side, side), (32, 28, 24))
        square.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
        return square.resize((512, 512), Image.Resampling.LANCZOS)

    def execute_job(pipe, job, run_folder):
        start = time.perf_counter()
        torch.cuda.reset_peak_memory_stats()
        generator = torch.Generator(device="cpu").manual_seed(int(job["seed"]))
        if job["mode"] == "text2img_with_face_adapter":
            reference = Image.open(PACKAGE_ROOT / job["reference_file"]).convert("RGB")
            face = square_face_crop(reference, job["face_crop_norm_xyxy"])
            result = pipe(
                prompt=job["prompt"],
                negative_prompt=job["negative_prompt"],
                ip_adapter_image=face,
                width=int(job["width"]),
                height=int(job["height"]),
                num_inference_steps=32,
                guidance_scale=5.0,
                num_images_per_prompt=1,
                generator=generator,
            ).images[0]
        elif job["mode"] == "inpaint_existing_candidate":
            source_path = PACKAGE_ROOT / job["reference_file"]
            source = Image.open(source_path).convert("RGB")
            mask = make_mask(source.size, job["mask_rects_norm_xyxy"], feather=8)
            result = pipe(
                prompt=job["prompt"],
                negative_prompt=job["negative_prompt"],
                image=source,
                mask_image=mask,
                width=source.width,
                height=source.height,
                strength=0.92,
                num_inference_steps=30,
                guidance_scale=5.0,
                generator=generator,
            ).images[0]
        else:
            raise ValueError(f"Unknown queue mode: {job['mode']}")

        output_path = unique_output_path(run_folder, job["output_stem"])
        temp_path = output_path.with_suffix(".partial.png")
        result.save(temp_path, format="PNG", optimize=True)
        temp_path.replace(output_path)
        elapsed = time.perf_counter() - start
        return {
            "job_id": job["job_id"],
            "batch_id": job["batch_id"],
            "output": output_path.relative_to(PROJECT_ROOT).as_posix(),
            "sha256": image_sha256(output_path),
            "seed": int(job["seed"]),
            "prompt": job["prompt"],
            "negative_prompt": job["negative_prompt"],
            "reference": job["reference_file"],
            "model": INPAINT_ID if job["mode"].startswith("inpaint") else SDXL_ID,
            "adapter": QUEUE["models"]["face_adapter_weight"] if job["mode"].startswith("text2img") else None,
            "gpu": GPU.name,
            "vram_gib": round(VRAM_GIB, 2),
            "peak_vram_gib": round(torch.cuda.max_memory_reserved() / 1024**3, 2),
            "elapsed_seconds": round(elapsed, 2),
            "created_utc": datetime.now(timezone.utc).isoformat(),
        }

    def run_approved_batch(batch_id: str):
        batch = next((b for b in QUEUE["batches"] if b["batch_id"] == batch_id), None)
        if batch is None:
            raise ValueError(f"Unknown batch: {batch_id}")
        jobs = [job for job in QUEUE["jobs"] if job["batch_id"] == batch_id]
        if not jobs or len(jobs) > 3 or len(jobs) != batch["count"]:
            raise RuntimeError("Queue integrity check failed: every batch must contain 1–3 listed jobs.")
        if batch_id == "B02" and not SELECTED_BIMAL_ANCHOR.is_file():
            raise FileNotFoundError(
                "B02 is blocked. Review B01, then save the chosen anchor as "
                f"{SELECTED_BIMAL_ANCHOR.relative_to(PROJECT_ROOT).as_posix()}"
            )
        print(f"About to run {batch_id}: {len(jobs)} image(s), one at a time, on {GPU.name}.")
        approval = input(f"Type APPROVE {batch_id} to spend GPU time on this exact batch: ").strip()
        if approval != f"APPROVE {batch_id}":
            print("No generation started.")
            return []

        run_id = datetime.now(timezone.utc).strftime(f"{batch_id}_%Y%m%dT%H%M%SZ")
        run_folder = OUTPUT_ROOT / run_id
        run_folder.mkdir(parents=True, exist_ok=False)
        pipe = load_anchor_pipeline() if batch_id == "B01" else load_inpaint_pipeline()
        manifest = []
        try:
            for job in jobs:
                row = execute_job(pipe, job, run_folder)
                manifest.append(row)
                print(f"Saved {row['output']} | {row['elapsed_seconds']}s | peak {row['peak_vram_gib']} GiB")
        finally:
            del pipe
            gc.collect()
            torch.cuda.empty_cache()

        manifest_path = run_folder / "run_manifest.json"
        manifest_path.write_text(json.dumps({"run_id": run_id, "batch_id": batch_id, "jobs": manifest}, indent=2), encoding="utf-8")
        print(f"Manifest: {manifest_path.relative_to(PROJECT_ROOT).as_posix()}")
        return manifest

    print("Generation functions are ready but idle. Nothing runs until you call run_approved_batch('B01' or 'B02').")
    """),
    md(r"""
    ## 6. Run only an approved batch

    1. Inspect the complete queue and mask previews above.
    2. Run `run_approved_batch("B01")`. It asks you to type `APPROVE B01` before downloading weights or generating the Bimal anchor.
    3. Review the output at full size. If selected, copy it to `storyboard_pipeline/lightning_noir_assets_v01/selected/BIMAL_FACE_ANCHOR_selected.png`.
    4. Only then run `run_approved_batch("B02")`; this batch contains exactly three repair candidates.

    Do not run both batches together. A rejected or weak face anchor is a reason to stop and refine the reference crop/prompt before B02.
    """),
    code(r"""
    # After a batch completes, run this cell to build a contact sheet from its manifest.
    def show_run_contact_sheet(manifest_path: Path):
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        cards = []
        for job in data["jobs"]:
            image_path = PROJECT_ROOT / job["output"]
            image = Image.open(image_path).convert("RGB")
            thumb = ImageOps.contain(image, (480, 360))
            card = Image.new("RGB", (500, 410), "#151515")
            card.paste(thumb, ((500 - thumb.width) // 2, 10))
            ImageDraw.Draw(card).text((12, 378), f"{job['job_id']} | seed {job['seed']}", fill="white")
            cards.append(card)
        sheet = Image.new("RGB", (500 * len(cards), 410), "#111111")
        for index, card in enumerate(cards):
            sheet.paste(card, (index * 500, 0))
        display(sheet)

    print("Pass the path to a run_manifest.json after generation; no images are selected automatically.")
    """),
    md(r"""
    ## 7. Review checklist and save credits

    For every candidate, inspect the full-resolution image for facial identity, age, hair/goatee, hands, clothing, props, text, accidental logos/watermarks, analog texture, and 4:3 framing. The notebook records seed, prompt, source reference, model, runtime, and peak VRAM in `run_manifest.json`.

    Keep generated files in `output/lightning_assets_v01/`. Select images manually by copying only approved candidates to a new `_selected` filename; do not replace the existing v01 stills. Use Lightning's sleep control after inference. Do not start the separate AI-video phase until these stills are approved; that phase needs its own visible queue and approval.
    """),
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10+"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUTPUT.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"Created {OUTPUT}")
