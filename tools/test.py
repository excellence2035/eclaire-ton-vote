#!/usr/bin/env python3
"""Éclaire ton vote : tests de bout en bout (Python + Playwright, Chromium).

    python3 tools/test.py [--shots DIR] [--only NAME[,NAME…]] [--headed]

Teste le site tel qu'il est construit à la racine du dépôt (lancer d'abord `node tools/build.js`),
puis construit dans un dossier temporaire un second site avec des éditions de test jetables
(`node tools/build.js --extra <fixtures> --out <tmp>/site`) : page d'information, édition « leader »,
traductions incomplètes et éditions cassées. Rien n'est écrit dans src/.
Le dépôt est servi avec `python3 -m http.server` sur un port libre. Aucune requête externe n'est
autorisée, sauf Google Fonts (remplacé par une feuille vide pendant les tests).
"""
import argparse, json, math, os, re, shutil, socket, subprocess, sys, tempfile, time, traceback, urllib.request

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AP = argparse.ArgumentParser()
AP.add_argument("--shots", default=os.path.join(tempfile.gettempdir(), "etv-shots"), help="dossier des captures d'écran")
AP.add_argument("--only", default="", help="noms de tests séparés par des virgules")
AP.add_argument("--headed", action="store_true")
ARGS = AP.parse_args()
os.makedirs(ARGS.shots, exist_ok=True)

LANGS = ["en", "fr", "pt", "sw", "ar"]
STR_KEYS = ["tabs", "partial", "presCand", "partyLeader", "partyBasisLeader", "mCodingLead", "mTransl", "legReady", "legInfo",
            "langNoQ", "langNoInfo", "retry", "infoWhy", "infoActors", "proto", "seeResults", "tryNigeria", "mapHint"]


# ------------------------------------------------------------------ petite infrastructure
class Check:
    def __init__(self):
        self.n = 0

    def __call__(self, cond, msg):
        if not cond:
            raise AssertionError(msg)
        self.n += 1


RESULTS, TESTS = [], []


def test(fn):
    TESTS.append(fn)
    return fn


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def serve(directory):
    port = free_port()
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", directory],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            urllib.request.urlopen(base + "/", timeout=0.5)
            break
        except Exception:
            time.sleep(0.05)
    return proc, base


class Session:
    """Un contexte navigateur : capture des erreurs JS et blocage des requêtes externes."""

    def __init__(self, browser, width=1280, height=900, scheme="light", motion="reduce"):
        # Mouvement réduit par défaut : Playwright n'attend pas la fin de l'animation d'entrée à chaque clic
        self.ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme, locale="en-GB", reduced_motion=motion)
        self.errors, self.console, self.external = [], [], []

        def outside(route):
            url = route.request.url
            if re.match(r"https://fonts\.(googleapis|gstatic)\.com/", url):
                route.fulfill(status=200, content_type="text/css", body="")
            else:
                self.external.append(url)
                route.abort()

        self.ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1[:/])"), outside)
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("console", lambda m: m.type == "error" and self.console.append(m.text))

    def close(self, c, allow_console=False):
        try:
            c(not self.errors, f"page errors: {self.errors[:3]}")
            c(allow_console or not self.console, f"console errors: {self.console[:3]}")
            c(not self.external, f"external requests: {self.external[:3]}")
        finally:
            self.ctx.close()


def no_overflow(page, c, where):
    sw, iw = page.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
    c(sw <= iw + 1, f"{where}: horizontal overflow ({sw} > {iw})")


def strings(page, lang):
    return page.evaluate("([l, ks]) => Object.fromEntries(ks.map(k => [k, T[l][k]]))", [lang, STR_KEYS])


def wait_view(page, view, timeout=8000):
    page.wait_for_function("v => state.view === v", arg=view, timeout=timeout)


def rgb(hexcol):
    h = hexcol.lstrip("#")
    return "rgb(%d, %d, %d)" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def shot(page, name, full=False):
    page.screenshot(path=os.path.join(ARGS.shots, name), full_page=full)


def open_country(page, a3, lang):
    page.click(f'#mapWrap [data-place="{a3}"]')
    page.wait_for_selector("#langDlg[open]")
    page.click(f'#langBody [data-pick="{lang}"]')


# ------------------------------------------------------------------ calcul attendu (copie du modèle de l'application)
def js_round(x):
    return math.floor(x + 0.5)


def expected_ranking(D, answers, double, prios):
    rows = []
    for p in D["ed"]["parties"]:
        num = den = k = 0
        for qi, q in enumerate(D["ed"]["questions"]):
            v = answers.get(qi)
            c = q["cells"].get(p["id"])
            if not isinstance(v, int) or not c:
                continue
            w = (2 if double.get(qi) else 1) * (2 if q["theme"] in prios else 1)
            num += w * (1 - abs(v - c["p"]) / 4)
            den += w
            k += 1
        s = (num + 3 * 0.5) / (den + 3) if k else None
        rows.append((p["sigle"], s, k >= 2))
    rows.sort(key=lambda r: (0 if r[2] else 1, -(r[1] if r[1] is not None else -1)))
    return [(sig, js_round(s * 100) if ok else None) for sig, s, ok in rows]


def answer_all(page, plan, stop_after_prio=False):
    """Répond à tout le questionnaire. plan(qi) -> (valeur ou None pour passer, double?)."""
    answers, double = {}, {}
    while True:
        view = page.evaluate("state.view")
        if view == "checkpoint":
            if stop_after_prio:
                page.click('[data-go="results"]')
                wait_view(page, "results")
                break
            page.click('[data-go="more"]')
            wait_view(page, "question")
            continue
        if view == "results":
            break
        qi, i = page.evaluate("[state.order[state.i], state.i]")
        v, dbl = plan(qi)
        if dbl:
            page.check("#qDouble")
            double[qi] = True
        if v is None:
            page.click('[data-val="skip"]')
        else:
            page.click(f'.answers .ans[data-val="{v}"]')
        answers[qi] = v
        page.wait_for_function("i => state.view !== 'question' || state.i !== i", arg=i, timeout=5000)
    return answers, double


