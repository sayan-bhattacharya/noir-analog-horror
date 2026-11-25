#!/usr/bin/env python3
"""Build a local, clickable visual index of NOIR's image assets."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "NOIR_asset_explorer.html"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}


def describe(path: Path) -> tuple[str, str, str]:
    rel = path.relative_to(ROOT).as_posix()
    name = path.stem.replace("_", " ").replace("-", " ")
    folder = path.parent.relative_to(ROOT).as_posix()
    if folder.startswith("output") or folder.startswith("screenshots"):
        kind = "Rendered film frame / preview"
        where = "Existing NOIR render · " + folder
    elif folder.startswith("assets"):
        kind = "Production asset or visual reference"
        where = "Project asset library · " + folder
    elif folder.startswith("plates"):
        kind = "Scene plate used by the compositor"
        where = "Film scene plates · " + folder
    else:
        kind = "Project image"
        where = folder
    return name, kind, where


def main() -> None:
    files = sorted((p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS and "__pycache__" not in p.parts), key=lambda p: p.relative_to(ROOT).as_posix().lower())
    entries = []
    for p in files:
        title, what, where = describe(p)
        entries.append({"src": "../" + p.relative_to(ROOT).as_posix(), "path": p.relative_to(ROOT).as_posix(), "title": title, "what": what, "where": where, "folder": p.parent.relative_to(ROOT).as_posix()})
    data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    page = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NOIR — Image Library</title><style>
:root{color-scheme:dark;--bg:#11120f;--panel:#1a1b17;--line:#37382f;--ink:#eee9dc;--muted:#aaa695;--gold:#d5ba7c;--green:#a4b39d}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 50% -20%,#373326,transparent 55%),var(--bg);color:var(--ink);font:15px/1.5 Inter,Segoe UI,Arial,sans-serif}.shell{width:min(1500px,calc(100% - 40px));margin:auto}header{padding:40px 0 24px;border-bottom:1px solid var(--line)}.eyebrow,.tag,.path,.count{font:10px ui-monospace,Consolas,monospace;text-transform:uppercase;letter-spacing:.1em;color:var(--gold)}h1{font:500 clamp(38px,6vw,68px)/1 Georgia,serif;margin:14px 0}.intro{max-width:850px;color:#c9c3b5}.top{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap}.actions{display:flex;gap:8px;flex-wrap:wrap}input,select,button,.back{background:#20211c;border:1px solid #555346;color:var(--ink);padding:10px 12px;font:inherit}input{min-width:min(320px,80vw)}button,.back{cursor:pointer;text-decoration:none}button.active{background:var(--gold);color:#151510;border-color:var(--gold)}.bar{display:flex;justify-content:space-between;gap:15px;align-items:center;margin:24px 0 14px;color:var(--muted)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;padding-bottom:55px}.asset{background:var(--panel);border:1px solid var(--line);overflow:hidden;min-width:0}.image{display:block;background:#080908;aspect-ratio:16/10;position:relative;cursor:zoom-in}.image img{width:100%;height:100%;object-fit:contain;display:block}.image:hover img{filter:brightness(1.08)}.info{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line)}.column{padding:12px 14px;min-width:0}.column+ .column{border-left:1px solid var(--line)}.column h2{margin:0 0 7px;color:var(--gold);font:10px ui-monospace,Consolas,monospace;text-transform:uppercase;letter-spacing:.1em}.column p{margin:0;color:#ded8ca;font-size:12px;overflow-wrap:anywhere}.title{padding:11px 14px 0;font:20px Georgia,serif}.file{display:block;padding:8px 14px 12px;color:var(--green);font:10px ui-monospace,Consolas,monospace;overflow-wrap:anywhere}.empty{display:none;color:var(--muted);padding:60px;text-align:center}.modal{display:none;position:fixed;inset:0;z-index:5;background:#050605f5;align-items:center;justify-content:center;padding:24px;cursor:zoom-out}.modal.open{display:flex}.modal img{max-width:96vw;max-height:85vh;object-fit:contain}.caption{position:fixed;bottom:12px;color:var(--ink);font:11px ui-monospace,Consolas,monospace;text-align:center;max-width:90vw}.hidden{display:none!important}@media(max-width:1000px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){.shell{width:calc(100% - 22px)}.grid{grid-template-columns:1fr}.info{grid-template-columns:1fr}.column+.column{border-left:0;border-top:1px solid var(--line)}.bar{align-items:flex-start;flex-direction:column}}@media print{body{background:#fff;color:#111}.grid{grid-template-columns:repeat(2,1fr)}.asset{break-inside:avoid;background:#fff;color:#111}.column p{color:#222}.actions{display:none}}
</style></head><body><header><div class="shell"><div class="top"><div class="eyebrow">PROJECT NOIR / VISUAL LIBRARY</div><a class="back" href="NOIR_storyboard.html">← Back to storyboard</a></div><h1>Frames &amp; source images</h1><p class="intro">Browse the images available in this project. Render captures and reference assets are labelled by source so it’s clear what was rendered and what is an ingredient. Select any image to enlarge it; click its file path to open the original.</p><div class="actions"><input id="search" type="search" placeholder="Search titles, filenames, folders…" aria-label="Search image assets"><select id="folder"><option value="all">All folders</option></select><button id="all">All images</button><button id="renders">Render captures</button><button onclick="window.print()">Print</button></div></div></header><main class="shell"><div class="bar"><span id="count"></span><span>Each card has the two requested columns: “What it does” and “Where it appears.”</span></div><section class="grid" id="grid"></section><div class="empty" id="empty">No images match that search.</div></main><div class="modal" id="modal"><img alt="Expanded project image"><div class="caption"></div></div><script id="data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.querySelector('#data').textContent),grid=document.querySelector('#grid'),folder=document.querySelector('#folder'),search=document.querySelector('#search');
for(const f of [...new Set(data.map(x=>x.folder))]){const o=document.createElement('option');o.value=f;o.textContent=f;folder.append(o)}
for(const a of data){const card=document.createElement('article');card.className='asset';card.dataset.path=a.path.toLowerCase();card.dataset.folder=a.folder;card.dataset.render=/^(output|screenshots)\//.test(a.path);card.innerHTML=`<div class="title">${esc(a.title)}</div><a class="image" href="${esc(a.src)}" aria-label="Open full image: ${esc(a.title)}"><img loading="lazy" src="${esc(a.src)}" alt="${esc(a.title)}"></a><div class="info"><section class="column"><h2>What it does</h2><p>${esc(a.what)}</p></section><section class="column"><h2>Where it appears</h2><p>${esc(a.where)}</p></section></div><a class="file" href="${esc(a.src)}" target="_blank">${esc(a.path)}</a>`;grid.append(card)}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function filter(){let n=0;for(const c of grid.children){const ok=(folder.value==='all'||c.dataset.folder===folder.value)&&c.dataset.path.includes(search.value.toLowerCase())&&(!document.querySelector('#renders').classList.contains('active')||c.dataset.render==='true');c.classList.toggle('hidden',!ok);if(ok)n++}document.querySelector('#count').textContent=`${n} of ${data.length} images`;document.querySelector('#empty').style.display=n?'none':'block'}folder.onchange=filter;search.oninput=filter;document.querySelector('#all').onclick=()=>{document.querySelector('#renders').classList.remove('active');filter()};document.querySelector('#renders').onclick=e=>{e.currentTarget.classList.toggle('active');filter()};
const modal=document.querySelector('#modal'),big=modal.querySelector('img'),caption=modal.querySelector('.caption');grid.addEventListener('click',e=>{const a=e.target.closest('.image');if(!a)return;e.preventDefault();big.src=a.querySelector('img').src;caption.textContent=a.closest('.asset').querySelector('.file').textContent;modal.classList.add('open')});modal.onclick=()=>modal.classList.remove('open');document.onkeydown=e=>{if(e.key==='Escape')modal.classList.remove('open')};filter();
</script></body></html>'''.replace("__DATA__", data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUT} with {len(entries)} images")


if __name__ == "__main__":
    main()
