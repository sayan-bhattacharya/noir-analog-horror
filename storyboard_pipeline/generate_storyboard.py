#!/usr/bin/env python3
"""Build a self-contained storyboard HTML and a prompt shot list from storyboard.json."""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "storyboard.json"
DEFAULT_HTML = HERE.parent / "output" / "NOIR_storyboard.html"
DEFAULT_SHOTLIST = HERE.parent / "output" / "NOIR_storyboard_shotlist.md"


def esc(value):
    return html.escape(str(value), quote=True)


def sketch(kind):
    start = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900">
    <defs><linearGradient id="b" x2="0" y2="1"><stop stop-color="#24231f"/><stop offset="1" stop-color="#070808"/></linearGradient>
    <pattern id="s" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0 1H8" stroke="#eee" stroke-opacity=".07"/></pattern></defs>
    <rect width="1600" height="900" fill="url(#b)"/><rect width="1600" height="900" fill="url(#s)"/>
    <rect x="76" y="52" width="1448" height="796" rx="7" fill="none" stroke="#b9ad91" stroke-opacity=".4" stroke-width="3"/>
    <text x="112" y="110" fill="#d1b76f" font-family="monospace" font-size="24" letter-spacing="5">NOIR / STORYBOARD STUDY</text>"""
    if kind == "bedroom":
        art = """<path d="M100 680H1500M160 180V680M1440 180V680" stroke="#aaa18c" stroke-opacity=".55" stroke-width="5" fill="none"/>
        <rect x="1170" y="205" width="244" height="265" fill="#0a0c0d" stroke="#aaa18c" stroke-opacity=".7" stroke-width="6"/>
        <path d="M1290 205V470M1170 335H1414" stroke="#77796e" stroke-width="4"/>
        <path d="M338 575H1090V682H338Z" fill="#171816" stroke="#bbb096" stroke-opacity=".7" stroke-width="6"/>
        <path d="M290 553H1138L1080 429H369Z" fill="#26251f" stroke="#bbb096" stroke-opacity=".64" stroke-width="5"/>
        <path d="M350 422L1095 422M390 423L420 564M1075 423L1041 563" stroke="#c4bda9" stroke-opacity=".52" stroke-width="5" fill="none"/>
        <path d="M370 422L424 564M478 422L505 564M592 422L609 564M706 422L709 564M820 422L815 564M934 422L919 564M1048 422L1022 564" stroke="#d7d0bf" stroke-opacity=".12" stroke-width="3"/>
        <circle cx="742" cy="475" r="30" fill="#090a0a"/><path d="M697 505Q742 482 787 505L805 561H679Z" fill="#101110"/>
        <path d="M735 504L703 546M755 504L788 548" stroke="#101110" stroke-width="18"/>
        <circle cx="218" cy="553" r="27" fill="#d3a45c" opacity=".8"/><path d="M218 582V648" stroke="#d3a45c" stroke-opacity=".45" stroke-width="4"/>
        <text x="800" y="781" fill="#aaa18c" font-family="monospace" font-size="27" text-anchor="middle">BIMAL LISTENS · THEN CHOOSES</text>"""
    elif kind == "fall":
        art = """<ellipse cx="800" cy="512" rx="420" ry="248" fill="#020303" stroke="#c3b38d" stroke-opacity=".5" stroke-width="5"/>
        <ellipse cx="800" cy="512" rx="303" ry="178" fill="none" stroke="#7f817b" stroke-opacity=".22" stroke-width="3"/>
        <ellipse cx="800" cy="512" rx="182" ry="102" fill="none" stroke="#7f817b" stroke-opacity=".18" stroke-width="3"/>
        <path d="M96 198L515 362M1500 160L1085 360M128 702L487 597M1468 728L1097 602" stroke="#b9b09b" stroke-opacity=".34" stroke-width="9"/>
        <path d="M786 434L817 454L804 493L774 514L745 498L760 466Z" fill="#d4cbb4"/><circle cx="786" cy="416" r="19" fill="#ded5bf"/>
        <path d="M773 487L728 529M803 489L859 527M767 459L709 447M808 461L868 433" stroke="#d4cbb4" stroke-width="14" stroke-linecap="round"/>
        <path d="M112 260H1488M138 642H1463" stroke="#f1eee4" stroke-opacity=".12" stroke-width="2"/>
        <text x="800" y="781" fill="#aaa18c" font-family="monospace" font-size="27" text-anchor="middle">GROUND TILTS · BIMAL FALLS BACKWARD</text>"""
    elif kind == "corridor":
        art = """<path d="M190 175L800 392L1410 175M190 175V620L800 790V392M1410 175V620L800 790" fill="none" stroke="#d5d0c3" stroke-opacity=".52" stroke-width="5"/>
        <path d="M190 280L800 455L1410 280M190 400L800 526L1410 400M190 520L800 617L1410 520" fill="none" stroke="#a9a79e" stroke-opacity=".28" stroke-width="3"/>
        <path d="M370 175V671M560 175V738M1040 175V738M1230 175V671" stroke="#c8c3b4" stroke-opacity=".24" stroke-width="3"/>
        <path d="M755 790L774 400M845 790L826 400" stroke="#d6b977" stroke-width="8" opacity=".8"/>
        <rect x="716" y="196" width="168" height="58" fill="#23251f" stroke="#d6b977" stroke-width="2"/><text x="800" y="235" fill="#e3d28e" font-family="monospace" font-size="27" text-anchor="middle">EXIT 8</text>
        <circle cx="800" cy="440" r="22" fill="#090a09"/><path d="M769 468Q800 449 831 468L848 574H752Z" fill="#101110"/><path d="M771 486L744 575M829 486L856 575M775 572L770 665M825 572L830 665" stroke="#101110" stroke-width="18"/>
        <text x="800" y="781" fill="#aaa18c" font-family="monospace" font-size="27" text-anchor="middle">BIMAL TESTS THE EMPTY CORRIDOR</text>"""
    else:
        raise ValueError("Unknown storyboard illustration: " + str(kind))
    return start + art + "</svg>"


def frame_source(shot, root):
    if shot.get("art"):
        path = (root / shot["art"]).resolve()
        if not path.is_file():
            raise FileNotFoundError("Shot " + shot["id"] + " is missing " + str(path))
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        relative = Path(os.path.relpath(path, DEFAULT_HTML.parent)).as_posix()
        return relative, path.name
    svg = sketch(shot["illustration"])
    content = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return "data:image/svg+xml;base64," + content, "Original vector previs sketch"


def card(shot, root):
    src, label = frame_source(shot, root)
    prompt = esc(shot["prompt"])
    image = '<img src="' + src + '" alt="' + esc(shot["title"]) + ' storyboard frame" loading="lazy">'
    return f"""<article class="card" data-act="{esc(shot['act'])}" id="shot-{esc(shot['id'])}">
      <div class="picture" tabindex="0" role="button" aria-label="Expand {esc(shot['title'])}">{image}
        <div class="corners"><span>{esc(shot['id'])}</span><span>{esc(shot['time'])}</span></div><span class="source">{esc(label)}</span></div>
      <div class="copy"><div class="kicker"><span>{esc(shot['act'])}</span><span>{esc(shot['time'])}</span></div>
        <h3>{esc(shot['title'])}</h3>
        <div class="spec"><b>FRAME</b>{esc(shot['frame'])}</div><div class="spec"><b>CAMERA</b>{esc(shot['movement'])}</div>
        <p>{esc(shot['story'])}</p><div class="cue"><b>ON-SCREEN TEXT</b><br>{esc(shot['text'])}</div>
        <div class="cue sound"><b>SOUND</b><br>{esc(shot['sound'])}</div>
        <details><summary>Image-generation prompt</summary><p>{prompt}</p><button class="copy" data-prompt="{prompt}">Copy prompt</button></details>
      </div></article>"""


def build_html(data, root):
    shots = data["shots"]
    cards = "\n".join(card(s, root) for s in shots)
    preview = data.get("rendered_preview")
    preview_block = ""
    if preview:
        preview_block = f'''<section class="note rendered-preview" aria-label="Rendered compositor preview">
<strong>{esc(preview['title'])} | {esc(preview['time'])}</strong>
<p>{esc(preview['story'])}</p>
<video controls preload="metadata" poster="{esc(preview['poster'])}" src="{esc(preview['video'])}"></video>
<p><b>Sound:</b> {esc(preview['sound'])}<br><span>{esc(preview['status'])}</span></p>
<a href="{esc(preview['video'])}">Open the five-second video</a></section>'''
    acts = list(dict.fromkeys(s["act"] for s in shots))
    filters = '<button class="filter active" data-filter="all">All frames</button>' + "".join(
        '<button class="filter" data-filter="' + esc(act) + '">' + esc(act) + "</button>" for act in acts
    )
    nav = "".join('<a href="#shot-' + esc(s["id"]) + '">' + esc(s["id"]) + " · " + esc(s["act"]) + "</a>" for s in shots)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(data['title'])} — Storyboard</title><style>
:root{{--bg:#10110f;--ink:#f2eee3;--muted:#aaa69a;--line:#35352f;--gold:#d6b977;--green:#91aa91}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(ellipse at 50% -20%,#363226,transparent 54%),var(--bg);color:var(--ink);font:15px/1.55 Inter,Segoe UI,Arial,sans-serif}}
.shell{{width:min(1440px,calc(100% - 42px));margin:auto}}header{{padding:48px 0 28px;border-bottom:1px solid var(--line)}}
.eyebrow,.kicker,.corners,.source,.meta span,.spec b,.cue b{{font:10px ui-monospace,Consolas,monospace;letter-spacing:.1em;text-transform:uppercase}}
.eyebrow{{color:var(--gold)}}h1{{font:500 clamp(40px,7vw,78px)/1 Georgia,serif;letter-spacing:-.04em;margin:20px 0 8px}}.subtitle{{font:italic 21px Georgia,serif;color:#c9c0ad}}
.meta,.tools,.nav,.filters{{display:flex;gap:8px;flex-wrap:wrap}}.meta{{margin-top:23px}}.meta span{{border:1px solid #49483e;padding:6px 9px;color:#d2cbbb}}
.tools{{margin-top:25px}}button{{font:inherit}}.tools button,.copy,.tool-link{{color:var(--ink);background:#25251f;border:1px solid #5a5645;padding:8px 12px;cursor:pointer;text-decoration:none;font:12px Inter,Segoe UI,Arial,sans-serif}}
.nav{{overflow:auto;flex-wrap:nowrap;padding:18px 0 8px}}.nav a{{white-space:nowrap;color:var(--muted);text-decoration:none;border-bottom:1px solid var(--line);padding:6px 9px;font:10px ui-monospace,Consolas,monospace}}
.overview{{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:26px 0 20px}}h2{{font:26px Georgia,serif;margin:0 0 4px}}.overview p{{color:var(--muted);margin:0;max-width:760px}}
.filter{{white-space:nowrap;background:none;border:1px solid var(--line);color:var(--muted);padding:7px 10px;cursor:pointer}}.filter.active{{background:var(--gold);color:#111;border-color:var(--gold)}}
.note{{border-left:2px solid var(--gold);background:#1b1b17;color:#c5bdad;padding:11px 15px;font-size:12px;margin-bottom:20px}}
.rendered-preview video{{display:block;width:min(100%,900px);margin:10px 0;background:#050505}}.rendered-preview p{{max-width:900px}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px;padding-bottom:60px}}
.card{{display:grid;grid-template-columns:1fr 1fr;background:#191a17;border:1px solid var(--line);overflow:hidden;min-height:330px;transition:transform .2s,border-color .2s}}.card:hover{{transform:translateY(-2px);border-color:#777052}}
.picture{{position:relative;min-height:300px;background:#080908;overflow:hidden;cursor:zoom-in}}.picture img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(.8) contrast(1.04)}}
.picture:after{{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(0deg,#090a09bb,transparent 28%),repeating-linear-gradient(0deg,#fff08 0 1px,transparent 1px 4px);mix-blend-mode:screen}}
.corners{{position:absolute;z-index:1;inset:11px 12px auto;display:flex;justify-content:space-between;text-shadow:0 1px 7px #000}}.source{{position:absolute;z-index:2;left:10px;bottom:10px;background:#111d;color:#d1c6ad;padding:4px 6px;font-size:8px}}
.copy{{padding:17px;min-width:0}}.kicker{{display:flex;justify-content:space-between;gap:6px;color:var(--green);font-size:9px}}.kicker span+span{{color:var(--gold);white-space:nowrap}}
h3{{font:400 24px/1.1 Georgia,serif;margin:12px 0}}.spec{{display:grid;grid-template-columns:55px 1fr;gap:8px;color:#d7d1c4;font-size:11px;margin:5px 0}}.spec b,.cue b{{color:#938d7e;font-size:8px}}
.copy>p{{font-size:12px;line-height:1.5;color:#d0cbbc;margin:13px 0}}.cue{{border-top:1px solid #38382f;padding-top:8px;margin-top:8px;color:#cfc7b5;font-size:10px;line-height:1.5}}.sound{{color:#9eaa9f}}
details{{border-top:1px solid #38382f;padding-top:8px;margin-top:10px}}summary{{cursor:pointer;color:var(--gold);font-size:10px}}details p{{color:#bbb5a8;font-size:10px;line-height:1.5}}.copy{{font-size:10px;color:#ead7a1}}
footer{{border-top:1px solid var(--line);padding:20px 0 34px;color:var(--muted);font-size:11px}}footer a{{color:var(--gold)}}
.modal{{display:none;position:fixed;z-index:10;inset:0;background:#050606f4;align-items:center;justify-content:center;padding:25px;cursor:zoom-out}}.modal.open{{display:flex}}.modal img{{max-width:95vw;max-height:88vh;object-fit:contain}}.modal-label{{position:fixed;bottom:15px;color:#d5cdbb;font:11px ui-monospace,Consolas,monospace}}.hidden{{display:none!important}}
@media(max-width:1000px){{.grid{{grid-template-columns:1fr}}}}@media(max-width:620px){{.shell{{width:calc(100% - 24px)}}header{{padding-top:32px}}.overview{{display:block}}.filters{{margin-top:13px;overflow:auto;flex-wrap:nowrap}}.card{{grid-template-columns:1fr}}.picture{{min-height:0;aspect-ratio:16/9}}.copy{{padding:15px}}}}
@media print{{body{{background:#fff;color:#111}}header{{padding:8px 0}}.tools,.nav,.filters,details,.source{{display:none!important}}.grid{{gap:7px}}.card{{break-inside:avoid;background:white;border:1px solid #aaa;min-height:0}}.copy>p,.cue,.spec{{color:#222}}.picture{{min-height:180px}}footer{{color:#333}}}}
</style></head><body>
<header><div class="shell"><div class="eyebrow">● &nbsp; PROJECT NOIR &nbsp; / &nbsp; DIRECTOR'S BOARD &nbsp; / &nbsp; 30:22</div>
<h1>{esc(data['title'])}</h1><p class="subtitle">{esc(data['subtitle'])}</p>
<div class="meta"><span>{esc(data['runtime'])} master</span><span>{esc(data['format'])}</span><span>{len(shots)} key frames</span><span>Visual reference pass</span></div>
<div class="tools"><button onclick="window.print()">Print / save as PDF</button><button id="download">Download shot manifest</button><button id="toggle-prompts">Open all prompts</button><a class="tool-link" href="NOIR_asset_explorer.html">Browse every project image ↗</a><a class="tool-link" href="NOIR_revision_review.html">06:00 render review ↗</a></div></div></header>
<main class="shell"><nav class="nav" aria-label="Storyboard chapters">{nav}</nav>
<div class="overview"><div><h2>Shot-by-shot visual treatment</h2><p>{esc(data['look'])}</p></div><div class="filters">{filters}</div></div>
<div class="note"><strong>Version note:</strong> this is the 30:22 NOIR music-film treatment based on <em>NOIR_30MIN_MASTER_SCRIPT.md</em> and the track <em>Noir.wav</em>. The current compositor covers six minutes; the inline video is a five-second working preview using the matching score excerpt, not a finished master export. The revision review is <a href="NOIR_revision_review.html" style="color:var(--gold)">here</a>.</div>
{preview_block}
<section class="grid">{cards}</section></main>
<footer><div class="shell">Source: <a href="../screenplay/NOIR_30MIN_TIMESTAMPED_SCRIPT.md">revised timestamped screenplay</a> · Built from storyboard_pipeline/storyboard.json · Offline, self-contained HTML</div></footer>
<div class="modal" id="modal" role="dialog" aria-modal="true"><img alt="Expanded storyboard frame"><div class="modal-label"></div></div>
<script id="manifest" type="application/json">{payload}</script><script>
const cards=[...document.querySelectorAll('.card')];
document.querySelectorAll('.filter').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('.filter').forEach(x=>x.classList.remove('active'));b.classList.add('active');cards.forEach(c=>c.classList.toggle('hidden',b.dataset.filter!=='all'&&c.dataset.act!==b.dataset.filter));}}));
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(b.dataset.prompt);b.textContent='Copied';setTimeout(()=>b.textContent='Copy prompt',1200)}}catch{{b.textContent='Copy unavailable; select prompt above'}}}}));
document.getElementById('toggle-prompts').addEventListener('click',()=>{{const d=[...document.querySelectorAll('details')],open=d.some(x=>!x.open);d.forEach(x=>x.open=open)}});
document.getElementById('download').addEventListener('click',()=>{{const a=document.createElement('a'),u=URL.createObjectURL(new Blob([document.getElementById('manifest').textContent],{{type:'application/json'}}));a.href=u;a.download='NOIR_storyboard.json';a.click();URL.revokeObjectURL(u)}});
const modal=document.getElementById('modal'),big=modal.querySelector('img'),label=modal.querySelector('.modal-label');
document.querySelectorAll('.picture').forEach(p=>{{const open=()=>{{big.src=p.querySelector('img').src;label.textContent=p.closest('.card').querySelector('h3').textContent;modal.classList.add('open')}};p.addEventListener('click',open);p.addEventListener('keydown',e=>{{if(e.key==='Enter'||e.key===' '){{e.preventDefault();open()}}}})}});
modal.addEventListener('click',()=>modal.classList.remove('open'));document.addEventListener('keydown',e=>{{if(e.key==='Escape')modal.classList.remove('open')}});
</script></body></html>"""


