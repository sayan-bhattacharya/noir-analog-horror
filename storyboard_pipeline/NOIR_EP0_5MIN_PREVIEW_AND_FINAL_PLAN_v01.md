# NOIR Episode 0 ? Five-Minute Preview and Final Pipeline Plan v01

## Goal

Produce a reviewable five-minute NOIR Episode 0 visualization in a separate Lightning Studio clone, then refine and render the approved cut as a 1280?720, 24 fps master with a 4:3 CRT image inside the 16:9 canvas and the opening five minutes of `Noir.wav`.

The preview is a complete timed cut for story, rhythm, and continuity review. It is not the final-quality render. Existing AI stills are plates; Blender supplies the primary world; Google Flow / Nano Banana Pro is reserved for gaps and continuity fixes. Use image-to-video for no more than the approved 8?12 key motion shots.

## Current state and evidence

- The separate remote clone is on branch `codex/noir-lightning-assets-v01`. The earlier `noir_lightning_pipeline_v01.py` only generates SDXL still candidates; it does not invoke Blender, extract scene frames, or assemble a movie.
- A Bimal candidate and three B02 inpaint candidates were generated in Lightning. B02 logged CLIP prompt truncation beyond 77 tokens; treat its images as unreviewed candidates, not approved plates.
- The local source tree already contains three five-minute prototype MP4s: `NOIR_Episode0_PlanC_v01.mp4`, `noir_5min_hybrid_master_000_300.mp4`, and `noir_5min_ai_vibe_000_300.mp4`. They are local reference cuts, not delivered in the Lightning branch and not proof that the fresh clone can rebuild them.
- Existing local Blender scripts use hard-coded Windows paths. The concept gallery and lighting studies select Eevee; the existing five-minute Python scripts composite image/video plates with OpenCV and invoke FFmpeg. They are not a portable, complete Blender-GPU-to-master workflow.
- The 50-row detailed shot list and 18-beat storyboard map do not have a confirmed one-to-one ID crosswalk. The detailed list references two clips not found in the local audit: `15002113_3840_2160_60fps.mp4` and `20200549-uhd_2160_3840_60fps.mp4`.
- The local package includes `.blend` scenes, AI stills, textures, intertitle cards, renders, and a 321 MB `Noir.wav`. Those production inputs are not in the Lightning branch. Do not assume the new clone can see files from the workstation or from the separate `she-blender-4k` clone.

## Working boundary

- Keep the user's existing `she-blender-4k` rendering clone unchanged. All new NOIR work stays in the separate `noir-lightning-pipeline` directory and branch.
- Use Lightning Drive or another deliberate media-transfer route for large production inputs; keep Git for scripts, cut manifests, small references, and documentation. Preserve originals and use new versioned output paths.
- Check for existing tools before installation. The project instructions require approval before installing software, downloading production assets, running Blender/FFmpeg, rendering, or assembling a master.
- The user's Google Flow / Nano Banana Pro authorization applies to missing NOIR image assets. Show the full image queue and use references; avoid duplicate or redundant scenes. Each generated still stays a candidate until reviewed. Keep the AI-video queue within 8?12 shots.

## Dependency order

### Phase 1 ? Make the new clone self-sufficient

**Work:** Create a portable media manifest for the separate clone. Verify Blender version, FFmpeg/ffprobe, Python packages, GPU visibility, free disk, and every source path. Stage only required inputs: selected `.blend` scenes and linked textures, existing AI stills/plates, storyboard/intertitle cards, relevant source footage, and the exact 0:00?5:00 audio segment or the source WAV. Exclude `.blend1` backups, old full-length exports, caches, and unrelated videos from the render input set.

**Acceptance:** A preflight report in the new clone finds every shot's source or marks it missing, with no hard-coded workstation paths. Existing working clones/files remain untouched.

### Phase 2 ? Lock the 300-second picture plan

**Work:** Use the 18 mapped beats as the story structure and reconcile the 50 detailed rows into a single explicit cut manifest. Resolve all start/end times to exactly 300 seconds at 24 fps; mark every beat as Blender animation, existing rendered plate, source video, Flow still/video, intertitle, or intentional black. Resolve each missing source clip to an available approved substitute or remove that use from the preview.

**Acceptance:** One versioned manifest totals 300 seconds, has no overlapping/gap timing errors, and every cut has a verified source path, framing treatment, and audio/cut intent. Keep Bengali-first text and English translations as post-composited typography.

### Phase 3 ? Prove the GPU render path cheaply

