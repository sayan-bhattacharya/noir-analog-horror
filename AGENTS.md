# NOIR — Project Instructions

## Project

NOIR is a Bengali-English analog-horror short film.

- Canonical full film: 30:22
- Current deliverable: NOIR — Episode 0: The Broadcast Begins
- Target runtime: 5:00, acceptable range 4:45–5:15
- Master soundtrack: Noir.wav, 30:22
- Output format: 1280 × 720, 24 fps
- Visual format: 4:3 CRT frame inside a 16:9 canvas
- Language: Bengali-first intertitles and dialogue, with English translations
- Genre: analog horror, surreal psychological horror, liminal spaces, Bengali folklore, CRT/VHS decay

## Core story

Bimal, a quiet archivist who restores old tapes, wakes beside his bed with no memory at 2:14 a.m. He carries only a candle. He explores a Bengali apartment, follows impossible rules, enters an endless surveillance corridor, confronts a cosmic hyper-object, and discovers that he is inside a CRT broadcast.

Theme: Being watched is not the same as being known.

The final revelation:
Bimal is not watching the broadcast. He is inside it. The audience’s attention keeps the broadcast alive.

## Five movements

1. DESCENT — 00:00–03:57  
   Doordarshan emergency interruption, storm loop, Bimal wakes, match and candle, newspaper, wall insect, moshari shadows, unplugged CRT, bricked East door, crimson dot, Rule 1.

2. APOCALYPTICA — 03:57–10:00  
   Pukur ghat, alpona, black cat Kalo Hulo, mirror Trinetra, DMT Trickster, idol/kathamo transitions, room dissolves.

3. MELANCHOLIA — 10:00–18:08  
   Hard cut on silence into monochrome EXIT 0 corridor, repeating doors, CCTV, second crimson dot, surveillance realization.

4. HEDONIA — 18:08–27:54  
   Hyper-object black cat over Bengal horizon, Trinetra, void, Master Control CRT bank, bedroom delayed by three seconds.

5. ASCENT — 27:54–30:22  
   Bimal holds candle to central CRT, camera pulls back through television bezel, Bimal is a silhouette inside the screen, final broadcast intertitle, CRT collapse.

## Rules and lore

1. Do not open the East door twice.  
   Bengali: পূর্ব দিকের দরজা দু'বার খুলো না।

2. Do not answer a voice that knows your name.

3. Do not let the candle go out before dawn.

4. If you see yourself on a screen, do not look away.

## Characters and entities

### Bimal
- Late 20s / early 30s
- Heavy-metal t-shirt
- Dark half-pants
- Goatee
- Quiet, exhausted, South Asian/Bengali appearance
- Must remain visually consistent across all stills, renders, and generated media

Assets:
- bimal_dressed.blend
- bimal_xbot.blend
- bimal_metal_tshirt_tex.png
- Mixamo Xbot.glb rig

### Trinetra
- One crimson geometric eye
- Backed by an 8D wireframe polytope lattice
- Appears in mirrors, CRTs, voids, and surveillance spaces

Assets:
- trinetra.blend
- ai_06_mirror_trinetra*.jpg

### DMT Trickster
- Gothic/fractal Trickster Clown
- Mimics Bimal’s posture
- Appears in doorways and voids

Assets:
- ai_09_clown_trickster_doorway*.jpg
- trickster.blend

### Kalo Hulo / Black Cat
- Gaunt black cat
- First appears at the pukur ghat
- Later becomes a cosmic hyper-object

Assets:
- concrete_cat_statue_1k.blend
- black_cat_variants.blend
- ai_08_pukur_ghat_black_cat*.jpg

### Wall Insect
- Segmented beetle/cockroach
- Has a detached oversized shadow
- Shadow may move before the insect

Assets:
- insect.blend
- ai_03_wall_insect_shadow*.jpg

## Existing assets

Do not assume files exist. Verify paths before using them.

### Blender scenes and renders
- bimal_apartment_roam.blend
- bengali_bedroom.blend
- sterile_corridor.blend
- candle.blend
- newspaper.blend
- mirror.blend
- crt_tv.blend
- bimal_utter_dark_candle_walk.mp4
- concept_01_the_awakening.png
- concept_02_the_mosquito_net.png
- concept_03_the_wall_insect.png
- concept_04_the_first_trinetra.png
- concept_05_the_trickster.png
- concept_06_the_cat.png
- concept_07_the_hyper_object.png
- concept_08_exit_0.png
- concept_09_master_control.png
- concept_10_the_final_broadcast.png

### AI stills
Located in:
story_development/assets/ai_scenes/

- ai_01_awakening_match_strike_*.jpg
- ai_02_roaming_*.jpg
- ai_03_wall_insect_shadow_*.jpg
- ai_04_moshari_*.jpg
- ai_05_unplugged_crt_static_*.jpg
- ai_06_mirror_trinetra_*.jpg
- ai_07_bricked_east_door_*.jpg
- ai_08_pukur_ghat_black_cat_*.jpg
- ai_09_clown_trickster_doorway_*.jpg
- ai_10_kathamo_exit_0_*.jpg

### Reference photos
Located in:
story_development/assets/textures/

- ref_01 through ref_05
- Polytope geometry
- Bengal gatehouse
- Pukur ghat with alpona
- Radha-Krishna and Saraswati ghat idols
- Straw kathamo idol

