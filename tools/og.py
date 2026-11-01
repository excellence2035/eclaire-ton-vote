#!/usr/bin/env python3
"""Image de partage et icônes : og.png (1200 × 630) et icons/*.png.

    python3 tools/og.py [--keep-html DIR]

Compose une page HTML aux couleurs du site (violet d'encre électorale, coche ambrée, polices de fonts/, carte de l'Afrique tirée de
src/mapdata.js : les pays où une élection nationale est prévue d'ici fin 2027 sont en ambre), la photographie avec Playwright (Chromium) et
écrit :
    og.png                       1200 × 630, aperçu des liens (Open Graph, Twitter)
    icons/icon-192.png           icônes du manifeste (coins arrondis, fond transparent)
    icons/icon-512.png
    icons/icon-maskable-512.png  pleine page, coche dans la zone sûre (icône « maskable »)
    icons/apple-touch-icon.png   180 × 180, pleine page
Le nom du site vient de BRAND (tools/build.js). Nécessite Node (pour lire les données de la carte), Python 3 et Playwright ; Pillow (facultatif) ramène og.png à environ 80 Ko.
Les fichiers produits sont versionnés ; tools/build.js les recopie dans le dossier de sortie quand --out change de dossier.
"""
import argparse, json, os, re, subprocess, sys, tempfile

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AP = argparse.ArgumentParser()
AP.add_argument("--keep-html", default="", help="dossier où garder les pages HTML intermédiaires (pour les regarder)")
ARGS = AP.parse_args()

PURPLE, PURPLE_DARK, AMBER, PAPER = "#5A2DB8", "#37186F", "#F2B42C", "#F3F1F8"


def brand():
    src = open(os.path.join(ROOT, "tools", "build.js"), encoding="utf8").read()
    m = re.search(r'const BRAND = "([^"]+)"', src)
    if not m:
        sys.exit("BRAND not found in tools/build.js")
    return m.group(1)


def map_data():
    """Tracés de la carte (src/mapdata.js) et pays « élection d'ici fin 2027 » (src/africa.js), lus par Node."""
    js = (
        "const vm=require('vm'),fs=require('fs');const c={};vm.createContext(c);"
        "vm.runInContext(fs.readFileSync('src/africa.js','utf8')+fs.readFileSync('src/mapdata.js','utf8')+';this.o={MAP,AFRICA}',c);"
        "const M=c.o.MAP,A=c.o.AFRICA;"
        "console.log(JSON.stringify({vb:M.vb,nb:M.nb,c:M.c,isl:M.isl,up:Object.keys(A).filter(k=>A[k].up)}))"
    )
    r = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def fonts_css():
    fonts = os.path.join(ROOT, "fonts")
    def face(fam, file, weight, stretch=None):
        st = f"font-stretch:{stretch};" if stretch else ""
        return f'@font-face{{font-family:"{fam}";font-weight:{weight};{st}src:url("file://{fonts}/{file}") format("woff2");}}'
    return (face("Bricolage Grotesque", "bricolage-grotesque-latin.woff2", "200 800", "75% 100%")
            + face("Readex Pro", "readex-pro-latin.woff2", "160 700"))