def displayed_ranking(page):
    return page.evaluate("""() => [...document.querySelectorAll('#pan0 .rank li')].map(li => {
        const pct = li.querySelector('.pct').textContent.replace(/[^0-9]/g, '');
        return [li.querySelector('.badge').textContent, li.classList.contains('out') ? null : Number(pct)];
    })""")


def check_results_page(page, c, D, lang, L, answers, double, prios, where):
    """Les 4 onglets, le clavier, le classement attendu, la fiche parti, la note de traduction."""
    nq = len(D["ed"]["questions"])
    c(page.locator('[role="tab"]').count() == 4, f"{where}: 4 tabs")
    c(page.inner_text("#tab0").strip() == L["tabs"][0], f"{where}: tab label in {lang}")
    exp = expected_ranking(D, answers, double, prios)
    got = [tuple(r) for r in displayed_ranking(page)]
    c(got == exp, f"{where}: ranking {got} != expected {exp}")
    # Onglets à la souris
    for k in range(4):
        page.click(f"#tab{k}")
        c(page.is_visible(f"#pan{k}") and all(not page.is_visible(f"#pan{j}") for j in range(4) if j != k), f"{where}: tab {k} panel")
    c(page.locator("#pan1 .theme-card").count() == len(D["ed"]["themes"]), f"{where}: one card per theme")
    c(page.locator("#pan2 .qa").count() == nq, f"{where}: one entry per question")
    if double:
        c(page.locator('#pan2 .chip.grey:text-is("×2")').count() == len(double), f"{where}: counts-double chips")
    has_tr = page.locator("#pan3 .method li.transl").count() == 1
    c(has_tr == (lang != D["lang"]), f"{where}: translation note shown iff UI language ≠ base ({lang} vs {D['lang']})")
    c(page.locator("#pan3 .src-list li").count() >= min(5, len(D["src"])), f"{where}: sources listed")
    # Clavier : flèches dans la liste d'onglets (sens visuel inversé en RTL non requis : comportement d'origine conservé)
    page.click("#tab0")
    page.focus("#tab0")
    page.keyboard.press("ArrowRight")
    c(page.get_attribute("#tab1", "aria-selected") == "true", f"{where}: ArrowRight selects next tab")
    page.keyboard.press("ArrowLeft")
    page.keyboard.press("ArrowLeft")
    c(page.get_attribute("#tab3", "aria-selected") == "true", f"{where}: ArrowLeft wraps")
    page.click("#tab0")
    # Couverture partielle (au moins un parti peu documenté dans le pilote)
    if D["id"] == "ng":
        c(page.locator(f'#pan0 .chip.warn:text-is("{L["partial"]}")').count() >= 1, f"{where}: partial-coverage chip")
    # Fiche parti
    page.locator("#pan0 [data-fiche]").first.click()
    page.wait_for_selector("#fiche[open]")
    c(page.inner_text("#ficheTitle").strip() != "", f"{where}: fiche title")
    c(page.locator("#fiche .pos-table li").count() == nq, f"{where}: fiche positions")
    c(page.evaluate("document.activeElement && document.activeElement.id") == "ficheClose", f"{where}: focus on close")
    page.click("#ficheClose")
    c(not page.is_visible("#fiche"), f"{where}: fiche closes")


def run_nigeria(browser, base, lang, width, c, switch_to=None, screenshot=None):
    S = Session(browser, width=width, motion="no-preference" if lang == "en" else "reduce")
    page = S.page
    page.goto(base + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    D = json.loads(open(os.path.join(ROOT, "data", "ng.json"), encoding="utf8").read())
    L = strings(page, lang)
    open_country(page, "566", lang)
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("document.documentElement.lang") == lang, f"ng-{lang}: html lang")
    c(page.evaluate("document.documentElement.dir") == ("rtl" if lang == "ar" else "ltr"), f"ng-{lang}: dir")
    c(page.locator("#langs button:not([disabled])").count() == 5, f"ng-{lang}: 5 languages offered")
    # Couleur du badge (thème clair) injectée depuis l'édition
    apc = next(p for p in D["ed"]["parties"] if p["id"] == "apc")
    page.click(".about details:nth-of-type(2) summary")
    bg = page.evaluate("getComputedStyle(document.querySelector('.party-list .badge')).backgroundColor")
    c(bg == rgb(apc["col"][0]), f"ng-{lang}: APC badge colour {bg}")
    c(page.inner_text(".party-list .pb-sub").startswith(L["presCand"]), f"ng-{lang}: presidential candidate label")
    no_overflow(page, c, f"ng-{lang} start")
    # Priorités : 2 sujets, dont un retiré puis remis
    themes = [t["id"] for t in D["ed"]["themes"]]
    prios = [themes[2], themes[0]]
    for th in prios:
        page.click(f'[data-prio="{th}"]')
    page.click(f'[data-prio="{themes[2]}"]')
    page.click(f'[data-prio="{themes[2]}"]')
    prios = [themes[0], themes[2]]
    c(page.get_attribute(f'[data-prio="{themes[0]}"]', "aria-pressed") == "true", f"ng-{lang}: priority pressed")
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    first_theme = page.evaluate("ed().questions[state.order[0]].theme")
    c(first_theme == themes[0], f"ng-{lang}: priority questions first")
    no_overflow(page, c, f"ng-{lang} question")

    def plan(qi):
        return (None if qi % 7 == 3 else [2, 1, 0, -1, -2][qi % 5]), qi % 11 == 5

    answers, double = answer_all(page, plan)
    answers = {k: v for k, v in answers.items() if v is not None}
    c(page.evaluate("Object.keys(state.answers).length") == len(D["ed"]["questions"]), f"ng-{lang}: every question seen")
    check_results_page(page, c, D, lang, L, answers, double, prios, f"ng-{lang}")
    no_overflow(page, c, f"ng-{lang} results")
    if screenshot:
        shot(page, screenshot, full=True)
    if switch_to:
        before = displayed_ranking(page)
        page.click(f'#langs [data-lang="{switch_to}"]')
        L2 = strings(page, switch_to)
        c(page.evaluate("document.documentElement.lang") == switch_to, f"ng-{lang}→{switch_to}: html lang")
        c(page.evaluate("state.view") == "results", f"ng-{lang}→{switch_to}: still on results")
        c(page.inner_text("#tab0").strip() == L2["tabs"][0], f"ng-{lang}→{switch_to}: tabs relabelled")
        c(displayed_ranking(page) == before, f"ng-{lang}→{switch_to}: same ranking after switch")
        c((page.locator("#pan3 .method li.transl").count() == 1) == (switch_to != "en"), f"ng-{lang}→{switch_to}: translation note")
        q0 = page.evaluate("ed().questions[0].text")
        base_q0 = D["ed"]["questions"][0]["text"]
        c((q0 == base_q0) == (switch_to == "en"), f"ng-{lang}→{switch_to}: questions translated")
    S.close(c)