### Original NOIR assets
Located in:
noir_film_project/

- Noir.wav
- noir_audio_features_24fps.npy
- output/text_audit/ — 30 pre-rendered silent dialogue cards
- plates/*.jpg
- assets/flow_storm_loop.mp4

### New 4K footage
- 15002113_3840_2160_60fps.mp4
  - 3840 × 2160
  - 16:9
  - 59.94 fps
  - 28.83 seconds
  - Use for realistic highway opening and recurring road-memory motif

- 20200549-uhd_2160_3840_60fps.mp4
  - 2160 × 3840
  - Vertical
  - 60 fps
  - 5.63 seconds
  - Use as a brief B&W phone-camera/found-footage interruption
  - Crop or pillarbox; never stretch

## Visual language

- 4:3 CRT framing inside 16:9
- 1990s Bengali apartment
- Candlelight, limewash walls, aged teak, terracotta, red oxide cement
- Mosquito net / moshari
- Pukur ghat, alpona, kathamo, Bengali idols
- VHS transfer, interlacing, chroma bleed, tracking noise, grain, crushed blacks
- CRT scanlines, static, crimson REC dots
- Monochrome corridors, fluorescent lights, EXIT 0
- Restrained dread, no gore, no cheap jump scares
- Bengali-first silent-film intertitles with English translations

## Editing philosophy

The film must feel like a corrupted broadcast, not a slideshow.

Use this rule:
- Hold ordinary images longer.
- Cut strange images sooner.
- Cut on revelation, not decoration.

Target pacing:
- Realistic highway: 4–8 seconds
- Bimal waking/candle: 3–6 seconds
- First wrong details: 1–3 seconds
- Insect, mirror, CRT, corridor: 1–4 seconds
- Hyper-object and Master Control: 3–8 seconds
- Final CRT pull-back: 5–10 seconds

Aim for approximately 55–70 total cuts across 5 minutes.

Every cut must:
- Reveal information
- Repeat an image with a difference
- Change location or scale
- Land on an audio onset
- Create silence or signal loss
- Advance Bimal’s emotional state

Do not make every shot 1–2 seconds.
Do not leave a still completely motionless for more than 4 seconds unless it is an intentional intertitle, held reveal, or final image.

## Production hierarchy

1. Existing Blender renders are the primary world.
2. Existing AI stills are plates and memory fragments.
3. Nano Banana creates only missing continuity stills and alternate angles.
4. AI image-to-video is reserved for 8–12 key motion shots.
5. Hard cuts, parallax, flicker, repetition, and sound create most movement.
6. Noir.wav remains the master soundtrack.

## Nano Banana rules

Use Nano Banana only for:
- Missing continuity stills
- Alternate camera angles
- Character consistency fixes
- Transition frames
- Props, textures, and CRT inserts

Use reference images whenever possible.

Nano Banana prompt formula:
[REFERENCE IMAGES] + [WHAT MUST REMAIN IDENTICAL] + [WHAT CHANGES] + [NEW SCENARIO] + [CAMERA / LENS] + [LIGHTING] + [FILM STOCK / ARTIFACTS] + [COMPOSITION] + [ASPECT RATIO]

Never use vague prompts such as “make it scary” or “cinematic horror.”

Always show the complete generation queue before generating.

## AI video rules

Generate AI video for no more than 8–12 shots.

Priority shots:
1. Realistic highway to CRT-static transition
2. Bimal waking and lighting candle
3. Wall insect shadow twitch
4. East door opening to bricked wall
5. Mirror reveal of Trinetra
6. Trickster mimicking Bimal
7. Corridor walk and repeated door
8. Hyper-object cat reveal
9. Master Control CRT bank
10. Final camera pull-back through CRT bezel

Every AI video must:
- Begin from an approved still
- Be 2–6 seconds
- Use 24 fps
- Use 4:3 CRT framing
- Preserve Bimal, bedroom, candle, CRT, and NOIR visual language
- Be reviewed for identity drift, morphing, warped hands, flicker, and color mismatch

## Approval gates

Always ask before:
- Installing software
- Connecting MCP servers
- Generating Nano Banana images
- Generating AI video
- Downloading assets
- Deleting files
- Overwriting existing files
- Running FFmpeg
- Rendering Blender
- Assembling the final video

Show a generation queue before every batch.

## File safety

Never overwrite:
- Noir.wav
- Blender files
- Existing AI stills
- Reference photos
- Existing renders
- Pre-rendered cards
- Original storyboard HTML

Use version suffixes:
- _v02
- _candidate
- _selected
- _graded
- _final

Maintain audit_log.md for every file created, moved, renamed, or modified.

## Required workflow

1. Audit existing files and footage with ffprobe.
2. Parse the original 24-shot NOIR storyboard HTML.
3. Create the revised Episode 0 shot list with sub-shots.
4. Create a visual storyboard/contact sheet.
5. Identify missing Nano Banana stills.
6. Show Nano Banana generation queue for approval.
7. Generate stills in batches of no more than 3.
8. Review each still for continuity.
9. Identify AI video shots.
10. Show AI video generation queue for approval.
11. Generate video in small batches.
12. Review each video.
13. Create a silent animatic.
14. Show the silent animatic.
15. After approval, conform audio and assemble the final 5-minute master.