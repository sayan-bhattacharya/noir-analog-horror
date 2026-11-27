# Audit Log

- 2026-11-28: Created AGENTS.md from the supplied NOIR project instructions.

- 2026-11-28: Added `storyboard_pipeline/audit_noir_assets.py` for a read-only media inventory and `storyboard_pipeline/NOIR_ASSET_AUDIT_v01.csv` (666-file initial snapshot).
- 2026-11-28: Added versioned Lightning still-generation plan, setup notes, clean notebook builder, and `NOIR_LIGHTNING_ASSET_GENERATOR_v01.ipynb`; generation was not run.
- 2026-11-28: Added `storyboard_pipeline/NOIR_ASSET_AUDIT_v02.csv` (685-file updated local snapshot).
- 2026-11-28: Added 10 versioned reference copies and 3 source copies under `storyboard_pipeline/lightning_noir_assets_v01/`, plus generation queue and SHA-256 provenance manifest. Original inputs were not edited.
- 2026-11-28: Updated the Lightning setup/plan documents to state that the current notebook only generates still candidates, the active clone must remain untouched, and the full render package is not self-contained because local assets and two video sources are absent from GitHub main.
