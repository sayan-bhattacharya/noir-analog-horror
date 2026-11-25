# NOIR storyboard pipeline

This folder is the editable source for the visual board of the 30:22 screenplay.

## Build the storyboard

From the repository root, run:

    python noir_film_project/storyboard_pipeline/generate_storyboard.py

Or double-click run_storyboard.bat in this folder. The script uses only Python's standard library and writes:

- noir_film_project/output/NOIR_storyboard.html — one self-contained offline HTML deliverable with embedded artwork, act filters, image zoom, printable layout, downloadable JSON, and per-shot prompt copy buttons.
- noir_film_project/output/NOIR_storyboard_shotlist.md — a prompt-first shot list for use in an image-generation studio.

Edit storyboard.json to change shot timing, descriptions, camera direction, text, sound, visual references, or generation prompts. Run the command again to rebuild both outputs. Add image references with paths relative to this folder, or use the built-in bedroom, fall, and corridor vector-previs illustrations.

## Imagination Studio handoff

The image prompts are intentionally stored with the shots and shown in each HTML card. In Imagination Studio, use Story & Production to plan shots and build a storyboard, or copy a card's prompt into Image generation. Bring the existing still into the app as a reference when a shot needs identity or style continuity. Save chosen generations into the project and change that shot's art path in storyboard.json; rebuilding embeds the new frame in the HTML automatically.

The upstream Studio exposes a local job API and an MCP server for queuing stills, but there is no Studio process or local server at 127.0.0.1:7870 on this machine. The checked-out environment reports Windows 10, while the Studio's current Windows setup instructions target Windows 11 on Arm / RTX Spark. Model downloads also have separate hardware and licensing requirements. This pipeline therefore works now without installing the Studio or downloading model weights. Studio code is Apache-2.0; each model's terms are separate. See the upstream repository before choosing a model:
https://github.com/Keys-Wasserman/Imagination-Studio-by-keys-Wasserman

## Artlist MCP handoff

The repository-root .mcp.json points VS Code's MCP-capable agent session at Artlist's remote MCP server. Codex's user-level configuration has also been given an artlist server entry. Complete the OAuth sign-in with `codex mcp login artlist`, then restart the Codex session so the newly connected server's tools can load. This current turn does not yet expose Artlist tools, so no image-generation jobs have been submitted.

Use [ARTLIST_NOIR_BRIEF.md](ARTLIST_NOIR_BRIEF.md) to pass the screenplay context and three continuity-matched image prompts. Artlist generations use account credits. Review the selected model and credit cost in Artlist before generating. Save approved stills to `noir_film_project/assets/artlist/`, then add their paths to `storyboard.json` and rebuild the HTML.