# ------------------------------------------------------------------ éditions de test jetables
def fixture_ed(cc, n_parties=3, leader=True):
    S = {f"{cc}1": {"o": "Fixture Gazette", "t": "Test source one", "d": "1 Oct 2026", "u": "https://example.org/fixture/one"},
         f"{cc}2": {"o": "Fixture Times", "t": "Test source two", "d": "2 Oct 2026", "u": "https://example.org/fixture/two"},
         f"{cc}3": {"o": "Fixture Radio", "t": "Test source three", "d": "3 Oct 2026", "u": "https://example.org/fixture/three"}}
    M = {"ev": [{"t": "legislative", "d": "2027-07", "q": "month"}], "src": f"{cc}1"}
    cols = [["#7A2E2E", "#F0A0A0"], ["#2E5A7A", "#A0C8F0"], ["#3F6B2A", "#B4E09A"]]
    parties = []
    for k, (sig, name) in enumerate([("ALP", "Fixture Party Alpha"), ("BET", "Fixture Party Beta"), ("GAM", "Fixture Party Gamma")][:n_parties]):
        p = {"id": f"{cc}_{sig.lower()}", "sigle": sig, "nom": name, "cand": f"Leader {sig}", "tag": "Governing party" if k == 0 else "Opposition",
             "col": cols[k], "commit": [[f"{sig} commitment {j}", f"{cc}{j}"] for j in (1, 2, 3)]}
        if k == 1:
            p["candNote"] = "Candidate not yet designated"
        parties.append(p)
    theme_ids = ["econ", "security", "gov", "integrity", "edu", "health", "social", "agri"]
    themes = [{"id": t, "name": f"Theme {t}", "min": f"Ministry of {t}"} for t in theme_ids]
    questions = []
    for i in range(32):
        cells = {p["id"]: {"p": [2, 1, 0, -1, -2][(i + k * 2) % 5], "k": "stated", "s": f"{cc}{1 + (i % 3)}", "n": f"Note {i} for {p['sigle']}."}
                 for k, p in enumerate(parties) if not (k == 2 and i % 4 == 0)}
        q = {"theme": theme_ids[i // 4], "short": f"Short {i}", "text": f"Statement number {i} for the fixture.", "ctx": f"Context {i}.", "cells": cells}
        if len(parties) > 2 and i % 4 == 0:
            q["nd"] = {parties[2]["id"]: f"No position on {i}."}
        questions.append(q)
    E = {"id": cc, "name": "Fixture country", "lang": "en", "role": "leader" if leader else "pres",
         "strip": "Legislative elections 2027", "stripDate": "July 2027 (date not set)",
         "facts": [["Vote", "July 2027"], ["Seats", "151"], ["Parties compared", str(n_parties)]], "factsSrc": [f"{cc}1"],
         "system": [["Political system", "Text one."], ["How parliament is elected", "Text two."], ["Who can vote", "Text three."], ["Rules", "Text four."]],
         "systemSrc": [f"{cc}2"], "status": "Fixture status line.", "others": ["XYZ · Someone", "and 3 other parties"], "othersSrc": f"{cc}3",
         "parties": parties, "themes": themes, "questions": questions}
    return S, M, E


def fixture_ed_i18n(E, lang, drop_q=False, drop_cand=False):
    L = {"strip": f"[{lang}] {E['strip']}", "stripDate": f"[{lang}] {E['stripDate']}", "status": f"[{lang}] status",
         "facts": [[f"[{lang}] {a}", b] for a, b in E["facts"]], "system": [[f"[{lang}] {a}", b] for a, b in E["system"]],
         "others": [f"[{lang}] {o}" for o in E["others"]],
         "tags": {p["id"]: f"[{lang}] {p['tag']}" for p in E["parties"]},
         "commits": {p["id"]: [f"[{lang}] {cm[0]}" for cm in p["commit"]] for p in E["parties"]},
         "themes": {t["id"]: [f"[{lang}] {t['name']}", f"[{lang}] {t['min']}"] for t in E["themes"]},
         "q": [{"short": f"[{lang}] {q['short']}", "text": f"[{lang}] {q['text']}", "ctx": f"[{lang}] {q['ctx']}",
                "n": {pid: f"[{lang}] {c['n']}" for pid, c in q["cells"].items()},
                **({"nd": {pid: f"[{lang}] {n}" for pid, n in q["nd"].items()}} if q.get("nd") else {})} for q in E["questions"]]}
    cn = {p["id"]: f"[{lang}] {p['candNote']}" for p in E["parties"] if p.get("candNote")}
    if cn and not drop_cand:
        L["candNotes"] = cn
    if drop_q:
        L["q"] = L["q"][:5]
    return L


def fixture_info(cc):
    S = {f"{cc}1": {"o": "Fixture Gazette", "t": "Info source one", "d": "1 Oct 2026", "u": "https://example.org/fixture/i1"},
         f"{cc}2": {"o": "Fixture Times", "t": "Info source two", "d": "2 Oct 2026", "u": "https://example.org/fixture/i2"}}
    M = {"ev": [{"t": "legislative", "d": "2027-01", "q": "month"}], "src": f"{cc}1", "note": "Fixture caveat about the date."}
    I = {"id": cc, "name": "Fixture islands", "lang": "en", "strip": "Legislative elections 2027", "stripDate": "January 2027 (date not set)",
         "facts": [["Vote", "Jan 2027"], ["Seats", "33"], ["Lists filed", "None yet"]], "factsSrc": [f"{cc}1"],
         "system": [["System", "S one."], ["Parliament", "S two."], ["Voters", "S three."], ["Context", "S four."]], "systemSrc": [f"{cc}2"],
         "actors": [["Actor one", "Who they are one.", f"{cc}1"], ["Actor two", "Who they are two.", f"{cc}2"], ["Actor three", "Who they are three.", f"{cc}1"]],
         "why": "Fixture reason why parties cannot be compared yet."}
    return S, M, I


def info_i18n(I, lang, drop_why=False):
    L = {"strip": f"[{lang}] {I['strip']}", "stripDate": f"[{lang}] {I['stripDate']}",
         "facts": [[f"[{lang}] {a}", b] for a, b in I["facts"]], "system": [[f"[{lang}] {a}", f"[{lang}] {b}"] for a, b in I["system"]],
         "actors": [[f"[{lang}] {a[0]}", f"[{lang}] {a[1]}"] for a in I["actors"]], "why": f"[{lang}] {I['why']}"}
    if drop_why:
        del L["why"]
    return L


def write_js(path, **consts):
    with open(path, "w", encoding="utf8") as f:
        f.write("/* Fixture de test, générée par tools/test.py */\n")
        for k, v in consts.items():
            f.write(f"const {k} = {json.dumps(v, ensure_ascii=False, indent=1)};\n")


def make_fixtures(tmp):
    fx = os.path.join(tmp, "fixtures")
    os.makedirs(os.path.join(fx, "editions"))
    os.makedirs(os.path.join(fx, "i18n"))
    # cg : questionnaire « leader » (Congo), fr complet, pt incomplet (questions), sw incomplet (candNotes)
    S, M, E = fixture_ed("cg")
    write_js(os.path.join(fx, "editions", "cg.js"), SRC_CG=S, META_CG=M, ED_CG=E)
    write_js(os.path.join(fx, "i18n", "cg.js"), I18N_CG={"fr": fixture_ed_i18n(E, "fr"), "pt": fixture_ed_i18n(E, "pt", drop_q=True),
                                                         "sw": fixture_ed_i18n(E, "sw", drop_cand=True)})
    # km : page d'information sur un État insulaire (Comores), ar complet, fr incomplet
    S, M, I = fixture_info("km")
    write_js(os.path.join(fx, "editions", "km.js"), SRC_KM=S, META_KM=M, INFO_KM=I)
    write_js(os.path.join(fx, "i18n", "km.js"), I18N_KM={"ar": info_i18n(I, "ar"), "fr": info_i18n(I, "fr", drop_why=True)})
    # bi : questionnaire invalide (2 partis) ; td : fichier qui ne se charge pas
    S, M, E = fixture_ed("bi", n_parties=2)
    write_js(os.path.join(fx, "editions", "bi.js"), SRC_BI=S, META_BI=M, ED_BI=E)
    with open(os.path.join(fx, "editions", "td.js"), "w", encoding="utf8") as f:
        f.write("const SRC_TD = { half: 'written' \n")
    return fx


# ------------------------------------------------------------------ tests
CTX = {}


@test
def build_outputs(c):
    """Le site du dépôt : page complète, page d'artefact, données non intégrées."""
    idx = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
    art = open(os.path.join(ROOT, "artifact.html"), encoding="utf8").read()
    c(idx.startswith("<!doctype html>\n<html lang=\"fr\">"), "index.html starts with doctype + html lang")
    c('<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">' in idx, "viewport meta")
    c('<meta charset="utf-8">' in idx and 'property="og:title"' in idx and 'rel="icon" href="data:image/svg+xml' in idx, "charset, og, favicon")
    c("[hidden]{display:none!important}" in idx and "env(safe-area-inset-top" in idx, "reset + safe areas")
    c(idx.rstrip().endswith("</html>") and "</head>\n<body>" in idx, "document closed")
    c(art.startswith("<title>"), "artifact.html starts with <title>")
    c(not re.search(r"<!doctype|<html[\s>]|<head[\s>]|<body[\s>]", art, re.I), "artifact.html has no wrapper")
    c("[hidden]{display:none!important}" in art, "artifact keeps the reset")
    for marker in ("const SRC_NG", "const ED_NG", "Allied Peoples Movement", "I18N_NG", "Rassemblement national"):
        c(marker not in idx, f"edition data not inlined ({marker})")
    c(len(idx.encode()) < 300_000, f"index.html small ({len(idx.encode())} bytes)")
    for v in ("--c-apc", "--c-lepen"):
        c(v not in idx, f"old colour token {v} removed")
    cat = json.loads(re.search(r"const CATALOG = (\{.*?\});\n", idx).group(1))
    c("ng" in cat and cat["ng"]["kind"] == "ed" and cat["ng"]["a3"] == "566", "catalog: Nigeria")
    c(cat["ng"]["langs"][0] == "en" and set(cat["ng"]["langs"]) == set(LANGS), "catalog: Nigeria in 5 languages")
    c("fr" in cat and cat["fr"]["langs"] == ["fr"] and cat["fr"]["a3"] is None, "catalog: France")
    for cc, e in cat.items():
        c(os.path.exists(os.path.join(ROOT, "data", cc + ".json")), f"data/{cc}.json exists")
        c(e["evSrc"] and e["evSrc"]["u"].startswith("http"), f"catalog {cc}: date source")
        D = json.load(open(os.path.join(ROOT, "data", cc + ".json"), encoding="utf8"))
        c(D["kind"] == e["kind"] and D["id"] == cc and D["langs"] == e["langs"] and set(D["i18n"]) == set(e["langs"][1:]), f"data/{cc}.json matches catalog")
    CTX["catalog"] = cat


@test
def build_fixtures(c):
    """Construction avec éditions de test : langues et éditions invalides écartées, sorties dans un dossier temporaire."""
    tmp = tempfile.mkdtemp(prefix="etv-test-")
    CTX["tmp"] = tmp
    fx = make_fixtures(tmp)
    site = os.path.join(tmp, "site")
    os.makedirs(site)
    before = sorted(os.listdir(os.path.join(ROOT, "src", "editions")))
    r = subprocess.run(["node", os.path.join(ROOT, "tools", "build.js"), "--extra", fx, "--out", site], capture_output=True, text=True, timeout=180)
    out = r.stdout + r.stderr
    CTX["fixture_build_log"] = out
    c(r.returncode == 0, f"build exit code {r.returncode}: {out[-500:]}")
    c(sorted(os.listdir(os.path.join(ROOT, "src", "editions"))) == before, "src/editions untouched")
    c(re.search(r"ok\s+cg: questionnaire, 3 parties, 32 questions, langs en,fr\b", out), "cg built with en,fr")
    c(re.search(r"cg: translation “pt” incomplete, dropped", out), "cg: pt dropped (questions)")
    c(re.search(r"cg: translation “sw” incomplete, dropped .*candNotes", out), "cg: sw dropped (candNotes)")
    c(re.search(r"ok\s+km: information page, 3 actors, langs en,ar\b", out), "km built with en,ar")
    c(re.search(r"km: translation “fr” incomplete, dropped .*why", out), "km: fr dropped (why)")
    c(re.search(r"bi: validation failed, skipped", out), "bi skipped (validation)")
    c(re.search(r"td: cannot load", out), "td skipped (load error)")
    files = sorted(os.listdir(os.path.join(site, "data")))
    c("cg.json" in files and "km.json" in files and "ng.json" in files, f"fixture data written: {files}")
    c("bi.json" not in files and "td.json" not in files, "invalid editions not written")
    cg = json.load(open(os.path.join(site, "data", "cg.json"), encoding="utf8"))
    c(cg["a3"] == "178" and cg["langs"] == ["en", "fr"] and list(cg["i18n"]) == ["fr"], "cg.json langs and i18n")
    c(not os.path.exists(os.path.join(ROOT, "data", "cg.json")), "repo data/ untouched")
    CTX["site"] = site


@test
def map_400(c):
    """La carte à 400 px : pas d'erreur, pas de défilement horizontal, repères et légende tirés du catalogue."""
    S = Session(CTX["browser"], width=400, height=860)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    no_overflow(page, c, "map")
    cat = CTX["catalog"]
    info = page.evaluate("""() => {
      const inA = Object.values(CATALOG).filter(c => c.a3 && AFRICA[c.a3]);
      return { ed: inA.filter(c => c.kind === 'ed').length, info: inA.filter(c => c.kind === 'info').length,
               pins: document.querySelectorAll('#mapWrap .pin').length, marks: document.querySelectorAll('#mapWrap .pin-info').length,
               up: Object.keys(AFRICA).filter(isUp).length,
               cnt: [...document.querySelectorAll('.legend .cnt')].map(e => +e.textContent),
               ngPin: [...document.querySelectorAll('#mapWrap .pin')].map(p => [+p.getAttribute('cx'), +p.getAttribute('cy')]),
               cent: MAP.cent['566'] }
    }""")
    n_ed = sum(1 for e in cat.values() if e["kind"] == "ed" and e["a3"])
    n_info = sum(1 for e in cat.values() if e["kind"] == "info" and e["a3"])
    c(info["pins"] == n_ed == info["ed"], f"check pins {info['pins']} = {n_ed}")
    c(info["marks"] == n_info == info["info"], f"info markers {info['marks']} = {n_info}")
    c(info["cnt"] == [info["up"], 54 - info["up"], n_ed, n_info, 1], f"legend counts {info['cnt']}")
    c(info["cent"] in info["ngPin"], "Nigeria pin at its centroid")
    c(page.locator(".legend .leg-info svg").count() == 1, "legend row for information pages")
    shot(page, "map-400.png", full=True)
    # Clavier : Entrée sur un pays ouvre le choix de langue ; infobulle au focus
    page.focus('#mapWrap path[data-place="566"]')
    c(page.is_visible("#tip") and "✓" in page.inner_text("#tip"), "tooltip on focus shows questionnaire mark")
    page.keyboard.press("Enter")
    page.wait_for_selector("#langDlg[open]")
    c(page.locator("#langBody .lang-btn:not([disabled])").count() == 5, "Nigeria: 5 languages enabled")
    no_overflow(page, c, "language dialog")
    page.click("#langCancel")
    # Pays sans données : comportement d'origine, puis « Essayer avec le Nigeria »
    page.click("#listBox summary")
    page.fill("#csearch", "Angola")
    c(page.locator("#clist .cbtn").count() == 1, "country search")
    page.click('#clist [data-place="024"]')
    page.wait_for_selector("#langDlg[open]")
    c(page.locator("#langBody .lang-btn[disabled]").count() == 0, "no-data country: every language enabled")
    page.click('#langBody [data-pick="pt"]')
    wait_view(page, "info")
    c("Angola" in page.inner_text(".strip"), "no-data info screen")
    no_overflow(page, c, "no-data screen")
    page.click('[data-go="nigeria"]')
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("[state.country, state.ui]") == ["ng", "pt"], "Try it with Nigeria (keeps Portuguese)")
    S.close(c)


def make_ng_test(lang, width, switch_to, screenshot):
    def t(c):
        run_nigeria(CTX["browser"], CTX["base"], lang, width, c, switch_to=switch_to, screenshot=screenshot)
    t.__name__ = f"nigeria_{lang}"
    t.__doc__ = f"Nigeria en {lang} : priorités → toutes les questions → résultats, onglets, fiche, changement de langue → {switch_to}."
    return t


for _lang, _w, _sw, _shot in [("en", 1280, "fr", "ng-en-results.png"), ("fr", 400, "pt", None), ("pt", 1024, "sw", None),
                              ("sw", 400, "ar", None), ("ar", 400, "en", "ng-ar-results-400.png")]:
    test(make_ng_test(_lang, _w, _sw, _shot))


@test
def france(c):
    """Prototype France : lien hors Afrique, français seulement, 9 partis."""
    S = Session(CTX["browser"], width=1100)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    page.click('#langs [data-lang="en"]')
    page.click('[data-go="france"]')
    page.wait_for_selector(".theme-grid")
    D = json.load(open(os.path.join(ROOT, "data", "fr.json"), encoding="utf8"))
    c(page.evaluate("[state.country, state.ui]") == ["fr", "fr"], "France opens in French")
    c(page.inner_text(".strip b").startswith("France · "), "strip uses the edition name")
    c([b.strip() for b in page.locator("#langs button:not([disabled])").all_inner_texts()] == ["FR"], "only French enabled")
    lepen = next(p for p in D["ed"]["parties"] if p["id"] == "lepen")
    c(page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--c-fr-lepen').trim().toLowerCase()") == lepen["col"][0].lower(), "France colour token injected")
    th = D["ed"]["themes"][0]["id"]
    page.click(f'[data-prio="{th}"]')
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    answers, double = answer_all(page, lambda qi: ([2, -1, 1, -2, 0][qi % 5], False), stop_after_prio=True)
    L = strings(page, "fr")
    check_results_page(page, c, D, "fr", L, answers, double, [th], "france")
    c(page.locator("#pan0 .rank li").count() == 9, "9 parties ranked")
    c(page.locator('#pan0 .chip.grey:text-is("Primaire en cours")').count() == 2, "primary chips")
    shot(page, "fr-results.png")
    page.click('[data-go="home"]')
    wait_view(page, "map")
    S.close(c)


@test
def dark(c):
    """Thème sombre : couleurs de partis sombres, fond sombre, capture."""
    S = Session(CTX["browser"], width=1100, scheme="dark")
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    c(page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(17, 15, 25)", "dark page background")
    shot(page, "map-dark.png")
    D = json.load(open(os.path.join(ROOT, "data", "ng.json"), encoding="utf8"))
    open_country(page, "566", "en")
    page.wait_for_selector(".theme-grid")
    page.click(f'[data-prio="{D["ed"]["themes"][1]["id"]}"]')
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    answer_all(page, lambda qi: ([1, 2, -2, 0, -1][qi % 5], False), stop_after_prio=True)
    apc = next(p for p in D["ed"]["parties"] if p["id"] == "apc")
    cols = page.evaluate("""() => { const li = [...document.querySelectorAll('#pan0 .rank li')].find(l => l.querySelector('.badge').textContent === 'APC');
        return [getComputedStyle(li.querySelector('.badge')).backgroundColor, getComputedStyle(li.querySelector('.bar span')).backgroundColor] }""")
    c(cols == [rgb(apc["col"][1])] * 2, f"dark APC badge + bar colour {cols}")
    shot(page, "ng-dark-results.png", full=True)
    # data-theme="light" force le thème clair malgré la préférence sombre
    page.evaluate("document.documentElement.setAttribute('data-theme', 'light')")
    c(page.evaluate("getComputedStyle(document.querySelector('#pan0 .badge')).backgroundColor") == rgb(next(p for p in D["ed"]["parties"] if p["sigle"] == page.inner_text("#pan0 .badge"))["col"][0]), "data-theme=light restores light party colours")
    page.evaluate("document.documentElement.removeAttribute('data-theme')")
    S.close(c)


@test
def info_page(c):
    """Page d'information (édition de test sur les Comores) : repère « i » sur l'île, langues, RTL, encadré « pourquoi »."""
    S = Session(CTX["browser"], width=400, height=860)
    page = S.page
    page.goto(CTX["fbase"] + "/site/index.html")
    page.wait_for_selector("#mapWrap svg")
    pos = page.evaluate("""() => { const r = document.querySelectorAll('#mapWrap .pin-info');
        return { isl: MAP.isl['174'], marks: [...r].map(g => { const c = g.querySelector('.ring'); return [+c.getAttribute('cx'), +c.getAttribute('cy')] }),
                 up: document.querySelector('.isl[data-place="174"]').classList.contains('up'), status: statusLine('174') } }""")
    c(pos["isl"] in pos["marks"], "info marker on the Comoros island coordinates")
    c(pos["up"], "Comoros coloured from META (election by end 2027)")
    page.click('.isl[data-place="174"]')
    page.wait_for_selector("#langDlg[open]")
    Lfr = strings(page, "fr")  # interface encore en français
    enabled = page.evaluate("[...document.querySelectorAll('#langBody .lang-btn')].filter(b => !b.disabled).map(b => b.dataset.pick).sort()")
    c(enabled == ["ar", "en"], f"Comoros: ar + en enabled ({enabled})")
    c(page.locator(f'#langBody .lang-btn[disabled] .lnote:text-is("{Lfr["langNoInfo"]}")').count() == 3, "disabled languages carry a note")
    c(Lfr["legInfo"] in page.inner_text("#langBody"), "dialog says information page")
    page.click('#langBody [data-pick="ar"]')
    page.wait_for_selector(".why-box")
    L = strings(page, "ar")
    c(page.evaluate("document.documentElement.dir") == "rtl", "Arabic info page is RTL")
    c(page.inner_text(".strip b").endswith("[ar] Legislative elections 2027"), "translated strip")
    c(page.locator(".actors li").count() == 3 and page.locator(".actors li .src a").count() == 3, "actors with their sources")
    c(L["infoWhy"] in page.inner_text(".why-box h2") and "[ar] Fixture reason" in page.inner_text(".why-box p"), "why box")
    c(page.locator(".info-src .src-list li").count() == 2, "sources list")
    c(page.locator(f'.info-src .caveat:text-is("{L["mTransl"]}")').count() == 1, "translation note on a translated page")
    c("Fixture caveat" in page.inner_text("#app"), "META note shown")
    c(sorted(b.strip() for b in page.locator("#langs button:not([disabled])").all_inner_texts()) == ["AR", "EN"], "header offers ar + en only")
    no_overflow(page, c, "info page 400px")
    shot(page, "info-km-ar-400.png", full=True)
    page.click('#langs [data-lang="en"]')
    c(page.locator(".info-src .caveat").count() == 0 and "Fixture reason why" in page.inner_text(".why-box p"), "base language: no translation note")
    page.click('[data-go="nigeria"]')
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("state.country") == "ng", "Try it with Nigeria from an information page")
    S.close(c)


@test
def leader_edition(c):
    """Édition role:"leader" (test, Congo) : dirigeant·e du parti, candNote traduite, méthode adaptée, couleurs."""
    S = Session(CTX["browser"], width=1100)
    page = S.page
    page.goto(CTX["fbase"] + "/site/index.html")
    page.wait_for_selector("#mapWrap svg")
    open_country(page, "178", "fr")
    page.wait_for_selector(".theme-grid")
    D = json.load(open(os.path.join(CTX["site"], "data", "cg.json"), encoding="utf8"))
    L = strings(page, "fr")
    page.click(".about details:nth-of-type(2) summary")
    subs = page.locator(".party-list .pb-sub").all_inner_texts()
    c(all(s.startswith(L["partyLeader"]) for s in subs), f"party leader label: {subs}")
    c("[fr] Candidate not yet designated" in subs[1], "translated candNote")
    c(page.inner_text(".basis").strip() == L["partyBasisLeader"], "leader basis text")
    c(page.evaluate("getComputedStyle(document.querySelector('.party-list .badge')).backgroundColor") == rgb(D["ed"]["parties"][0]["col"][0]), "fixture colour")
    page.click('[data-prio="health"]')
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    c(page.inner_text(".slip h2").startswith("[fr] "), "translated question")
    answers, double = answer_all(page, lambda qi: ([2, 1, 0, -1, -2][(qi * 3) % 5], qi == 21))
    answers = {k: v for k, v in answers.items() if v is not None}
    check_results_page(page, c, D, "fr", L, answers, double, ["health"], "cg-fr")
    c(page.locator(f'#pan3 .method li:text-is("{L["mCodingLead"]}")').count() == 1, "method: leader coding line")
    c(page.locator("#pan0 .rank-sub").first.inner_text().startswith(L["partyLeader"]), "ranking: leader label")
    page.click('#pan0 [data-fiche="cg_bet"]')
    page.wait_for_selector("#fiche[open]")
    c(L["partyLeader"] in page.inner_text("#fiche .fiche-head p") and "[fr] Candidate" in page.inner_text("#fiche .fiche-head p"), "fiche: leader + candNote")
    shot(page, "leader-cg-fiche.png")
    page.click("#ficheClose")
    page.click('#langs [data-lang="en"]')
    c(page.locator("#pan3 .method li.transl").count() == 0, "base language: no translation note")
    c(page.locator('#langs button[data-lang="pt"][disabled]').count() == 1, "dropped language disabled in header")
    S.close(c)


@test
def offline(c):
    """Données inaccessibles : écran d'erreur avec « Réessayer », puis reprise ; chargement visible et annulable."""
    S = Session(CTX["browser"], width=400, height=860)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    blocked = []
    page.route("**/data/*.json", lambda r: (blocked.append(r.request.url), r.abort()))
    open_country(page, "566", "en")
    page.wait_for_selector('[data-go="retry"]')
    L = strings(page, "en")
    c(page.inner_text('[data-go="retry"]').strip() == L["retry"], "retry button")
    c(page.locator('[role="alert"] h1').count() == 1, "error announced (role=alert)")
    c(page.evaluate("document.activeElement && document.activeElement.dataset.go") == "retry", "focus on retry")
    c(blocked and blocked[0].endswith("/data/ng.json"), "relative data URL")
    no_overflow(page, c, "error screen")
    shot(page, "offline-error-400.png")
    page.click('#langs [data-lang="sw"]')
    c(page.inner_text('[data-go="retry"]').strip() == strings(page, "sw")["retry"], "error screen follows UI language")
    page.unroute("**/data/*.json")
    page.click('[data-go="retry"]')
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("[state.country, state.ui]") == ["ng", "sw"], "retry loads the edition")
    page.close()
    # Chargement lent : écran de chargement, retour à la carte, puis la réponse arrive sans détourner l'utilisateur
    page = S.ctx.new_page()
    page.on("pageerror", lambda e: S.errors.append(str(e)))
    held = []
    page.route("**/data/ng.json", lambda r: held.append(r))
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    open_country(page, "566", "en")
    page.wait_for_selector('.load-box[role="status"]')
    c("Nigeria" in page.inner_text(".load-box"), "loading screen names the country")
    page.click('#app [data-go="home"]')
    wait_view(page, "map")
    held[0].continue_()
    page.wait_for_function("() => !!DATA.ng")
    page.wait_for_timeout(200)
    c(page.evaluate("state.view") == "map", "late response does not hijack the map")
    open_country(page, "566", "en")
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("state.country") == "ng", "cached edition opens at once")
    S.close(c, allow_console=True)


