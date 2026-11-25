# NOIR Full-Length Film and Soundtrack Delivery Plan

## Objective

Deliver a complete 30:22 NOIR music video with its original score, `Noir.wav` by Atandra. The export must contain picture across the full track, preserve the project's quiet-to-uncanny pacing, and be reviewable in sections before the expensive full render.

## Current state verified in the project

- `Noir.wav` and the timestamped screenplay specify a 30:22 film (about 1,822.5 seconds).
- The Colab notebook is explicitly a 05:52 workprint and sets `RENDER_SECONDS = 352`.
- `noir_film/timeline.py` has developed visual coverage through 06:00; the last 8 seconds are the goofy creature beat. Its generic final `else` continues returning that creature shot after the designed sequence, so increasing render duration today would repeat a stale shot for most of the track.
- `noir_film/modular_cache.py` only declares modules through 06:00. `render_noir.py` can render longer durations, but that only extends the current timeline behavior; it does not implement the remaining screenplay.
- Two screenplay documents coexist: `screenplay/NOIR_30MIN_TIMESTAMPED_SCRIPT.md` (revised dramatic approach) and `NOIR_30MIN_MASTER_SCRIPT.md` (older, denser sequence plan). They differ in beats and timing, so the team must reconcile them before extending picture.
- The current notebook requires the original `Noir.wav`; it must never substitute podcast audio or another soundtrack.

## Delivery decisions

1. Keep the final runtime tied to the measured source score, targeting 1,822.46 seconds / 30:22, with the exact measured duration recorded during preflight.
2. Treat the revised timestamped screenplay as the preferred dramatic/pacing direction, then reconcile any unique required beats from the master script into one approved beat sheet. Preserve NOIR's identity and continuity; do not borrow assets or material from Between The Notes podcast or SHE.
3. Do not label a 05:52/06:00 render as the full film. Keep it as a clearly named workprint until all remaining timeline ranges have actual scene coverage.
4. Render and review in acts/chunks with handles, then join picture and mux the original score once at final assembly. This limits rerender cost and avoids soundtrack drift between chunks.

## Dependency order

Approved source score + reconciled beat sheet → complete timecoded scene map → assets and shot implementations → act previews and review → full-duration render → soundtrack mux and technical QC → final delivery package.

## Work plan

### Phase 1 — Lock story and audio inputs

**Task 1: Verify the soundtrack master.** Record the exact `Noir.wav` path, sample rate, channel count, sample count, measured duration, and a SHA-256 checksum in the render manifest. Inspect the track once and confirm there is no narration/podcast audio.

Acceptance: the manifest identifies `Noir.wav` as the only audio source and records a duration consistent with 30:22; no fallback audio path can silently choose another file.

**Task 2: Reconcile the screenplays.** Compare the revised timestamped screenplay and the 30-minute master script into one approved beat sheet with start/end time, action, character state, transition, text, and required assets. Resolve overlapping or conflicting timestamps and identify any intentionally changed beats.

Acceptance: every second from 00:00 to the score end belongs to a named beat or deliberate hold; all 30-second-plus quiet passages have purposeful visual progression; the approved document identifies which screenplay is authoritative.

Checkpoint: review the reconciled beat sheet and act timing before building the remaining film.

### Phase 2 — Complete timeline and assets

**Task 3: Audit existing coverage.** Map current timeline branches and media to the approved beat sheet, marking each segment implemented, partial, missing, or requiring replacement. Carry forward approved Shot 30 portal, Bimal's slip/fall, sparse flicker, cloud motion, and character-continuity requirements.

Acceptance: an asset/shot coverage table spans the entire 30:22 and explicitly flags footage gaps, uncertain references, and generated assets that are unavailable locally.

**Task 4: Implement missing acts in bounded sections.** Extend the timeline with explicit, reviewable acts and shot ranges. Build each act around the score's dynamics while preserving pauses and natural image holds. Every interval must have intentional visuals, a hold, a transition, or a deliberate black frame; no accidental last-frame/creature repetition.

