# NOIR Episode 0 — Lightning Studio Asset Plan v01

## Goal

Prepare a reproducible, GPU-aware notebook that can generate a reviewed set of photorealistic continuity stills for the five-minute Episode 0. It must run from a GitHub clone in Lightning Studio, preserve the existing NOIR assets, record prompts/seeds/model settings, and avoid spending GPU time before the user approves a batch.

## Scope

- Film target: 5:00 Episode 0, 1280×720 / 24 fps, with 4:3 CRT imagery inside 16:9.
- This package prepares **still-image candidates**. It does not generate video, run FFmpeg, render Blender, or assemble the film.
- Keep `Noir.wav`, existing AI stills, Blender files, and rendered concept images unchanged.
- Generate only assets that the audit confirms are missing. Reuse existing plates and renders wherever they cover the shot.
- Save candidates with versioned names under `output/lightning_assets_v01/`; never overwrite a previous run.

## Audit findings

- `audit_noir_assets.py` inventoried 666 files: 382 image files, 50 video files, 1 audio file, 26 3D assets, 15 Blender backup files, 88 notebooks/scripts, and 93 production documents. `ffprobe` successfully read metadata for all 51 audio/video assets.
- Existing assets already include a photographic Bimal face in the awakening still and a photographic, painted Trickster face in the doorway still. Episode 0's current character list has no additional named human men; do not invent background cast. A generated Bimal face anchor is still useful for future face-forward continuity shots.
- All three previous `NB_001`–`NB_003` images exist and appear in the 18-card storyboard. They are useful composition candidates, not final selections: `NB_001` contains unintended shirt/sign/timestamp text; `NB_002` has a visible sparkle-like overlay; `NB_003` has a visible overlay and branded shirt text. Prepare correction candidates instead of regenerating the three scenes from scratch.
- The 50-entry `shot_list_EP0_v02.csv` and the 18-beat `storyboard_to_episode0_mapping.md` use different numbering schemes. Preserve both source files and add an explicit crosswalk before assigning final per-card timing.
- Six shot-list rows reference two absent clips: `15002113_3840_2160_60fps.mp4` (4 rows) and `20200549-uhd_2160_3840_60fps.mp4` (2 rows). The checked-in 640×360, 12 fps story preview is only 14 seconds and is not a substitute for either source.
- `story_development/` and its character references are present locally but are not in `origin/main`. A clone-ready package therefore needs a small, versioned reference pack and the Episode 0 planning files copied into the tracked pipeline folder.
- Model choice: SDXL Base plus Apache-2.0 IP-Adapter Plus Face for the Bimal anchor, and SDXL inpainting for localized text/overlay cleanup. Face conditioning encourages continuity but does not guarantee exact identity; every candidate must be reviewed.

## Dependency order

### Phase 1 — Inventory and source reconciliation

1. Run `audit_noir_assets.py` to inventory files, image dimensions, video/audio metadata, and exact shot-list source matches.
2. Mark existing candidates, missing sources, untracked local-only sources, and obsolete `.blend1` backups separately.
3. Use the 50-entry shot list as the detailed cut list; retain the 18-beat map as a grouping proposal until a crosswalk resolves ID conflicts.

**Checkpoint:** audit report exists and the missing-image queue contains only assets with no usable existing source.

### Phase 2 — Clone-ready reference package

1. Copy, without moving or editing originals, the selected Bimal, Trickster, cat, Trinetra, corridor, and Master Control references into a new versioned `lightning_noir_assets_v01/` folder.
2. Include versioned copies of the Episode 0 CSV and 18-beat mapping, with SHA-256 provenance back to their original paths.
3. Keep generated outputs and model caches outside source/reference folders.

**Checkpoint:** all notebook inputs are contained in tracked project paths; no source image is overwritten.

### Phase 3 — Generation notebook

1. Clone the repository and locate the versioned reference pack.
2. Run asset/Git/GPU preflight on CPU; install only the Python inference dependencies, preserving Lightning's preinstalled PyTorch/CUDA stack.
3. Display the full prompt queue, references, output names, model/license notes, and dependency order before any model download or generation.
4. Load SDXL in FP16 with PyTorch SDPA, TF32, VAE slicing, batch size 1, deterministic seeds, and GPU-memory telemetry. Use model CPU offload only when VRAM is insufficient.
5. Require explicit typed batch approval, cap each batch at three images, write `_candidate_v01` outputs atomically, and append prompt/settings/hashes to a manifest.
6. Produce a contact sheet and a review CSV; do not mark candidates selected automatically.

## Prepared still queue (not submitted)

| Order | Batch | Asset | Reference | Purpose |
|---|---|---|---|---|
| 1 | B01 (1 image) | Bimal face/wardrobe anchor | Existing awakening still | Photorealistic, neutral 4:3 identity reference. Review and select before dependent fixes. |
| 2 | B02 (3 images) | Corrected EXIT 0 CCTV plate; corrected cosmic Kalo Hulo/Trinetra plate; corrected Master Control plate | The three existing candidate plates plus the approved Bimal anchor | Inpaint only unwanted text/overlay regions; preserve the established composition and character. |

