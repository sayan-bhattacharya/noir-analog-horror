# NOIR music-video opening — Flow generation brief

## Project context

**NOIR is a visual music film cut to Atandra's `Noir.wav`, a 30:22 composition.** The authoritative opening in `NOIR_30MIN_MASTER_SCRIPT.md` is a six-second visual phrase: a near-black CRT, one suspended black droplet, a fine amber eye-aperture ring, then the Between the Notes emblem resolving with a soft phosphor halo. The score is quiet in this opening; the image should breathe with it.

The current compositor does something different: a logo-to-satellite-dish morph for two seconds, then a cut to aerial geography. That is the current 6-minute compositor cut, not the 30:22 screenplay opening. Do not use this generated material as an unrelated station ident, and do not add a satellite dish or signal beam unless that change is explicitly chosen.

## Nano Banana image prompt

> Create one widescreen 16:9 cinematic keyframe for a restrained visual music film. Almost-black curved CRT glass in a 1990s rural Bengal night palette. Center a thin, muted amber eye-aperture ring; within it, one suspended obsidian droplet hangs above a delicate hairline ripple. The Between the Notes station emblem is only beginning to resolve behind the ring as a faint, translucent phosphor afterimage, not yet fully stable. Keep most of the frame black, with quiet analog grain, fine scanlines, soft phosphor bloom, and no modern UI. The mood is patient and musical: a held breath in the opening seconds of Atandra's dark ambient composition. Precise centered geometry, restrained amber and blue-black tones, visual negative space, no satellite dish, no landscape, no extra symbols, no generated text, no watermark.

Use the current Between the Notes emblem artwork as an image reference if Flow can accept it. Keep any real lettering or branding out of the generated image; composite the approved logo as a clean layer in the edit.

## Flow image-to-video prompt

> Animate the supplied keyframe as the first six seconds of a slow, score-led visual music film. Keep the camera locked. 0.0–1.5 seconds: hold in near-silence visually; the single black droplet trembles once above the fine ripple, while the thin amber ring barely breathes. 1.5–4.5 seconds: the ring gently clarifies and the Between the Notes emblem emerges behind it as a translucent phosphor afterimage, resolving gradually without changing into another object. 4.5–6.0 seconds: the emblem settles into a steady three-layer halo; let the droplet and ring remain as the quiet omen. Match the soft, sparse opening of `Noir.wav`—no fabricated hit, sudden flash, or dramatic crescendo. Near-black CRT glass, restrained amber, subtle analog grain and scanlines. Preserve the composition and identity. No satellite dish, beam, aerial landscape, rapid movement, extra imagery, text, subtitles, logos invented by the model, or watermark.

At 00:06, the screenplay cuts into storm/news imagery. Make the final frame dark and stable so an editor can make that cut cleanly. If Flow's duration options cannot produce six seconds, generate its nearest supported duration and trim at the resolved-emblem hold.

## Source and render audit

- `Noir.wav` is the actual film soundtrack: 30:22 (1,822.46 seconds); the music transcription and screenplay reference it.
- The latest named master files are only 14-second, 640×360 previews. No complete 30:22 music-video master render is present.
- `config/global.yaml` and `render_noir.py` currently limit the compositor to six minutes / 360 seconds. Several storyboard beats later in the screenplay have no matching compositor implementation yet.
- The former five-second revision clip selected `audio/BetweenTheNotes_Podcast_5min.wav` ahead of `Noir.wav`. The audio-source priority has now been corrected in the renderer and preview script; regenerate preview clips before using them as score-synced evidence.
- Google Flow and the free video-generation MCPs were not exposed to the prior assistant session. No Flow still or video was generated.
