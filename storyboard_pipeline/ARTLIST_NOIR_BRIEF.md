# NOIR — Artlist generation brief

Use this brief as shared context for image generation in Artlist. The revised screenplay is at noir_film_project/screenplay/NOIR_30MIN_TIMESTAMPED_SCRIPT.md; the frame timings and prompts below are the initial asset brief.

## Film context

**Title:** NOIR — The Nishidak Broadcast  
**Logline:** During an unlisted late-night emergency broadcast, Bimal Babu, a solitary Bengali clerk, follows a familiar call into the countryside. A black liquid, an impossible cat, and a watching eye draw him into a fall that ends in a fluorescent corridor where the broadcast's rules still apply.  
**Format:** 30:22 silent visual narrative; 4:3 archival image within a 16:9 master.  
**Visual arc:** rural Bengal and tactile analog dread → cosmic scale → a sudden, nearly clean fluorescent corridor → a restrained circular image that closes the loop.

## Continuity bible

- **Bimal Babu:** ordinary middle-aged Bengali clerk, average build, short dark hair with a little grey, thin moustache, rumpled off-white cotton shirt and dark high-waisted trousers. Keep his face, hair, build and clothes identical across every generation. He is watchful and deliberate, never an action hero.
- **Rural scenes:** old Bengal house, wet paddy earth, banana leaves, bamboo, rusted cast-iron handpump, humid monsoon night. Keep the place lived-in and materially specific.
- **Broadcast treatment:** 1990s CRT curvature, soft monochrome grain, restrained phosphor green/amber, occasional signal drift. Add all words and logos later in HTML/video; never ask the image model to render exact typography.
- **Cosmic restraint:** one anomaly at a time. Do not add gore, generic demons, fantasy armor, random symbols, or extra monsters.
- **Corridor:** spotless white tile, cool fluorescent light, one yellow tactile strip. The shift should feel calm and clinical before it feels wrong.
- **Composition:** design each image as a clear storyboard keyframe, with strong silhouettes and clean negative space. 16:9 export, composed for a central 4:3 safe frame.
- **Text policy:** no legible text, subtitles, logos, watermarks or UI baked into generated images.
- **Rights/style:** original visual language. Do not reproduce a film frame or imitate a living filmmaker's exact style.

## Initial three stills

Generate one still for each prompt. Keep one shared Bimal identity across all three; use the first output as a character reference for the later two if Artlist permits reference images. These are storyboard assets, not final video shots.

### A — Bimal character anchor

**Target file:** noir_film_project/assets/artlist/NOIR_bimal_character_anchor.png  
**Shot:** neutral character reference, medium portrait.

> Original cinematic character reference for Bimal Babu, an ordinary middle-aged Bengali office clerk, average build, short dark hair lightly touched with grey, thin moustache, tired observant eyes, rumpled off-white cotton shirt and dark high-waisted trousers. Neutral three-quarter stance, hands visible, reserved expression, no heroic posing. A dim rural Bengal room in the background, kerosene-lamp warmth, tactile natural materials, restrained near-monochrome archival 1990s television texture, carefully preserved facial detail. Centered 4:3-safe composition inside a 16:9 frame. No text, no logo, no watermark, no supernatural features.

### B — The threshold / familiar call

**Target file:** noir_film_project/assets/artlist/NOIR_bimal_threshold.png  
**Shot:** medium-wide profile, Act I, 03:15–06:00.

> Use the Bimal character reference to preserve his face, hair, moustache, build and exact off-white shirt and dark trousers. Inside an old rural Bengal bedroom at night, Bimal sits at the edge of a wooden bed beneath a sheer cotton mosquito net, listening toward a dark open window. He checks the doorway, puts on his shoes and pauses at the threshold before stepping out. The pose should read as a practical, deliberate choice, not panic. Damp lime plaster, one dim kerosene lamp, quiet negative space. 1990s analog broadcast image, restrained monochrome with a trace of warm amber, subtle CRT grain. 16:9 frame with central 4:3 safe composition. No insect, no monster, no text, no watermark.

### C — The corridor test

**Target file:** noir_film_project/assets/artlist/NOIR_corridor_test.png  
**Shot:** deep one-point perspective, Act V, 21:00–25:00.

> Use the Bimal character reference to preserve his face, hair, moustache, build and clothing. In a spotless underground corridor of white square tiles, Bimal stands on a single yellow tactile strip, seen from behind and small in frame. Far down the hall, an ordinary pale middle-aged man in a charcoal suit holds a briefcase and remains motionless. Cool fluorescent strips create strong one-point perspective. The corridor is calm, clinical and nearly monochrome; no horror makeup, no visible gore, no dramatic action. Composition leaves clean space around both figures and keeps the vanishing point centered. 16:9 frame with central 4:3 safe composition. Do not add signs or legible text, no logos, no watermark.

## After generation

1. Review all three stills for Bimal identity and visual continuity before approving them.
2. Save the chosen stills under the target filenames above.
3. Update the matching shots in storyboard_pipeline/storyboard.json to reference the new files with paths relative to that folder.
4. Rebuild the HTML board with python noir_film_project/storyboard_pipeline/generate_storyboard.py.
5. Do not render motion until the still frames are approved.

