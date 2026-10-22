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
import argparse, functools, json, math, os, random, re, shutil, socket, subprocess, sys, tempfile, time, traceback, urllib.request

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
            "langNoQ", "langNoInfo", "retry", "infoWhy", "infoActors", "proto", "seeResults", "tryNigeria", "mapHint",
            "thinTitle", "straight", "resReady", "double", "themesTitle", "cancel", "confirmRestart", "confirmHome", "footer2"]
BRAND = "Éclaire ton vote"
FSI, PDI = "\u2068", "\u2069"
COV_MIN, TIE, EQ, EARLY = 0.4, 0.03, 0.005, 8   # règles de lecture des résultats (copie de src/app.js)


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

    def __init__(self, browser, width=1280, height=900, scheme="light", motion="reduce", locale="en-GB", init=None):
        # Mouvement réduit par défaut : Playwright n'attend pas la fin de l'animation d'entrée à chaque clic
        self.ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=scheme, locale=locale, reduced_motion=motion)
        if init:
            self.ctx.add_init_script(init)
        self.errors, self.console, self.external, self.dialogs = [], [], [], []

        def outside(route):
            url = route.request.url
            if re.match(r"https://fonts\.(googleapis|gstatic)\.com/", url):
                route.fulfill(status=200, content_type="text/css", body="")
            else:
                self.external.append(url)
                route.abort()

        self.ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1[:/])"), outside)
        self.page = self.new_page()

    def new_page(self):
        page = self.ctx.new_page()
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        page.on("console", lambda m: m.type == "error" and self.console.append(m.text))
        # confirm()/alert() sont bloqués chez certains hébergeurs : l'application ne doit jamais les appeler
        page.on("dialog", lambda d: (self.dialogs.append(d.type), d.dismiss()))
        return page

    def close(self, c, allow_console=False):
        try:
            c(not self.errors, f"page errors: {self.errors[:3]}")
            c(allow_console or not self.console, f"console errors: {self.console[:3]}")
            c(not self.external, f"external requests: {self.external[:3]}")
            c(not self.dialogs, f"native dialogs opened: {self.dialogs[:3]}")
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


def open_country(page, a3, lang, from_list=False):
    """Touche un pays (carte ou liste) puis choisit la langue. Une fois une langue choisie dans l'onglet, le choix de
    langue n'est plus proposé (on va droit au pays) : on change alors de langue dans l'en-tête si besoin."""
    if from_list:
        if not page.evaluate("document.getElementById('listBox').open"):
            page.click("#listBox summary")
        page.click(f'#clist [data-place="{a3}"]')
    else:
        page.click(f'#mapWrap [data-place="{a3}"]')
    page.wait_for_function("() => document.getElementById('langDlg').open || state.view !== 'map'")
    if page.evaluate("document.getElementById('langDlg').open"):
        page.click(f'#langBody [data-pick="{lang}"]')
        return
    if page.evaluate("state.ui") != lang:
        page.wait_for_function("() => state.view !== 'loading'")
        page.click(f'#langs [data-lang="{lang}"]')


def fresh_tab(page):
    """Oublie la session de l'onglet (sessionStorage) : le choix de langue réapparaît, les réponses sont oubliées."""
    page.evaluate("() => { try { sessionStorage.clear(); } catch (e) {} }")


def live_text(page):
    page.wait_for_timeout(120)  # l'annonce est écrite 60 ms après avoir vidé la région
    return page.inner_text("#live").strip()


def focused_heading(page):
    return page.evaluate("() => { const a = document.activeElement; return a && a.tagName === 'H1' && a.closest('#app') ? a.textContent.trim() : null }")


# ------------------------------------------------------------------ calcul attendu (copie du modèle de l'application)
def js_round(x):
    return math.floor(x + 0.5)


def model_rows(D, answers, double, prios, theme=None):
    """Classement attendu : formule de l'application, puis groupes « ok » (classé : k ≥ 2 et couverture ≥ 40 %),
    « thin » (k ≥ 2, couverture < 40 %), « out » (k < 2) ; par sujet, k ≥ 1. Dans un groupe : score décroissant,
    sigle à score égal (à 0,005 près) ; « out » par sigle."""
    E = D["ed"]
    a = sum(1 for qi, v in answers.items() if isinstance(v, int) and (not theme or E["questions"][qi]["theme"] == theme))
    rows = []
    for p in E["parties"]:
        num = den = k = 0
        for qi, q in enumerate(E["questions"]):
            v = answers.get(qi)
            c = q["cells"].get(p["id"])
            if not isinstance(v, int) or not c or (theme and q["theme"] != theme):
                continue
            w = (2 if double.get(qi) else 1) * (1 if theme else (2 if q["theme"] in prios else 1))
            num += w * (1 - abs(v - c["p"]) / 4)
            den += w
            k += 1
        prior = 1 if theme else 3
        s = (num + prior * 0.5) / (den + prior) if k else None
        cov = k / a if a else 0
        grp = 2 if k < (1 if theme else 2) else (1 if cov < COV_MIN else 0)
        rows.append({"sig": p["sigle"], "nom": p["nom"], "id": p["id"], "s": s, "k": k, "cov": cov, "grp": grp})
    sc = lambda x, y: (x > y) - (x < y)

    def cmp(x, y):
        if x["grp"] != y["grp"]:
            return x["grp"] - y["grp"]
        if x["grp"] == 2:
            return sc(x["sig"], y["sig"])
        d = y["s"] - x["s"]
        return sc(x["sig"], y["sig"]) if abs(d) < EQ else (1 if d > 0 else -1)
    return sorted(rows, key=functools.cmp_to_key(cmp)), a


