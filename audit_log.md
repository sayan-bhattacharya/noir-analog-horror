# Audit Log

- 2026-11-28: Created AGENTS.md from the supplied NOIR project instructions.

- 2026-11-28: Added `storyboard_pipeline/audit_noir_assets.py` for a read-only media inventory and `storyboard_pipeline/NOIR_ASSET_AUDIT_v01.csv` (666-file initial snapshot).
- 2026-11-28: Added versioned Lightning still-generation plan, setup notes, clean notebook builder, and `NOIR_LIGHTNING_ASSET_GENERATOR_v01.ipynb`; generation was not run.
- 2026-11-28: Added `storyboard_pipeline/NOIR_ASSET_AUDIT_v02.csv` (685-file updated local snapshot).
- 2026-11-28: Added 10 versioned reference copies and 3 source copies under `storyboard_pipeline/lightning_noir_assets_v01/`, plus generation queue and SHA-256 provenance manifest. Original inputs were not edited.
- 2026-11-28: Updated the Lightning setup/plan documents to state that the current notebook only generates still candidates, the active clone must remain untouched, and the full render package is not self-contained because local assets and two video sources are absent from GitHub main.
- 2026-11-28: Updated the Lightning notebook GPU preflight to initialize CUDA, select visible GPU 0, report runtime/VRAM, and explain that hardware selection must be changed in Lightning Studio; updated setup guide.
- 2026-11-28: Added `storyboard_pipeline/noir_lightning_pipeline_v01.py`, a logged CLI runner with safe preflight/queue modes, typed per-batch approval, CUDA reporting, model-load and denoising-step progress, and per-image runtime/VRAM/hash records; added `NOIR_LIGHTNING_CLI_SETUP_v02.md`. Generation was not run.
- 2026-11-28: Added `storyboard_pipeline/NOIR_EP0_5MIN_PREVIEW_AND_FINAL_PLAN_v01.md`, a dependency-ordered Blender-first preview-to-final plan covering the separate Lightning clone, missing inputs, the 18/50 cut crosswalk, GPU benchmark, Flow asset queue, preview checkpoint, final render, and approval gates. No media was rendered, generated, transferred, or assembled in this planning step.
