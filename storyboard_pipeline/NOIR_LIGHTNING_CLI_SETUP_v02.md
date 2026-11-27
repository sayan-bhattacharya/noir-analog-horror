# NOIR Lightning CLI setup v02

This is the logged Python-script workflow for the still-image queue. The earlier notebook remains available, but the CLI is easier to monitor from the Studio terminal. It does not render Blender scenes, extract animation frames, or assemble the five-minute film.

## Update the separate clone

In the terminal for `noir-lightning-pipeline` (the existing rendering clone stays untouched), update the branch:

```bash
git pull --ff-only
```

Run the following from the repository root. `python -u` keeps console output live. Every run also writes a timestamped log under `output/lightning_assets_v01/logs/`.

## Safe first run

```bash
python -u storyboard_pipeline/noir_lightning_pipeline_v01.py --mode preflight
```

This checks references and reports Python, PyTorch, CUDA, GPU count, GPU name, and VRAM. It does not download model weights or generate images. If inference libraries are missing, install them without replacing Lightning's CUDA-enabled PyTorch build:

```bash
python -m pip install "diffusers>=0.35,<0.37" "transformers>=4.44,<5" "accelerate>=0.33" "safetensors>=0.4" "peft>=0.10" "Pillow>=9"
```

If CUDA is unavailable, switch the Studio to a GPU in the Lightning hardware selector, wait for restart, then rerun preflight. Python cannot change the Studio machine type. The visible T4 has about 16 GiB VRAM; the runner enables model CPU offload below 18 GiB. That reduces VRAM use and can slow inference.

## Review before generation

Print every prompt and negative prompt first. This also saves red-overlay mask previews under `output/lightning_assets_v01/mask_previews_v01/` without generating AI images:

```bash
python -u storyboard_pipeline/noir_lightning_pipeline_v01.py --mode queue
```

Read the queue output and inspect the reference files. The runner does not submit work in `preflight` or `queue` mode.

## Generate one approved batch

Run Bimal's anchor first:

```bash
python -u storyboard_pipeline/noir_lightning_pipeline_v01.py --mode generate --batch B01
```

The script prints the exact job, then waits for `APPROVE B01`. Until that exact response is entered, it does not load models or generate images. Watch the terminal for model-load phases, denoising steps, elapsed time, memory, and output hash. The same timestamped log is written to disk. After the batch, a contact sheet is saved beside the candidates.

Inspect the saved Bimal candidate manually. If selected, copy it to `storyboard_pipeline/lightning_noir_assets_v01/selected/BIMAL_FACE_ANCHOR_selected.png`. Then review B02's full queue and run: 

```bash
python -u storyboard_pipeline/noir_lightning_pipeline_v01.py --mode generate --batch B02
```

B02 stops unless the selected Bimal anchor exists, and asks for `APPROVE B02` before loading the inpainting model. Its three images run sequentially; each batch is capped at three images. Outputs and `run_manifest.json` are saved in a unique directory under `output/lightning_assets_v01/`. The original candidate images remain unchanged.

Do not launch both generation commands together. Stop after B01 if the face needs refinement. Sleep the Studio when finished to avoid idle GPU use.