def build_shotlist(data):
    lines = ["# " + data["title"] + " — Storyboard shot list", "", data["studio_handoff"], ""]
    for s in data["shots"]:
        lines += [f"## {s['id']} · {s['title']} ({s['time']})",
                  f"**Act:** {s['act']}  ", f"**Frame:** {s['frame']}  ",
                  f"**Camera:** {s['movement']}  ", f"**Story:** {s['story']}  ",
                  f"**Text:** {s['text']}  ", f"**Sound:** {s['sound']}  ",
                  "**Image prompt:**", "", s["prompt"], ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--shotlist", type=Path, default=DEFAULT_SHOTLIST)
    args = parser.parse_args()
    manifest = args.manifest.resolve()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not data.get("shots"):
        raise ValueError("Storyboard contains no shots.")
    seen = set()
    required = ("act", "time", "title", "frame", "movement", "story", "text", "sound", "prompt")
    for s in data["shots"]:
        if not s.get("id") or s["id"] in seen:
            raise ValueError("Storyboard shot IDs must be present and unique.")
        seen.add(s["id"])
        missing = [key for key in required if not s.get(key)]
        if missing:
            raise ValueError("Shot " + s["id"] + " is missing: " + ", ".join(missing))
        if not s.get("art") and not s.get("illustration"):
            raise ValueError("Shot " + s["id"] + " needs art or an illustration.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.shotlist.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(data, manifest.parent), encoding="utf-8")
    args.shotlist.write_text(build_shotlist(data), encoding="utf-8")
    print("Storyboard:", args.output)
    print("Shot list: ", args.shotlist)
    print("Frames:    ", len(data["shots"]))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("storyboard build failed:", exc, file=sys.stderr)
        raise SystemExit(2)