def expected_ranking(D, answers, double, prios):
    rows, _ = model_rows(D, answers, double, prios)
    return [(r["sig"], js_round(r["s"] * 100) if r["grp"] < 2 else None) for r in rows]


def lead_group(rows):
    ok = [r for r in rows if r["grp"] == 0]
    return [r for r in ok if ok[0]["s"] - r["s"] < TIE] if ok else []


def answer_all(page, plan, stop_after_prio=False):
    """Répond à tout le questionnaire. plan(qi) -> (valeur ou None pour passer, double?)."""
    answers, double = {}, {}
    page.evaluate("TAP_GUARD = 0")  # Playwright clique plus vite qu'un double tapotement : protection testée à part
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
            c_ok = page.get_attribute(f'.star[data-dbl="{qi}"]', "aria-pressed") == "false"
            page.click(".star")
            assert c_ok and page.get_attribute(".star", "aria-pressed") == "true", "★ toggle"
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
    # Clavier : flèches dans la liste d'onglets, dans le sens visuel (inversé de droite à gauche), Début et Fin ; tabindex mobile
    rtl = page.evaluate("document.documentElement.dir") == "rtl"
    nxt, prv = ("ArrowLeft", "ArrowRight") if rtl else ("ArrowRight", "ArrowLeft")
    page.click("#tab0")
    page.focus("#tab0")
    c(page.evaluate("[...document.querySelectorAll('[role=tab]')].map(b => b.tabIndex).join()") == "0,-1,-1,-1", f"{where}: roving tabindex")
    page.keyboard.press(nxt)
    c(page.get_attribute("#tab1", "aria-selected") == "true", f"{where}: {nxt} selects next tab")
    c(page.evaluate("document.activeElement.id") == "tab1", f"{where}: focus follows the selected tab")
    page.keyboard.press(prv)
    page.keyboard.press(prv)
    c(page.get_attribute("#tab3", "aria-selected") == "true", f"{where}: {prv} wraps")
    page.keyboard.press("Home")
    c(page.get_attribute("#tab0", "aria-selected") == "true", f"{where}: Home")
    page.keyboard.press("End")
    c(page.get_attribute("#tab3", "aria-selected") == "true" and page.evaluate("location.hash").endswith("/results/method"), f"{where}: End (tab in the address)")
    page.click("#tab0")
    # Partis peu documentés sur ces réponses : à part, sans rang, jamais dans le titre
    rows, _ = model_rows(D, answers, double, prios)
    thin = [r["sig"] for r in rows if r["grp"] == 1]
    got_thin = page.evaluate("[...document.querySelectorAll('#pan0 .rank li.thin .badge')].map(b => b.textContent)")
    c(got_thin == thin, f"{where}: thin group {got_thin} != expected {thin}")
    c((page.locator("#pan0 h2.rank-h").count() == 1) == bool(thin), f"{where}: thin-group heading iff thin parties")
    if thin:
        c(page.inner_text("#pan0 h2.rank-h").strip() == L["thinTitle"], f"{where}: thin-group heading text")
        c(all(x.strip() == "" for x in page.locator("#pan0 .rank li.thin .pos").all_inner_texts()), f"{where}: thin parties have no rank")
    title = page.inner_text(".res-head h1")
    for r in rows:
        if r["grp"] > 0:
            c(r["sig"] not in title, f"{where}: unranked party {r['sig']} not in the headline “{title}”")
    if D["id"] == "ng":
        c(thin or page.locator(f'#pan0 .chip.warn:text-is("{L["partial"]}")').count() >= 1, f"{where}: thinly documented parties flagged")
    # Fiche parti
    page.locator("#pan0 [data-fiche]").first.click()
    page.wait_for_selector("#fiche[open]")
    c(page.inner_text("#ficheTitle").strip() != "", f"{where}: fiche title")
    c(page.locator("#fiche .pos-table li").count() == nq, f"{where}: fiche positions")
    c(page.evaluate("document.activeElement && document.activeElement.id") == "ficheClose", f"{where}: focus on close")
    page.click("#ficheClose")
    c(not page.is_visible("#fiche"), f"{where}: fiche closes")


def run_nigeria(browser, base, lang, width, c, switch_to=None, screenshot=None):
    S = Session(browser, width=width, height=844 if width < 400 else 900, motion="no-preference" if lang == "en" else "reduce")
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


def info_i18n(I, lang, drop_why=False, note=None):
    L = {"strip": f"[{lang}] {I['strip']}", "stripDate": f"[{lang}] {I['stripDate']}",
         "facts": [[f"[{lang}] {a}", b] for a, b in I["facts"]], "system": [[f"[{lang}] {a}", f"[{lang}] {b}"] for a, b in I["system"]],
         "actors": [[f"[{lang}] {a[0]}", f"[{lang}] {a[1]}"] for a in I["actors"]], "why": f"[{lang}] {I['why']}"}
    if drop_why:
        del L["why"]
    if note is not None:
        L["note"] = note
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
    # note : META.note traduite (ar) ; fr serait écartée de toute façon (why manquant)
    write_js(os.path.join(fx, "i18n", "km.js"), I18N_KM={"ar": info_i18n(I, "ar", note="[ar] Fixture caveat about the date."),
                                                         "fr": info_i18n(I, "fr", drop_why=True)})
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
    # Un pays sans édition (le premier par nom anglais : les éditions s'ajoutent au fil du temps)
    nid, nname = page.evaluate("(() => { const id = Object.keys(AFRICA).filter(id => !catFor(id)).sort((a, b) => AFRICA[a].en.localeCompare(AFRICA[b].en))[0]; return [id, AFRICA[id].en]; })()")
    page.click("#listBox summary")
    page.fill("#csearch", nname)
    c(page.locator(f'#clist .cbtn[data-place="{nid}"]').count() == 1, f"country search ({nname})")
    page.click(f'#clist [data-place="{nid}"]')
    page.wait_for_selector("#langDlg[open]")
    c(page.locator("#langBody .lang-btn[disabled]").count() == 0, "no-data country: every language enabled")
    page.click('#langBody [data-pick="pt"]')
    wait_view(page, "info")
    c(page.evaluate(f"cname('{nid}')") in page.inner_text(".strip"), "no-data info screen")
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
                              ("sw", 400, "ar", None), ("ar", 390, "en", "ng-ar-results-390.png")]:
    test(make_ng_test(_lang, _w, _sw, _shot))