CHECK = ('<svg viewBox="0 0 32 32" width="100%" height="100%"><path d="M8 17l6 6L27 7" fill="none" stroke="' + AMBER
         + '" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def og_html(name, M):
    land, up = [], set(M["up"])
    for cid, d in M["c"].items():
        if cid == "732":
            continue
        land.append(f'<path d="{d}" class="{"up" if cid in up else "no"}"/>')
    for cid, (x, y) in M["isl"].items():
        if cid not in M["c"]:
            land.append(f'<circle cx="{x}" cy="{y}" r="7" class="{"up" if cid in up else "no"}"/>')
    vb = " ".join(str(v) for v in M["vb"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{fonts_css()}
*{{box-sizing:border-box;margin:0}}
html,body{{width:1200px;height:630px;overflow:hidden}}
body{{position:relative;background:linear-gradient(135deg,{PURPLE} 0%,{PURPLE_DARK} 100%);color:#fff;font-family:"Readex Pro",sans-serif}}
.map{{position:absolute;right:-6px;top:12px;width:620px;height:606px}}
.map svg{{width:100%;height:100%}}
.map .nb{{fill:rgba(255,255,255,.07)}}
.map .no{{fill:rgba(255,255,255,.2);stroke:{PURPLE_DARK};stroke-width:1}}
.map .up{{fill:{AMBER};stroke:{PURPLE_DARK};stroke-width:1.2}}
.left{{position:absolute;left:64px;top:52px;width:610px;height:526px;display:flex;flex-direction:column}}
.brand{{display:flex;align-items:center;gap:22px}}
.mark{{width:84px;height:84px;border-radius:24px;background:#fff1;border:3px solid rgba(255,255,255,.35);padding:12px 10px 0 12px}}
.mark svg{{overflow:visible;transform:translate(2px,-6px)}}
.name{{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:100px;line-height:1;letter-spacing:-.03em;font-stretch:85%}}
h1{{margin-top:30px;font-family:"Bricolage Grotesque",sans-serif;font-weight:750;font-size:56px;line-height:1.05;letter-spacing:-.02em;font-stretch:90%}}
h1 em{{font-style:normal;color:{AMBER}}}
p{{margin-top:18px;font-size:25px;line-height:1.35;font-weight:400;color:#EDE6FB;max-width:560px}}
.chips{{margin-top:auto;display:flex;gap:12px;flex-wrap:wrap}}
.chip{{font-size:21px;font-weight:600;padding:7px 16px;border-radius:999px;background:rgba(255,255,255,.14);color:#fff;letter-spacing:.01em}}
.legend{{position:absolute;right:40px;bottom:30px;display:flex;align-items:center;gap:12px;font-size:21px;font-weight:500;color:#fff;background:rgba(24,12,56,.55);padding:8px 16px;border-radius:12px}}
.legend i{{width:20px;height:20px;border-radius:5px;background:{AMBER};display:inline-block}}
</style></head><body>
<div class="map"><svg viewBox="{vb}" aria-hidden="true"><path class="nb" d="{M['nb']}"/>{''.join(land)}</svg></div>
<div class="left">
  <div class="brand"><div class="mark">{CHECK}</div><div class="name">{name}</div></div>
  <h1>Elections in Africa:<br><em>which party thinks<br>like you?</em></h1>
  <p>Answer precise questions, issue by issue, and compare with each party’s documented positions.</p>
  <div class="chips"><span class="chip">54 countries</span><span class="chip">5 languages</span><span class="chip">Anonymous</span></div>
</div>
<div class="legend"><i></i>Elections by end of 2027</div>
</body></html>"""


def icon_html(size, rounded, mark_scale):
    r = f"{size * 0.22:.0f}px" if rounded else "0"
    m = size * mark_scale
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;box-sizing:border-box}}html,body{{width:{size}px;height:{size}px;background:transparent;overflow:hidden}}
.i{{width:{size}px;height:{size}px;border-radius:{r};background:{PURPLE};display:grid;place-items:center}}
.m{{width:{m:.0f}px;height:{m:.0f}px}}
</style></head><body><div class="i"><div class="m">{CHECK}</div></div></body></html>"""


def shrink(path):
    """og.png en 256 couleurs : une image de 400 Ko est refusée par certains aperçus de liens (WhatsApp : environ 300 Ko) ; Pillow, s'il est là."""
    try:
        from PIL import Image
    except ImportError:
        print("Pillow not installed: og.png left as a 24-bit PNG (about 400 Ko)")
        return
    Image.open(path).convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(path, optimize=True)


def main():
    name = brand()
    M = map_data()
    tmp = ARGS.keep_html or tempfile.mkdtemp(prefix="etv-og-")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "icons"), exist_ok=True)

    def render(html, out, w, h, transparent=False):
        f = os.path.join(tmp, os.path.basename(out) + ".html")
        open(f, "w", encoding="utf8").write(html)
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        page.goto("file://" + f)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        page.screenshot(path=out, omit_background=transparent)
        page.close()
        if os.path.basename(out) == "og.png":
            shrink(out)
        print(f"{os.path.relpath(out, ROOT):34} {os.path.getsize(out) / 1024:6.1f} Ko  {w}x{h}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        render(og_html(name, M), os.path.join(ROOT, "og.png"), 1200, 630)
        render(icon_html(192, True, 0.74), os.path.join(ROOT, "icons", "icon-192.png"), 192, 192, True)
        render(icon_html(512, True, 0.74), os.path.join(ROOT, "icons", "icon-512.png"), 512, 512, True)
        render(icon_html(512, False, 0.5), os.path.join(ROOT, "icons", "icon-maskable-512.png"), 512, 512)
        render(icon_html(180, False, 0.62), os.path.join(ROOT, "icons", "apple-touch-icon.png"), 180, 180)
        browser.close()


if __name__ == "__main__":
    main()