@test
def all_editions(c):
    """Chaque édition réelle du catalogue, dans chacune de ses langues (questionnaire : départ, une réponse, résultats ;
    fiche d'information : contenu), puis artifact.html. Couvre automatiquement les pays ajoutés."""
    cat = CTX["catalog"]
    S = Session(CTX["browser"], width=1100)
    page = S.page
    for cc, e in sorted(cat.items()):
        if not e["a3"] or cc == "ng":
            continue
        D = json.load(open(os.path.join(ROOT, "data", cc + ".json"), encoding="utf8"))
        for lang in e["langs"]:
            w = f"{cc}-{lang}"
            page.goto(CTX["base"] + "/index.html")
            page.wait_for_selector("#mapWrap svg")
            page.click("#listBox summary")
            page.click(f'#clist [data-place="{e["a3"]}"]')
            page.wait_for_selector("#langDlg[open]")
            enabled = page.evaluate("[...document.querySelectorAll('#langBody .lang-btn')].filter(b => !b.disabled).map(b => b.dataset.pick).sort()")
            c(enabled == sorted(e["langs"]), f"{w}: dialog offers {enabled}")
            page.click(f'#langBody [data-pick="{lang}"]')
            if e["kind"] == "info":
                page.wait_for_selector(".why-box")
                c(page.locator(".actors li").count() == len(D["info"]["actors"]), f"{w}: actors")
                c(page.locator(".info-src .src-list li").count() >= 1, f"{w}: sources")
                if lang == e["langs"][0]:
                    shot(page, f"info-{cc}.png", full=True)
                continue
            page.wait_for_selector(".theme-grid")
            E = D["ed"]
            c(page.locator(".party-list li").count() == len(E["parties"]), f"{w}: parties listed")
            label = strings(page, lang)["partyLeader" if E["role"] == "leader" else "presCand"]
            first = E["parties"][0]
            subs = [x.strip() for x in page.locator(".party-list .pb-sub").all_text_contents()]
            for p, sub in zip(E["parties"], subs):
                want = strings(page, lang)["partyLeader"] if p.get("candNote") else label
                c(sub.startswith(want), f"{w}: {p['sigle']} label “{sub[:40]}”")
                c(not p.get("candNote") or "(" in sub, f"{w}: {p['sigle']} candNote shown")
            bg = page.evaluate("getComputedStyle(document.querySelector('.party-list .badge')).backgroundColor")
            c(bg == rgb(first["col"][0]), f"{w}: party colour {bg}")
            page.click(f'[data-prio="{E["themes"][0]["id"]}"]')
            page.click('[data-go="startq"]')
            wait_view(page, "question")
            page.evaluate("() => { ed().questions.forEach((q, i) => { state.answers[i] = (i % 5) - 2; }); go('results'); }")
            wait_view(page, "results")
            c(page.locator("#pan0 .rank li").count() == len(E["parties"]), f"{w}: ranking")
            c((page.locator("#pan3 .method li.transl").count() == 1) == (lang != D["lang"]), f"{w}: translation note")
    page.goto(CTX["base"] + "/artifact.html")
    page.wait_for_selector("#mapWrap svg")
    open_country(page, "566", "fr")
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("state.country") == "ng", "artifact.html loads editions too")
    S.close(c)