@test
def france(c):
    """Prototype France : lien hors Afrique, français seulement, 9 partis."""
    S = Session(CTX["browser"], width=1100)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    shot(page, "map-desktop.png")
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
    page.click('#app [data-go="home"]')
    c(page.is_visible("#confirmBox") and page.evaluate("state.view") == "results", "change country asks first")
    page.click('#confirmBox [data-go="home!"]')
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
    c(page.evaluate("state.ui") == "en", "interface starts in the browser language (en-GB → en)")
    Lui = strings(page, "en")  # langue de l'interface pendant le choix
    enabled = page.evaluate("[...document.querySelectorAll('#langBody .lang-btn')].filter(b => !b.disabled).map(b => b.dataset.pick).sort()")
    c(enabled == ["ar", "en"], f"Comoros: ar + en enabled ({enabled})")
    c(page.locator(f'#langBody .lang-btn[disabled] .lnote:text-is("{Lui["langNoInfo"]}")').count() == 3, "disabled languages carry a note")
    c(Lui["legInfo"] in page.inner_text("#langBody"), "dialog says information page")
    page.click('#langBody [data-pick="ar"]')
    page.wait_for_selector(".why-box")
    L = strings(page, "ar")
    c(page.evaluate("document.documentElement.dir") == "rtl", "Arabic info page is RTL")
    c(page.inner_text(".strip b").endswith("[ar] Legislative elections 2027"), "translated strip")
    c(page.locator(".actors li").count() == 3 and page.locator(".actors li .src a").count() == 3, "actors with their sources")
    c(L["infoWhy"] in page.inner_text(".why-box h2") and "[ar] Fixture reason" in page.inner_text(".why-box p"), "why box")
    c(page.locator(".info-src .src-list li").count() == 2, "sources list")
    c(page.locator(f'.info-src .caveat:text-is("{L["mTransl"]}")').count() == 1, "translation note on a translated page")
    note = page.locator(".caveat span[dir='auto']")
    c(note.count() == 1 and note.inner_text().strip() == "[ar] Fixture caveat about the date." and note.get_attribute("lang") == "ar",
      "META note translated (i18n note), isolated with dir=auto")
    c(sorted(b.strip() for b in page.locator("#langs button:not([disabled])").all_inner_texts()) == ["AR", "EN"], "header offers ar + en only")
    no_overflow(page, c, "info page 400px")
    shot(page, "info-km-ar-400.png", full=True)
    page.click('#langs [data-lang="en"]')
    c(page.locator(".info-src .caveat").count() == 0 and "Fixture reason why" in page.inner_text(".why-box p"), "base language: no translation note")
    c(page.inner_text(".caveat span[dir='auto']").strip() == "Fixture caveat about the date.", "META note in the base language")
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
    c(page.inner_text(".slip h1").startswith("[fr] "), "translated question (the statement is the page's h1)")
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
    # Chargement lent : écran de chargement, retour à la carte, pays rouvert pendant le chargement (un seul
    # téléchargement), puis la réponse arrive sans détourner l'utilisateur
    page = S.new_page()
    held = []
    page.route("**/data/ng.json", lambda r: held.append(r))
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    open_country(page, "566", "en")
    page.wait_for_selector('.load-box[role="status"]')
    c("Nigeria" in page.inner_text(".load-box"), "loading screen names the country")
    page.click('#app [data-go="home"]')
    wait_view(page, "map")
    open_country(page, "566", "en")  # langue déjà choisie dans l'onglet : pas de choix de langue
    page.wait_for_selector('.load-box[role="status"]')
    page.wait_for_timeout(150)
    c(len(held) == 1, f"country reopened while loading: one download ({len(held)})")
    page.click('#app [data-go="home"]')
    wait_view(page, "map")
    held[0].continue_()
    page.wait_for_function("() => !!DATA.ng")
    page.wait_for_timeout(200)
    c(page.evaluate("state.view") == "map", "late response does not hijack the map")
    open_country(page, "566", "en")
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("state.country") == "ng", "cached edition opens at once")
    page.close()
    # Délai dépassé (réduit ici) : écran d'erreur avec « Réessayer » ; pendant le chargement, l'en-tête ne propose
    # que les langues du pays (catalogue)
    cat = CTX["catalog"]
    cc = "ke" if "ke" in cat else next(k for k, e in sorted(cat.items()) if e["a3"] and e["kind"] == "ed" and 1 < len(e["langs"]) < 5)
    page = S.new_page()
    page.route(f"**/data/{cc}.json", lambda r: None)  # ne répond jamais
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    page.evaluate("LOAD_TIMEOUT = 1500")
    open_country(page, cat[cc]["a3"], cat[cc]["langs"][-1])
    page.wait_for_selector(".load-box")
    offered = sorted(b.strip().lower() for b in page.locator("#langs button:not([disabled])").all_inner_texts())
    c(offered == sorted(cat[cc]["langs"]), f"{cc} loading: header offers {offered}")
    page.wait_for_selector('[data-go="retry"]', timeout=6000)
    c(page.evaluate("state.view") == "loaderror" and page.evaluate("document.activeElement.dataset.go") == "retry", "timeout → error screen, focus on retry")
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
            fresh_tab(page)
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
    fresh_tab(page)
    page.goto(CTX["base"] + "/artifact.html")
    page.wait_for_selector("#mapWrap svg")
    open_country(page, "566", "fr")
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("state.country") == "ng", "artifact.html loads editions too")
    S.close(c)


