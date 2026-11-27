# NOIR Episode 0 — Lightning Studio Setup v01

## What this package prepares

- A clean Lightning Studio notebook for four still-image candidates: one Bimal identity anchor, followed by three repairs to the existing CCTV, hyper-object, and Master Control plates.
- A compact versioned reference pack so the notebook does not depend on the local-only `story_development/` directory.
- A source/copy SHA-256 manifest, full prompts, mask previews, GPU preflight, explicit per-batch approval, and per-run metadata/contact sheets.
- No new generation has been submitted. Existing v01 plates remain untouched; new output is saved under ignored `output/lightning_assets_v01/` paths with candidate suffixes.

## Clone and open in Lightning Studio

After the package branch `codex/noir-lightning-assets-v01` is published, clone it with:

```bash
git clone --branch codex/noir-lightning-assets-v01 https://github.com/sayan-bhattacharya/noir-analog-horror.git noir-lightning-pipeline
cd noir-lightning-pipeline
```

Open `storyboard_pipeline/NOIR_LIGHTNING_ASSET_GENERATOR_v01.ipynb` from JupyterLab. The notebook checks its own repository root and all packaged references.

## Cost-conscious run order

1. On the CPU Studio, run the repository/input preflight and review `generation_queue_v01.json`.
2. Install the Python inference libraries without replacing Lightning's PyTorch/CUDA build.
3. Review the three inpaint-mask previews. No model weights are downloaded by the preflight or queue cells.
4. Switch to one 24 GB GPU (L4 if available) for inference. A larger GPU is not needed for single-image SDXL generation at 1024×768.
5. Run B01 only after reviewing its prompt, then type `APPROVE B01` when asked. Inspect the Bimal face closely. B02 is blocked until a selected Bimal anchor is saved at `storyboard_pipeline/lightning_noir_assets_v01/selected/BIMAL_FACE_ANCHOR_selected.png`.
6. Review the complete B02 queue and type `APPROVE B02` to generate its three candidate repairs. No automatic selection occurs.
7. Inspect every image at full size. Keep only manually selected files; all candidates include generation metadata and SHA-256 hashes.
8. Sleep the Studio between sessions. Lightning Studio files and packages persist while sleeping.

Check current availability and billing in [Lightning AI pricing](https://lightning.ai/pricing); GPU rates depend on instance and provider. The notebook reports actual GPU, elapsed seconds, and peak VRAM but cannot query your account balance or estimate an exact run price.

## Existing assets and gaps

`NOIR_ASSET_AUDIT_v02.csv` is the current local inventory. The first audit found 666 files: 382 images, 50 videos, 1 audio file, 26 3D assets, 15 `.blend1` backups, 88 notebooks/scripts, and 93 production documents. `ffprobe` read all 51 audio/video files.

The realistic Bimal awakening still and Trickster doorway still are existing identity references. The queue does not invent additional human cast for Episode 0. The three previous generated plates are composition candidates but contain unwanted typography/graphic artifacts; this pass repairs those regions.

Six rows in the detailed 50-shot CSV reference two absent source videos:

- `15002113_3840_2160_60fps.mp4` — four shot rows
- `20200549-uhd_2160_3840_60fps.mp4` — two shot rows

Upload those source clips to Lightning Drive if they are available on another device. The notebook does not synthesize replacement footage. The 14-second 640×360 story preview is not a master source.

The five-minute cut list has 50 detailed rows while the storyboard mapping uses 18 IDs. Keep both source files; resolve their ID crosswalk before using timing as a locked cut.

## Model and license notes

- Base image model: [Stable Diffusion XL 1.0 Base](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0), CreativeML Open RAIL++-M.
- Inpainting model: [SDXL 1.0 Inpainting](https://huggingface.co/diffusers/stable-diffusion-xl-1.0-inpainting-0.1), based on the SDXL license.
- Face adapter: [IP-Adapter](https://huggingface.co/h94/IP-Adapter), Apache-2.0. The notebook uses the SDXL Plus-Face adapter with a cropped image embedding. This encourages likeness but cannot guarantee identical facial identity. Bimal anchor review is mandatory.
- The FaceID adapter is intentionally not selected because Diffusers documents those FaceID weights as research-only.

Review model terms before using outputs in a monetized release. Text, logo, and intertitle typography should be added in post, not generated into plates.

## How the existing files relate

- `colab_noir_accelerator.ipynb` is a prior Colab workprint-render notebook; it is not the new Lightning image-generation notebook.
- `story_development/output/storyboard/noir_episode0_board.json` is the exported 18-card visual board used as a source copy here.
- `story_development/production/shot_list_EP0_v02.csv` is the detailed 50-row cut list; its numbering differs from the 18-card board.
- New images remain candidates until reviewed; no final-video rendering or audio conform is part of this notebook.

## References

- [Lightning AI Studio quick start](https://lightning.ai/docs/platform/overview/getting-started)
- [Lightning Studio environment persistence](https://lightning.ai/docs/platform/build/ai-studio/environment-persistence)
- [Lightning Studio start/stop and idle costs](https://lightning.ai/docs/platform/build/ai-studio/start-and-stop-studio)
- [Diffusers IP-Adapter guide](https://huggingface.co/docs/diffusers/en/using-diffusers/ip_adapter)
- [Diffusers GPU memory guide](https://huggingface.co/docs/diffusers/optimization/memory)

## Full-film pipeline boundary

This package branch is based on the repository's tracked `main`; it does not yet contain the local-only `story_development/` production tree. The local tree is about 609 MB, `Noir.wav` is about 321 MB, and the two source clips `15002113_3840_2160_60fps.mp4` and `20200549-uhd_2160_3840_60fps.mp4` were not found. The existing 5-minute renders and Blender project assets in the current working copy are not automatically present in a fresh clone.

Therefore this v01 clone is not yet a self-contained Blender render-and-stitch package. Do not start a full render from it expecting the missing files to be available. To finish that package, the production sources must be staged into the new repository/Lightning Drive, and the 50-shot list must be reconciled with the 18-card map. GPU use should be focused on Cycles Blender rendering and approved image generation; final frame conform and audio mux are separate FFmpeg steps. The current notebook does not run either the Blender or FFmpeg steps.

## GPU access and execution

Python cannot turn on a Lightning GPU or change the Studio machine type. First use the Studio hardware/environment selector to switch to a GPU and let the Studio restart. The notebook then initializes CUDA, selects visible GPU 0, reports the CUDA runtime and VRAM, and stops with instructions if CUDA is unavailable. It deliberately uses one GPU and one image at a time; extra GPUs will not speed up this notebook. A 24 GB L4 is the recommended fit. This uses GPU acceleration for SDXL still inference only; this v01 notebook does not render Blender scenes or assemble the film.

