# Project NOIR ? Nishidak Broadcast

This folder is the independent working copy of [`sayan-bhattacharya/noir-analog-horror`](https://github.com/sayan-bhattacharya/noir-analog-horror). It has its own Git history and remote. SHE belongs to the separate `aianimationautomate` repository; the two projects do not share code, assets, audio, render caches, or notebooks.

NOIR is an analog-horror visual engine inspired by a corrupted 1994 Doordarshan Kendra Calcutta transmission and folk-horror signals from rural Bengal. The full screenplay is about 30:22. The current Colab compositor renders a 5:52 (352-second) workprint, so the screenplay and rendered film are not yet the same duration.

## Render profiles

- **Colab notebook:** [`colab_noir_accelerator.ipynb`](colab_noir_accelerator.ipynb) renders the current 5:52 workprint at 1280?720, 24 fps. `RENDER_PREVIEW = True` selects a 640?360, 12 fps draft.
- **Local Python CLI:** `config/global.yaml` currently sets a 360-second (6-minute) timeline at 1280?720, 24 fps. These profiles differ by eight seconds; check the timeline you intend to use before treating them as interchangeable.
- **Soundtrack:** `Noir.wav`, stored with Git LFS. Do not substitute the unrelated podcast sample in `audio/`.

## Quick start

```powershell
git lfs install
git lfs pull
python -m pip install -r requirements.txt
python -m noir_film.render_noir --quality final
```

The local CLI writes its master under `output/`. A quick draft can be rendered with:

```powershell
python -m noir_film.render_noir --preview
```

The Colab notebook can also retrieve `Noir.wav` through Git LFS, Google Drive, or a user upload. It explicitly rejects missing/short audio rather than replacing it.

## Project layout

- `noir_film/`, `config/`: rendering engine and timeline configuration
- `assets/`, `plates/`, `screenshots/`: NOIR-only image and video inputs
- `screenplay/`, `storyboard_pipeline/`: narrative and storyboard materials
- `output/`: generated renders, caches, and review artifacts; render MP4s and chunk caches are ignored by Git
- `Noir.wav`: original score, tracked using Git LFS

Use this folder as the NOIR Git root (`git -C noir_film_project status`). The parent `between-the-notes` workspace also contains other projects, but do not commit NOIR files to the SHE repository.