These are proposed candidates. The notebook must print complete prompts for all four before any batch runs. The project’s approval gate still applies to each batch. No video jobs are included; those require a separate approved queue capped at 8–12 shots.

## Lightning Studio usage and cost controls

- Clone and audit on CPU; install packages and inspect references before switching to a GPU.
- Switch to GPU only for the approved inference batch. The notebook detects GPU name, VRAM, dtype support, and peak allocated/reserved memory.
- Generate one image at a time at 1024×768 (4:3); upscale only selected images after review.
- Cache model weights in the persistent Studio home, not inside Git or the output folder.
- Sleep the Studio when idle. GPU selection and hourly rates vary by account/region, so the notebook reports the hardware it sees rather than assuming a specific credit cost.

## Acceptance criteria

- [ ] A fresh clone contains the notebook, reference pack, queue, and required Episode 0 source files.
- [ ] CPU preflight reports missing files and GPU availability without downloading model weights.
- [ ] The printed queue contains four complete prompts, grouped 1/3 and ordered by identity dependency.
- [ ] Generation refuses to run without explicit batch approval and never submits more than three images per batch.
- [ ] Every saved image has a deterministic seed and a manifest row; reruns use new candidate suffixes.
- [ ] A review contact sheet/CSV is created, and no output is marked selected automatically.

## Risks and limitations

| Risk | Impact | Mitigation |
|---|---|---|
| Episode 0 source IDs conflict across the 50-row CSV and 18-beat map | Wrong shot timing or labels | Keep both originals; create a crosswalk before final timing. |
| Source footage from the brief is absent | Road shots cannot be generated from the named source clips | Keep them flagged missing; do not pretend generated stills replace footage. |
| Reference pack differs from GitHub `main` | A normal clone cannot find local-only AI stills | Put small versioned copies in the tracked package and report that main needs a pushed branch. |
| IP-Adapter face conditioning is approximate | Face drift across shots | Establish and review a Bimal anchor first; inspect every dependent candidate; use local relighting/crops rather than assuming exact identity. |
| Model download / GPU rates vary | Setup and credit spend varies | Preflight before download; keep output count and resolution fixed; user explicitly approves each batch. |

## Documentation and provenance

The audit CSV, reference provenance manifest, generation queue, notebook, setup notes, and project `audit_log.md` together record what was inspected, copied, generated, and reviewed. A generation is considered “done” only after the user selects it; generated candidates remain labeled as candidates until then.


## Prepared package status (2026-11-28)

- Completed the CPU-side inventory and produced `NOIR_ASSET_AUDIT_v02.csv`. The v01 report remains an earlier snapshot.
- Packaged ten versioned references and three Episode 0 planning sources under `lightning_noir_assets_v01/`; source originals were not edited. SHA-256 source/copy pairs are recorded in `provenance_manifest_v01.csv`.
- Built `NOIR_LIGHTNING_ASSET_GENERATOR_v01.ipynb` as a clean, unexecuted notebook. It performs CPU preflight, prints the full queue, gates batches with typed approval, caps each batch at three outputs, writes candidates and provenance, and requires manual selection before dependent repairs.
- No model weights were downloaded and no image generation was run. The four candidates remain queued for the user to review and approve in Lightning Studio.
- Clone instructions target `codex/noir-lightning-assets-v01`; that branch must be published before the command can work.
- Implementation references: [Lightning AI getting started](https://lightning.ai/docs/platform/overview/getting-started), [Lightning Studio persistence](https://lightning.ai/docs/platform/build/ai-studio/environment-persistence), [Lightning Studio start and stop](https://lightning.ai/docs/platform/build/ai-studio/start-and-stop-studio), [Diffusers IP-Adapter](https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter), [Diffusers memory optimization](https://huggingface.co/docs/diffusers/optimization/memory), [SDXL model card](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0), [SDXL inpainting model card](https://huggingface.co/diffusers/stable-diffusion-xl-1.0-inpainting-0.1), [IP-Adapter model card](https://huggingface.co/h94/IP-Adapter).


## User's separate-clone requirement and full-film scope

The user's current Storyboard Reference Studio/NOIR working clone must remain untouched. Any published or Lightning Studio clone is a separate directory (`noir-lightning-pipeline`). The current asset generator notebook only makes still-image candidates. It does not invoke Blender, extract animation frames, conform footage, or stitch the final five-minute master.

The local source tree is approximately 609 MB and is not part of GitHub `main`; `Noir.wav` is approximately 321 MB. Two required shot-list source clips are missing locally. A self-contained full-film clone therefore needs an intentional media transfer strategy (repository/LFS or Lightning Drive), those source clips, a portable path rewrite for the existing scripts, and a reconciled cut list. This packaging gap must be resolved before promising a one-command five-minute render.