# ------------------------------------------------------------------ exécution
def main():
    t0 = time.time()
    only = set(filter(None, ARGS.only.split(",")))
    must = {"build_outputs", "build_fixtures"}
    procs = []
    proc, CTX["base"] = serve(ROOT)
    procs.append(proc)
    try:
        with sync_playwright() as pw:
            CTX["browser"] = pw.chromium.launch(headless=not ARGS.headed)
            for fn in TESTS:
                if only and fn.__name__ not in only and fn.__name__ not in must:
                    continue
                if fn.__name__ in ("info_page", "leader_edition") and "fbase" not in CTX:
                    if "site" not in CTX:
                        RESULTS.append((fn.__name__, False, 0, "fixture site not built", 0))
                        continue
                    p2, CTX["fbase"] = serve(os.path.dirname(CTX["site"]))
                    procs.append(p2)
                c = Check()
                t1 = time.time()
                try:
                    fn(c)
                    RESULTS.append((fn.__name__, True, c.n, "", time.time() - t1))
                except Exception as e:
                    msg = f"{type(e).__name__}: {e}".split("\n")[0][:300]
                    if not isinstance(e, AssertionError):
                        msg += " @ " + traceback.extract_tb(e.__traceback__)[-1].line[:120]
                    RESULTS.append((fn.__name__, False, c.n, msg, time.time() - t1))
            CTX["browser"].close()
    finally:
        for p in procs:
            p.terminate()
        if CTX.get("tmp"):
            shutil.rmtree(CTX["tmp"], ignore_errors=True)
    print()
    for name, ok, n, msg, dt in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<24} {n:>4} checks  {dt:5.1f}s{'  ' + msg if msg else ''}")
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS)} tests, {len(RESULTS) - len(failed)} passed, {len(failed)} failed · "
          f"{sum(r[2] for r in RESULTS)} checks · {time.time() - t0:.1f}s · screenshots in {ARGS.shots}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