# ------------------------------------------------------------------ navigation, mémoire, accessibilité, lecture des résultats
def ng_start(page, lang="en", prio=0):
    """Nigeria, départ, un sujet prioritaire, première question (protection contre le double tapotement désactivée)."""
    D = json.load(open(os.path.join(ROOT, "data", "ng.json"), encoding="utf8"))
    open_country(page, "566", lang)
    page.wait_for_selector(".theme-grid")
    th = D["ed"]["themes"][prio]["id"]
    page.click(f'[data-prio="{th}"]')
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    page.evaluate("TAP_GUARD = 0")
    return D, th


def answer_one(page, v):
    i = page.evaluate("state.i")
    page.click(f'.answers .ans[data-val="{v}"]')
    page.wait_for_function("i => state.view !== 'question' || state.i !== i", arg=i, timeout=5000)


@test
def deep_links(c):
    """Adresses : #ke (forme courte) → choix de langue du Kenya ; #/ke/sw, #cv-pt directs ; adresses inconnues ou sans
    session dégradées ; langue de départ (navigateur), langue retenue d'un chargement à l'autre ; stockage indisponible."""
    cat, base = CTX["catalog"], CTX["base"]
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    if "ke" in cat:
        page.goto(base + "/index.html#ke")
        page.wait_for_selector("#langDlg[open]")
        c(page.evaluate("location.hash") == "#/ke", "#ke normalised to #/ke")
        c(page.text_content("#langBody .eyebrow").strip() == page.evaluate(f"cname('{cat['ke']['a3']}')"), "#ke: language choice for Kenya")
        page.click('#langBody [data-pick="sw"]')
        page.wait_for_selector(".theme-grid")
        c(page.evaluate("[state.country, state.ui, document.documentElement.lang, location.hash]") == ["ke", "sw", "sw", "#/ke/sw"], "#ke → Kenya in Swahili")
    S.close(c)
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    if "ke" in cat:
        page.goto(base + "/index.html#/ke/sw")
        page.wait_for_function("() => state.country === 'ke' && state.view === 'start'")
        c(page.evaluate("[state.country, state.ui, document.getElementById('langDlg').open]") == ["ke", "sw", False], "#/ke/sw: Kenya in Swahili, no language dialog")
        c(page.get_attribute('#langs [data-lang="sw"]', "aria-pressed") == "true", "#/ke/sw: header shows Swahili")
        c(page.evaluate("document.title").endswith(" · " + BRAND), "#/ke/sw: document title")
    if "cv" in cat and "pt" in cat["cv"]["langs"]:
        page.goto(base + "/index.html#cv-pt")  # même document : changement d'ancre seulement (hashchange)
        page.wait_for_function("() => state.country === 'cv' && state.view === 'start'")
        c(page.evaluate("[state.country, state.ui, location.hash]") == ["cv", "pt", "#/cv/pt"], "#cv-pt → Cabo Verde in Portuguese")
    page.goto(base + "/index.html#/zz/en/q/3")
    wait_view(page, "map")
    c(page.evaluate("[state.view, location.hash]") == ["map", "#/"], "unknown country → map")
    page.goto(base + "/index.html#/ng/en/q/5")
    page.wait_for_function("() => state.country === 'ng' && state.view === 'start'")
    c(page.evaluate("[state.view, location.hash]") == ["start", "#/ng/en"], "question without a questionnaire in progress → start screen")
    nid, n2 = page.evaluate("(() => { const id = Object.keys(AFRICA).filter(id => !catFor(id)).sort()[0]; return [id, AFRICA[id].a2.toLowerCase()]; })()")
    page.goto(base + f"/index.html#/{n2}/pt")
    page.wait_for_function(f"() => state.view === 'info' && state.place === '{nid}'")
    c(page.evaluate("[state.ui, location.hash]") == ["pt", f"#/{n2}/pt"], f"country without edition (#/{n2}/pt) → its page")
    shot(page, f"deeplink-{n2}-pt-390.png")
    S.close(c)
    # Langue de départ : celle du navigateur si l'interface la connaît, sinon l'anglais ; puis celle choisie
    for loc, want in [("sw-KE", "sw"), ("ar-EG", "ar"), ("pt-CV", "pt"), ("de-DE", "en")]:
        S = Session(CTX["browser"], width=800, locale=loc)
        S.page.goto(base + "/index.html")
        S.page.wait_for_selector("#mapWrap svg")
        c(S.page.evaluate("[state.ui, document.documentElement.lang, document.documentElement.dir]") == [want, want, "rtl" if want == "ar" else "ltr"], f"browser {loc} → interface {want}")
        if loc == "sw-KE":
            S.page.click('#langs [data-lang="fr"]')
            S.page.reload()
            S.page.wait_for_selector("#mapWrap svg")
            c(S.page.evaluate("state.ui") == "fr", "language kept after reload")
            p2 = S.new_page()
            p2.goto(base + "/index.html")
            p2.wait_for_selector("#mapWrap svg")
            c(p2.evaluate("[state.ui, document.documentElement.lang]") == ["fr", "fr"], "language kept in a new tab (localStorage etv.ui)")
            c("Tes réponses restent sur ton appareil" in p2.inner_text("#footer"), "privacy footer")
            p2.close()
        S.close(c)
    # Stockage indisponible (navigation privée stricte, iframe en bac à sable) : l'application marche quand même
    S = Session(CTX["browser"], width=390, height=844, init="""for (const k of ['localStorage', 'sessionStorage'])
        Object.defineProperty(window, k, { configurable: true, get() { throw new DOMException('denied', 'SecurityError'); } });""")
    page = S.page
    page.goto(base + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    ng_start(page)
    answer_one(page, 2)
    c(page.evaluate("[state.view, state.i, Object.keys(state.answers).length]") == ["question", 1, 1], "works without storage")
    S.close(c)


@test
def history_nav(c):
    """Retour (Android) : depuis une question → départ avec « Reprendre » ; depuis les résultats → questionnaire.
    Rechargement en cours de questionnaire (même onglet) : réponses, « compte double », question. Focus, titre, annonces."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    L = strings(page, "en")
    open_country(page, "566", "en")
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("location.hash") == "#/ng/en", "start: #/ng/en")
    c(focused_heading(page) == L["themesTitle"], f"focus on the start heading ({focused_heading(page)})")
    c(page.evaluate("document.title") == L["themesTitle"].rstrip(".:") + " · " + BRAND, "start: document title")
    D = json.load(open(os.path.join(ROOT, "data", "ng.json"), encoding="utf8"))
    th = D["ed"]["themes"][0]["id"]
    nprio = sum(1 for q in D["ed"]["questions"] if q["theme"] == th)
    page.click(f'[data-prio="{th}"]')
    c(live_text(page) == page.evaluate("T.en.chosen(1)"), "priority count announced")
    c(page.evaluate("document.getElementById('live').closest('#app')") is None, "live region outside #app")
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    page.evaluate("TAP_GUARD = 0")
    q0 = page.evaluate("ed().questions[state.order[0]].text")
    c(page.evaluate("location.hash") == "#/ng/en/q/1", "question 1 in the address")
    c(page.locator("h1").count() == 1 and page.inner_text(".slip h1").strip() == q0, "the statement is the page's h1")
    c(focused_heading(page) == q0, "focus on the statement")
    c(page.evaluate("document.title").endswith(" · " + BRAND), "question: document title")
    n_q = len(D["ed"]["questions"])
    c(live_text(page) == page.evaluate(f"T.en.qOf(1, {n_q})"), "question number announced")
    h_len = page.evaluate("history.length")
    for v in (2, 1, -1):
        answer_one(page, v)
    c(page.evaluate("location.hash") == "#/ng/en/q/4" and focused_heading(page) == page.evaluate("ed().questions[state.order[3]].text"), "auto-advance: q/4, focus on the new statement")
    c(page.evaluate("history.length") == h_len, "questions replace one history entry")
    c(live_text(page) == page.evaluate(f"T.en.qOf(4, {n_q})"), "new question announced")
    qi3 = page.evaluate("state.order[3]")
    page.click(".star")
    shot(page, "ng-question-390.png")
    # Retour depuis une question : l'écran d'avant (le départ), réponses gardées, « Reprendre »
    page.go_back()
    wait_view(page, "start")
    c(page.evaluate("[location.hash, Object.keys(state.answers).length]") == ["#/ng/en", 3], "Back from a question → start screen, answers kept")
    c(page.is_visible('.resume [data-go="resume"]'), "resume offered")
    page.click('.resume [data-go="resume"]')
    wait_view(page, "question")
    c(page.evaluate("[state.i, location.hash]") == [3, "#/ng/en/q/4"], "resume → question 4")
    # Rechargement (onglet mis en veille par le téléphone) : tout revient
    page.reload()
    wait_view(page, "question")
    page.evaluate("TAP_GUARD = 0")
    c(page.evaluate("[state.i, Object.keys(state.answers).length, state.double[state.order[state.i]] === true, state.priorities.length]") == [3, 3, True, 1],
      "reload restores question, answers, counts-double, priorities")
    c(page.get_attribute(".star", "aria-pressed") == "true" and page.get_attribute(".star", "data-dbl") == str(qi3), "reload: ★ still on")
    c(page.evaluate("document.documentElement.lang") == "en", "reload keeps the language")
    for _ in range(nprio - 3):
        answer_one(page, 0)
    wait_view(page, "checkpoint")
    c(page.evaluate("location.hash") == "#/ng/en/checkpoint", "checkpoint in the address")
    page.click('[data-go="results"]')
    wait_view(page, "results")
    c(page.evaluate("location.hash") == "#/ng/en/results", "results in the address")
    c(live_text(page) == L["resReady"], "results announced")
    c(focused_heading(page) == page.inner_text(".res-head h1").strip(), "focus on the results headline")
    # Retour depuis les résultats : le questionnaire ; Suivant : les résultats
    page.go_back()
    wait_view(page, "checkpoint")
    page.go_forward()
    wait_view(page, "results")
    page.click("#tab3")
    c(page.evaluate("location.hash") == "#/ng/en/results/method", "tab in the address")
    page.reload()
    wait_view(page, "results")
    c(page.get_attribute("#tab3", "aria-selected") == "true" and page.is_visible("#pan3"), "reload keeps the tab")
    page.go_back()
    wait_view(page, "checkpoint")
    page.go_back()
    wait_view(page, "start")
    page.go_back()
    wait_view(page, "map")
    c(page.url.split("#")[0].endswith("/index.html"), "Back never leaves the app")
    c(page.evaluate("Object.keys(state.answers).length") == nprio, "answers survive a visit to the map")
    shot(page, "map-390.png")
    S.close(c)


@test
def edit_and_confirm(c):
    """Corriger depuis les résultats ramène aux résultats ; « Recommencer » et « Changer de pays » demandent confirmation dans la page."""
    S = Session(CTX["browser"], width=1100)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    L = strings(page, "en")
    D, th = ng_start(page)
    nprio = sum(1 for q in D["ed"]["questions"] if q["theme"] == th)
    for k in range(nprio):
        answer_one(page, [2, 1, 0, -1, -2][k % 5])
    wait_view(page, "checkpoint")
    page.click('[data-go="results"]')
    wait_view(page, "results")
    # Une question, depuis l'onglet « par question »
    page.click("#tab2")
    page.locator("#pan2 .qa").nth(2).locator("[data-goto]").click()
    wait_view(page, "question")
    qi = page.evaluate("state.order[2]")
    c(page.evaluate("[state.i, location.hash]") == [2, "#/ng/en/q/3"], "edit one question from the By-question tab")
    page.go_back()
    wait_view(page, "results")
    c(page.get_attribute("#tab2", "aria-selected") == "true", "Back from the edited question → results, same tab")
    page.locator("#pan2 .qa").nth(2).locator("[data-goto]").click()
    wait_view(page, "question")
    page.evaluate("TAP_GUARD = 0")
    page.click('.answers .ans[data-val="-2"]')
    wait_view(page, "results")
    c(page.evaluate(f"state.answers[{qi}]") == -2, "edited answer saved")
    c(page.evaluate("location.hash") == "#/ng/en/results/questions", "back to results (same tab) after editing")
    page.go_back()
    wait_view(page, "checkpoint")
    page.go_forward()
    wait_view(page, "results")
    # « Modifier mes réponses » : on repasse sur les questions vues, puis retour aux résultats
    page.click('[data-go="edit"]')
    wait_view(page, "question")
    page.evaluate("TAP_GUARD = 0")
    c(page.evaluate("state.i") == 0, "Change my answers → first question")
    for k in range(nprio):
        answer_one(page, 1)
    wait_view(page, "results")
    c(page.evaluate(f"Object.values(state.answers).filter(v => v === 1).length") == nprio, "Change my answers → back to results after the last answered question")
    # Un sujet pas encore répondu, depuis « par sujet »
    page.click("#tab1")
    page.locator("#pan1 [data-until]").first.click()
    wait_view(page, "question")
    page.evaluate("TAP_GUARD = 0")
    th2 = page.evaluate("ed().questions[state.order[state.i]].theme")
    n2 = sum(1 for q in D["ed"]["questions"] if q["theme"] == th2)
    for k in range(n2):
        c(page.evaluate("state.view") == "question", f"answering issue {th2} ({k + 1}/{n2})")
        answer_one(page, -1)
    wait_view(page, "results")
    c(page.evaluate(f"ed().questions.filter((q, i) => q.theme === '{th2}' && state.answers[i] === -1).length") == n2, "Answer this issue → back to results")
    # Recommencer : confirmation dans la page (pas de confirm()), Annuler, puis Effacer
    n_ans = page.evaluate("Object.keys(state.answers).length")
    page.click('#app [data-go="restart"]')
    c(page.is_visible("#confirmBox") and page.evaluate("state.view") == "results", "restart asks first (in the page)")
    c(page.inner_text("#confirmMsg").strip() == page.evaluate(f"T.en.confirmLose({n_ans})"), "confirmation says how many answers")
    c(page.evaluate("document.activeElement.id") == "confirmMsg", "focus on the confirmation")
    page.click('#confirmBox [data-go="noconfirm"]')
    c(page.locator("#confirmBox").count() == 0 and page.evaluate("document.activeElement.dataset.go") == "restart", "cancel → focus back on the button")
    c(page.evaluate("Object.keys(state.answers).length") == n_ans, "cancel keeps the answers")
    page.click('#app [data-go="restart"]')
    page.click('#confirmBox [data-go="restart!"]')
    wait_view(page, "start")
    c(page.evaluate("[Object.keys(state.answers).length, state.priorities.length]") == [0, 0], "confirmed restart erases")
    # Changer de pays depuis une question (logo), avec des réponses
    page.click(f'[data-prio="{th}"]')
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    page.evaluate("TAP_GUARD = 0")
    answer_one(page, 2)
    page.click("#brand")
    c(page.is_visible("#confirmBox") and page.evaluate("state.view") == "question", "change country from a question asks first")
    c(page.inner_text('#confirmBox [data-go="home!"]').strip() == L["confirmHome"], "confirm button label")
    page.click('#confirmBox [data-go="home!"]')
    wait_view(page, "map")
    c(page.evaluate("[Object.keys(state.answers).length, state.ac]") == [0, None], "confirmed change of country erases")
    S.close(c)


@test
def star_and_guard(c):
    """★ « Compte double pour moi » : au-dessus des réponses, lié à la question affichée, sans avance automatique ;
    tapotement trop rapide après l'affichage ignoré (pas le clavier)."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    L = strings(page, "en")
    ng_start(page)
    c(page.inner_text(".star").replace("★", "").strip() == L["double"] and "★" in page.inner_text(".star"), "★ label")
    above = page.evaluate("document.querySelector('.star').getBoundingClientRect().bottom <= document.querySelector('.answers').getBoundingClientRect().top")
    c(above, "★ above the answers")
    q0 = page.evaluate("state.order[0]")
    c(page.get_attribute(".star", "data-dbl") == str(q0) and page.get_attribute(".star", "aria-pressed") == "false", "★ bound to the displayed question")
    page.click(".star")
    page.wait_for_timeout(500)
    c(page.evaluate("[state.view, state.i, state.double[state.order[0]] === true]") == ["question", 0, True], "★ does not advance")
    page.click(".star")
    c(page.evaluate("Object.keys(state.double).length") == 0 and page.get_attribute(".star", "aria-pressed") == "false", "★ toggles off")
    page.click(".star")
    answer_one(page, 1)
    q1 = page.evaluate("state.order[1]")
    c(page.get_attribute(".star", "aria-pressed") == "false" and page.get_attribute(".star", "data-dbl") == str(q1), "next question: ★ off")
    # Réponse puis ★ pendant l'avance automatique : le ★ touché est celui de la question affichée
    page.click('.answers .ans[data-val="2"]')
    page.evaluate(f"document.querySelector('.star[data-dbl=\"{q1}\"]') && document.querySelector('.star').click()")
    page.wait_for_function("() => state.i === 2")
    c(page.evaluate(f"Object.keys(state.double).map(Number).sort((a, b) => a - b).join()") == ",".join(str(x) for x in sorted([q0, q1])), "★ never lands on the next question")
    # Double tapotement : un tapotement juste après l'affichage est ignoré ; le clavier ne l'est pas
    page.evaluate("TAP_GUARD = 350; qShownAt = now()")
    page.click('.answers .ans[data-val="-1"]')
    q2 = page.evaluate("state.order[2]")
    c(page.evaluate(f"state.answers[{q2}] === undefined && state.i === 2"), "tap right after the question appears is ignored")
    page.wait_for_timeout(400)
    page.click('.answers .ans[data-val="-1"]')
    page.wait_for_function("() => state.i === 3")
    c(page.evaluate(f"state.answers[{q2}]") == -1, "tap after 350 ms counts")
    page.evaluate("qShownAt = now()")
    page.focus('.answers .ans[data-val="0"]')
    page.keyboard.press("Enter")
    page.wait_for_function("() => state.i === 4")
    c(page.evaluate("state.answers[state.order[3]]") == 0, "keyboard answers are not throttled")
    no_overflow(page, c, "question 390")
    S.close(c)


def set_answers(page, answers, prios=()):
    page.evaluate("""([ans, prios]) => { state.priorities = prios; buildOrder(); state.answers = ans; state.double = {};
        state.i = 0; state.tab = 0; state.ret = null; go('results'); }""", [{str(k): v for k, v in answers.items()}, list(prios)])
    wait_view(page, "results")


def expected_title(page, lang, D, answers):
    """Titre attendu d'après les règles de lecture (premier aperçu < 8 réponses, aucun parti proche < 50 %, égalité < 3 points)."""
    rows, a = model_rows(D, answers, {}, [])
    ok = [r for r in rows if r["grp"] == 0]
    thin = [r for r in rows if r["grp"] == 1]
    tr = lambda f, *args: page.evaluate("([l, f, a]) => typeof T[l][f] === 'function' ? T[l][f](...a) : T[l][f]", [lang, f, list(args)])
    if not ok:
        return tr("resThin" if thin else "resNone"), "thin" if thin else "none"
    lead = lead_group(rows)
    if len(lead) > 1:
        who = page.evaluate("([l, xs]) => new Intl.ListFormat(LANGS.find(x => x.code === l).locale, { style: 'long', type: 'conjunction' }).format(xs)",
                            [lang, [FSI + r["sig"] + PDI for r in lead]])
    else:
        who = FSI + f'{lead[0]["nom"]} ({lead[0]["sig"]})' + PDI
    pct = f'{js_round(ok[0]["s"] * 100)}{" %" if lang == "fr" else "%"}'
    if a < EARLY:
        return tr("resEarly", a, who, len(lead)), "early"
    if ok[0]["s"] < 0.5:
        return tr("resFar", who, pct, len(lead)), "far"
    if len(lead) > 1:
        return tr("resTie", who, pct), "tie"
    return tr("resClosest", who), "closest"


def find_answers(D, want, seed=7, tries=60000):
    """Cherche (au hasard, graine fixe) un jeu de réponses du Nigeria qui produit le cas voulu."""
    R = random.Random(seed)
    n = len(D["ed"]["questions"])
    for _ in range(tries):
        m = R.randint(3, EARLY - 1) if want == "early" else R.randint(EARLY, n)
        ans = {q: R.choice([-2, -1, 0, 1, 2]) for q in R.sample(range(n), m)}
        rows, a = model_rows(D, ans, {}, [])
        ok = [r for r in rows if r["grp"] == 0]
        if not ok:
            continue
        lead = lead_group(rows)
        if want == "early" and a < EARLY:
            return ans
        if want == "tie" and ok[0]["s"] >= 0.5 and len(lead) > 1:
            return ans
        if want == "far" and ok[0]["s"] < 0.5:
            return ans
        if want == "closest" and ok[0]["s"] >= 0.5 and len(lead) == 1:
            return ans
        if want == "equal":  # deux partis à score égal (< 0,005) dont l'ordre de l'édition n'est pas l'ordre alphabétique
            ids = [p["sigle"] for p in D["ed"]["parties"]]
            for x, y in zip(ok, ok[1:]):
                if abs(x["s"] - y["s"]) < EQ and ids.index(x["sig"]) > ids.index(y["sig"]):
                    return ans
    raise AssertionError(f"no Nigeria answer set found for case “{want}”")


@test
def headlines(c):
    """Lecture des résultats (Nigeria, réponses construites) : premier aperçu, égalité « 1= », aucun parti proche,
    scores égaux par ordre alphabétique, partis peu documentés à part, réponses identiques, cartes par sujet, RTL."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html#/ng/en")
    page.wait_for_selector(".theme-grid")
    D = json.load(open(os.path.join(ROOT, "data", "ng.json"), encoding="utf8"))
    L = strings(page, "en")

    def check(case, ans, lang="en"):
        set_answers(page, ans)
        title, kind = expected_title(page, lang, D, ans)
        got = page.inner_text(".res-head h1").strip()
        c(case is None or kind == case, f"{case}: model gives {kind}")
        case = case or kind
        c(got == title, f"{case}: headline “{got}” != “{title}”")
        got_rank = [tuple(r) for r in displayed_ranking(page)]
        exp_rank = expected_ranking(D, ans, {}, [])
        c(got_rank == exp_rank, f"{case}: ranking {got_rank} != {exp_rank}")
        rows, a = model_rows(D, ans, {}, [])
        lead = lead_group(rows)
        pos = page.evaluate("[...document.querySelectorAll('#pan0 ol.rank li')].map(li => li.querySelector('.pos').firstChild.textContent)")
        want_pos = ["1=" if (len(lead) > 1 and k < len(lead)) else str(k + 1) for k in range(len(pos))]
        c(pos == want_pos, f"{case}: positions {pos} != {want_pos}")
        c(page.evaluate("document.title").startswith(got.rstrip(".:").replace(FSI, "").replace(PDI, "")[:60]), f"{case}: document title follows the headline")
        return got

    early = find_answers(D, "early")
    check("early", early)
    c(page.is_visible('.res-head .early [data-go="continue"]'), "early: invitation to keep answering")
    c(page.inner_text(".res-head .early p").strip() == page.evaluate(f"T.en.earlyText({EARLY})"), "early: invitation text")
    page.click('.res-head [data-go="continue"]')
    wait_view(page, "question")
    c(page.evaluate("state.answers[state.order[state.i]] === undefined"), "continue → first open question")
    page.go_back()
    wait_view(page, "results")
    check("tie", find_answers(D, "tie"))
    shot(page, "ng-tie-390.png", full=True)
    check("far", find_answers(D, "far"))
    check("closest", find_answers(D, "closest"))
    check(None, find_answers(D, "equal", seed=11))  # ordre alphabétique à score égal (classement attendu)
    # Toutes les réponses « tout à fait d'accord » : APM (9 questions documentées sur 38, toutes positives) ne gagne plus
    allyes = {i: 2 for i in range(len(D["ed"]["questions"]))}
    set_answers(page, allyes)
    rows, a = model_rows(D, allyes, {}, [])
    title = page.inner_text(".res-head h1")
    c("APM" not in title and "Allied Peoples Movement" not in title, f"all agree: APM not in the headline “{title}”")
    c(page.inner_text(".res-head .notice").strip() == L["straight"], "straight-lining notice")
    thin = [r["sig"] for r in rows if r["grp"] == 1]
    c("APM" in thin and page.evaluate("[...document.querySelectorAll('#pan0 li.thin .badge')].map(b => b.textContent)") == thin, f"thin group {thin}")
    c(page.inner_text("#pan0 h2.rank-h").strip() == L["thinTitle"], "thin-group heading")
    # Cartes par sujet : même règle d'égalité, partis peu documentés sur le sujet signalés
    want_thin = sum(1 for th in D["ed"]["themes"] for r in model_rows(D, allyes, {}, [], theme=th["id"])[0] if r["grp"] == 1)
    c(page.locator("#pan1 .mini-row.thin").count() == want_thin, f"issue cards: {want_thin} thinly documented rows flagged")
    c(page.locator(f'#pan1 .mini-row.thin .chip.warn:text-is("{L["partial"]}")').count() == want_thin, "issue cards: partial chips")
    for k, th in enumerate(D["ed"]["themes"]):
        trows = model_rows(D, allyes, {}, [], theme=th["id"])[0]
        tok = [r for r in trows if r["grp"] == 0]
        tlead = [r for r in tok if tok[0]["s"] - r["s"] < TIE] if tok else []
        card = page.evaluate(f"[...document.querySelectorAll('#pan1 .theme-card')].find(a => a.querySelector('h3').textContent === ed().themes[{k}].name).querySelector('.verdict-line').textContent")
        if len(tlead) > 1:
            c(all(r["nom"] in card for r in tlead) and "tied" in card, f"issue {th['id']}: tie listed ({card[:80]})")
        elif tlead:
            c(f'{tlead[0]["nom"]} ({tlead[0]["sig"]})' in card, f"issue {th['id']}: closest {tlead[0]['sig']} ({card[:80]})")
    # Méthode : les règles de lecture
    c(page.locator("#pan3 .rules li").count() == len(page.evaluate("T.en.mRules")), "method: reading rules")
    # Arabe : « Nom (SIGLE) » isolé en entier dans le titre
    far = find_answers(D, "far")
    page.click('#langs [data-lang="ar"]')
    set_answers(page, far)
    title, kind = expected_title(page, "ar", D, far)
    got = page.evaluate("document.querySelector('.res-head h1').textContent")
    c(got == title, f"ar far headline “{got}” != “{title}”")
    rows, _ = model_rows(D, far, {}, [])
    lead = lead_group(rows)
    if len(lead) == 1:
        c(FSI + f'{lead[0]["nom"]} ({lead[0]["sig"]})' + PDI in got, "ar: whole “Name (SIG)” isolated")
    shot(page, "ng-ar-far-390.png", full=True)
    no_overflow(page, c, "ar results 390")
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