**Work:** Inspect scene render engines before changing them. Render one representative frame from the bedroom, corridor, and any other scene used in the preview at low resolution. Configure the scene's supported Eevee or Cycles GPU path deliberately; do not globally switch engines. Record actual device, engine, resolution, samples, elapsed time, and peak memory. Check camera, materials, linked assets, and 4:3 safe area.

**Acceptance:** Test frames visibly use the intended GPU path, have no missing assets, and preserve the NOIR look. Use the measured frame time to estimate full render time before rendering sequences.

### Phase 4 ? Generate only confirmed visual gaps

**Work:** Compare every timeline row against existing Blender renders, AI plates, and source footage. Build a deduplicated Flow / Nano Banana Pro queue for genuinely missing stills and continuity fixes. Keep Bimal's selected face anchor and approved references attached where useful. Create image-to-video jobs only for selected key motion shots, capped at 8?12.

**Acceptance:** The complete queue includes shot ID, reference(s), exact prompt, output path, aspect ratio, and intended use. Candidate outputs are reviewed before entering the preview. Do not regenerate a scene already covered by an acceptable Blender render or plate.

### Phase 5 ? Build the first five-minute visualization

**Work:** Produce any required Blender sequences at proxy settings and reuse stills with controlled camera movement/parallax for non-action beats. Conform footage to the centered 4:3 CRT window in 16:9. Assemble exactly 300 seconds at 24 fps, then add the matching opening audio from `Noir.wav`, Bengali/English cards, restrained signal treatment, and intentional black/silence. Use a unique `preview_v01` output path.

**Acceptance:** The entire preview plays from beginning to end; runtime is 5:00, frame rate 24 fps, frame size 1280?720 (or an explicitly labeled proxy), audio begins at the correct timestamp and is synchronized, and every cut uses an existing or reviewed candidate source. Create a contact sheet and render log.

### Checkpoint ? Human preview review

Review the complete film for story comprehension, pacing, Bimal identity, Bengali/English typography, visual continuity, and audio sync. Record change requests by shot ID. Do not make final-quality renders before this review checkpoint.

### Phase 6 ? Finalize and render

**Work:** Apply approved changes to a new cut-manifest version. Promote only manually selected assets, regenerate only specifically approved fixes, render Blender shots at final settings, then conform and assemble to a unique `final_v01` path. Preserve the original `Noir.wav`; mux the intended 300-second segment and verify video/audio metadata and end frame.

**Acceptance:** Final master is 1280?720, 24 fps, 4:3 CRT image inside 16:9, 4:45?5:15 runtime, correct Bengali-first title treatment, synchronized audio, no missing or placeholder media, and a manifest/log records sources, settings, output hashes, and selection status.

## Immediate next actions

1. Inventory files visible inside `noir-lightning-pipeline` and compare them with the local asset audit; do not use or modify the `she-blender-4k` clone.
2. Identify the exact Blender scenes and cut manifest required for the first five minutes; resolve the 18/50 timing crosswalk.
3. Verify availability of the two referenced clips, `Noir.wav`, cards, renders, linked textures, Blender, FFmpeg, and disk space in the separate Studio.
4. Stage required media through the approved transfer route, then run only the low-cost GPU sample renders and record a measured ETA.
5. Prepare a deduplicated Flow still queue from confirmed gaps; review candidates, then produce `preview_v01` and review it before final rendering.

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| `.blend` scenes and linked media are absent from the new clone | No Blender render can start | Transfer a minimal, checksummed input package to the separate Studio and preflight every dependency. |
| Two listed source clips are missing | Road and phone-camera beats cannot use the named footage | Locate/upload them or explicitly replace those manifest rows before rendering. |
| 18-beat map and 50-row shot list disagree | Wrong runtime or ordering | Treat 18 as the story-beat structure and author an explicit 50-row cut crosswalk before assembly. |
| Old scripts hard-code workstation paths and some use Eevee | Remote failures or unexpected render behavior | Make paths repository-relative/configurable and retain the scene's intended render engine. |
| T4 is 16 GB and render time is unknown | GPU job may exceed credits/time budget | Benchmark representative frames first; use proxy settings and sparse Blender animation rather than rendering every static beat as 3D. |
| B02 prompt truncation | Repairs may ignore late instructions | Inspect and reject unsuitable candidates; shorten future prompts and enforce CLIP token limits before diffusion. |

## Approval and cost checkpoints

- Preview/queue creation and metadata inspection are read-only or local-only planning steps.
- Before installing software, transferring/downloading media, rendering Blender, running FFmpeg, or assembling a movie, show the exact inputs, output path, settings, and expected runtime for that step.
- Before each Flow/Nano Banana batch, show the complete deduplicated queue. The user's current authorization permits Flow for missing NOIR image assets; keep batches focused and retain candidate labels.