Acceptance: timeline coverage reaches the measured score end; time outside the film is rejected or intentionally handled; shot boundaries and transitions align with the approved map.

**Task 5: Extend modular rendering/cache.** Add cache modules for the full approved shot map and ensure each module invalidates when its timeline branch or referenced media changes. Keep outputs chunkable and resumable.

Acceptance: each act can be rerendered without rebuilding unrelated acts, and cached outputs cannot be reused after a referenced shot or asset changes.

Checkpoint: render a short representative passage from each act and inspect continuity, character identity, text legibility, visual pacing, and transitions against the score.

### Phase 3 — Notebook and staged review renders

**Task 6: Update the Colab notebook for the complete film.** After timeline coverage exists, set the render target from the measured score duration rather than a hard-coded 352 seconds. Keep Drive mounting optional with a direct `Noir.wav` upload fallback. Save outputs to a clearly named NOIR folder and expose per-act preview and resumable full-render controls.

Acceptance: notebook fails clearly if `Noir.wav` is missing; preview/full settings are unambiguous; no source path or upload flow can select podcast audio; interrupted act renders can resume.

**Task 7: Stage and review.** Generate 4–5 second samples at every high-risk transition (especially opening, 03:17–03:22 portal/fall, first creature reveal, act changes, ending), then produce act-length low-resolution previews. Update the storyboard to show frames extracted from the actual rendered film and link each image to its source shot/asset.

Acceptance: transition samples show the intended action and the original score; act previews are reviewed before the full-quality render.

Checkpoint: picture approval across all acts before final-quality full render.

### Phase 4 — Full render, soundtrack, and delivery

**Task 8: Render the complete picture.** Render all acts at final dimensions/frame rate with consistent color, frame rate, and transition handles. Join chunks in timecode order, remove overlaps using the agreed edit points, and confirm there are no gaps or duplicate frames at joins.

**Task 9: Mux and verify the score.** Mux the original `Noir.wav` once against the assembled picture. Confirm codec, channels, start alignment, measured duration, and the final fade. Do not normalize, replace, or recompose the score unless that is explicitly in the approved audio plan.

Acceptance: final video runs for the score's measured duration (within one frame of the target), has continuous synchronized `Noir.wav`, and contains no unintended podcast audio, silence padding, frozen tail, or repeated fallback shot.

**Task 10: Package deliverables.** Provide the final MP4, a review copy if useful, the storyboard HTML with actual film frames, render manifest (source checksum, settings, duration, output checksum), and a concise QC report. Keep all changes in the standalone NOIR repository.

## Main risks and mitigations

| Risk | Mitigation |
|---|---|
| Two scripts disagree on sequence/timing | Reconcile them into one approved beat sheet before implementation. |
| Existing renderer repeats the last creature beat beyond the designed timeline | Require explicit full-runtime coverage and an end-of-timeline guard before long renders. |
| Full render is expensive or interrupted | Render preview acts first; use independently cached, resumable act chunks. |
| Wrong audio is muxed | Pin `Noir.wav` by path and checksum; reject unknown audio instead of silently falling back. |
| Cloud or generated media is referenced but unavailable in the repo | Inventory local media and verify each dependency before picture approval. |
| Chunk boundaries create audio/video gaps | Keep a frame-accurate time map, join picture first, then mux the score once. |

## Immediate next step

Complete Task 1 and Task 2, then present the reconciled 30:22 beat sheet for review. Once it is approved, implement and preview the missing acts. Only after full timeline coverage and act review should the notebook target the complete score and launch the final render.

## Current readiness

**Not ready for a full-length render.** The score and screenplay are full length, but the compositor is currently developed only through approximately 06:00 and the two screenplay sources need reconciliation. The existing 05:52 Colab output remains a workprint, not a final film.
