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
        page.click(f'#mapWrap .mk[data-place="{a3}"]')
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
        if view == "valintro":   # invitation facultative aux 10 questions sur les valeurs : on passe aux résultats
            page.click('[data-go="vresults"]')
            wait_view(page, "results")
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
    c(page.locator("#langs button:not([aria-disabled=true])").count() == 5, f"ng-{lang}: 5 languages offered")
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


def late_syntax(code):
    """Cherche dans un script la syntaxe plus récente qu'ES2019 (« ?? », « ?. », « ||= », « &&= », séparateurs de chiffres,
    BigInt, champs privés). Les chaînes, commentaires, expressions régulières et textes de gabarits sont ignorés."""
    hits, n, i, line, depth, prev, tpl = [], len(code), 0, 1, 0, "", []
    regex_after = "(,=:[!&|?{};+-*%<>~^"
    kw = re.compile(r"(?:^|[^\w$])(?:return|typeof|case|in|of|else|do|void|delete|throw|new)$")
    while i < n:
        ch, nx = code[i], code[i + 1] if i + 1 < n else ""
        if ch == "\n":
            line += 1; i += 1; continue
        if ch == "/" and nx == "/":
            while i < n and code[i] != "\n": i += 1
            continue
        if ch == "/" and nx == "*":
            i += 2
            while i < n and not (code[i] == "*" and code[i + 1:i + 2] == "/"):
                if code[i] == "\n": line += 1
                i += 1
            i += 2; continue
        if ch in "\"'":
            i += 1
            while i < n and code[i] != ch:
                if code[i] == "\\": i += 1
                i += 1
            i += 1; prev = "a"; continue
        if ch == "`" or (ch == "}" and tpl and tpl[-1] == depth - 1):
            if ch == "}":
                tpl.pop(); depth -= 1
            i += 1
            while i < n:
                if code[i] == "\\": i += 2; continue
                if code[i] == "\n": line += 1
                if code[i] == "`": i += 1; prev = "a"; break
                if code[i] == "$" and code[i + 1:i + 2] == "{":
                    tpl.append(depth); depth += 1; i += 2; prev = "{"; break
                i += 1
            continue
        if ch == "/" and (prev == "" or prev in regex_after or kw.search(code[max(0, i - 8):i].rstrip())):
            i += 1; cls = False
            while i < n and (cls or code[i] != "/") and code[i] != "\n":
                if code[i] == "\\": i += 1
                elif code[i] == "[": cls = True
                elif code[i] == "]": cls = False
                i += 1
            i += 1
            while i < n and code[i].isalpha(): i += 1
            prev = "a"; continue
        three = code[i:i + 3]
        if ch == "?" and nx == "?": hits.append(f"line {line}: ??")
        elif ch == "?" and nx == "." and not code[i + 2:i + 3].isdigit(): hits.append(f"line {line}: ?.")
        elif three in ("||=", "&&=") : hits.append(f"line {line}: {three}")
        elif ch == "#" and re.match(r"#[A-Za-z_]", code[i:i + 2]) and prev != "a": hits.append(f"line {line}: #private")
        elif ch.isdigit() and not (prev == "a" and re.match(r"\w", code[i - 1:i])):
            m = re.match(r"\d[\d_]*n?\b|0[xX][\da-fA-F_]+n?", code[i:])
            if m and ("_" in m.group(0) or m.group(0).endswith("n")): hits.append(f"line {line}: number {m.group(0)}")
        if ch == "{": depth += 1
        elif ch == "}": depth -= 1
        if not ch.isspace(): prev = "a" if re.match(r"[A-Za-z0-9_$)\]]", ch) else ch
        i += 1
    return hits


def find_acorn():
    for cand in ("acorn", "/opt/npm-tools/node_modules/acorn", "/opt/node-tools/node_modules/acorn"):
        r = subprocess.run(["node", "-e", f"console.log(require.resolve({json.dumps(cand)}))"], capture_output=True, text=True)
        if r.returncode == 0:
            return cand
    return None



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
    c(len(idx.encode()) < 350_000, f"index.html small ({len(idx.encode())} bytes)")
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
    # JavaScript livré : rien de plus récent qu'ES2019 (anciens navigateurs de téléphone), vérifié deux fois
    for name, html in (("index.html", idx), ("artifact.html", art)):
        code = "\n".join(re.findall(r"<script>(.*?)</script>", html, re.S))
        c(len(code) > 100_000, f"{name}: script found ({len(code)} characters)")
        c(not late_syntax(code), f"{name}: no syntax newer than ES2019 {late_syntax(code)[:3]}")
    # le détecteur lui-même : il voit « ?? » et « ?. », pas ceux des chaînes, commentaires, expressions régulières ou gabarits
    c(len(late_syntax("const a = b ?? c; const d = e?.f; g ||= 1;")) == 3, "scanner sees ??, ?. and ||=")
    c(not late_syntax("const a = '?? ?.'; // x ?? y\nconst r = /a??b/; const t = `${a ? .5 : 1} ?? ${b}`; const u = a ? .5 : 1;"), "scanner ignores strings, comments, regexes, templates and `a ? .5`")
    acorn = find_acorn()
    if acorn:
        code = "\n".join(re.findall(r"<script>(.*?)</script>", idx, re.S))
        r = subprocess.run(["node", "-e", f"const a=require({json.dumps(acorn)});a.parse(require('fs').readFileSync(0,'utf8'),{{ecmaVersion:2019,sourceType:'script'}});console.log('ok')"],
                           input=code, capture_output=True, text=True)
        c(r.returncode == 0 and "ok" in r.stdout, f"index.html parses as ES2019 (acorn): {r.stderr.strip()[:200]}")
        NOTES.append("bundle parses as ES2019 with acorn")
    else:
        NOTES.append("acorn not found: ES2019 parse check skipped (the built-in scanner ran)")
    c("color-mix" not in idx, "no color-mix() left in the page")
    # sans JavaScript : une phrase et la liste des pays qui ont un questionnaire ou une fiche, générée par le build
    m = re.search(r'<main id="app"><noscript>(.*?)</noscript></main>', idx, re.S)
    c(bool(m), "<noscript> block inside <main id=app>")
    ns = m.group(1) if m else ""
    c("JavaScript" in ns and ns.count("<li>") == len(cat), f"noscript lists the {len(cat)} countries with a questionnaire or an information page ({ns.count('<li>')})")
    for name in ("Nigeria", "Kenya", "Angola", "The Gambia"):
        c(name in ns, f"noscript names {name}")
    c(all(f'lang="{l}"' in ns for l in LANGS), "noscript sentence in the five languages")
    c("<noscript>" in art and "JavaScript" in art, "artifact.html has the noscript block too")
    # le build ne signale rien (calendrier cohérent avec les éditions, sources présentes, syntaxe) : --strict échoue au moindre avertissement
    tmp2 = tempfile.mkdtemp(prefix="etv-strict-")
    try:
        r = subprocess.run(["node", os.path.join(ROOT, "tools", "build.js"), "--strict", "--out", tmp2], capture_output=True, text=True, timeout=180)
        c(r.returncode == 0 and "WARN" not in r.stdout + r.stderr, f"build --strict passes without warnings: {(r.stdout + r.stderr)[-300:] if r.returncode else ''}")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)
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
    repo_data = sorted(os.listdir(os.path.join(ROOT, "data")))
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
    c(re.search(r"cg: africa\.js election dates differ from META\.ev", out), "build warns when an AFRICA row and the edition's dates disagree")
    c(re.search(r"km: africa\.js says up:false but META\.ev falls between", out), "build warns when AFRICA says no election but the edition has one")
    c(re.search(r"bi: validation failed, skipped", out), "bi skipped (validation)")
    c(re.search(r"td: cannot load", out), "td skipped (load error)")
    files = sorted(os.listdir(os.path.join(site, "data")))
    c("cg.json" in files and "km.json" in files and "ng.json" in files, f"fixture data written: {files}")
    c("bi.json" not in files and "td.json" not in files, "invalid editions not written")
    cg = json.load(open(os.path.join(site, "data", "cg.json"), encoding="utf8"))
    c(cg["a3"] == "178" and cg["langs"] == ["en", "fr"] and list(cg["i18n"]) == ["fr"], "cg.json langs and i18n")
    c(sorted(os.listdir(os.path.join(ROOT, "data"))) == repo_data, "repo data/ untouched")
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
               ngPin: [...document.querySelectorAll('#mapWrap .mk')].filter(g => g.querySelector('.pin')).map(g => [+g.dataset.x, +g.dataset.y]),
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
    c(page.locator("#langBody .lang-btn:not([aria-disabled=true])").count() == 5, "Nigeria: 5 languages enabled")
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
    c(page.locator("#langBody .lang-btn[aria-disabled=true]").count() == 0, "no-data country: every language enabled")
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
    c([b.strip() for b in page.locator("#langs button:not([aria-disabled=true])").all_inner_texts()] == ["FR"], "only French enabled")
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
    pos = page.evaluate("""() => { const g = document.querySelector('#mapWrap .mk[data-place="174"]');
        return { isl: MAP.isl['174'], at: g ? [+g.dataset.x, +g.dataset.y] : null, info: !!(g && g.querySelector('.pin-info')),
                 up: document.querySelector('.isl[data-place="174"]').classList.contains('up'), status: statusLine('174') } }""")
    c(pos["info"] and pos["isl"] == pos["at"], "info marker anchored on the Comoros island coordinates")
    c(pos["up"], "Comoros coloured from META (election by end 2027)")
    page.click('#mapWrap .mk[data-place="174"]')
    page.wait_for_selector("#langDlg[open]")
    c(page.evaluate("state.ui") == "en", "interface starts in the browser language (en-GB → en)")
    Lui = strings(page, "en")  # langue de l'interface pendant le choix
    enabled = page.evaluate("[...document.querySelectorAll('#langBody .lang-btn')].filter(b => b.getAttribute('aria-disabled') !== 'true').map(b => b.dataset.pick).sort()")
    c(enabled == ["ar", "en"], f"Comoros: ar + en enabled ({enabled})")
    c(page.locator(f'#langBody .lang-btn[aria-disabled=true] .lnote:text-is("{Lui["langNoInfo"]}")').count() == 3, "disabled languages carry a note")
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
    c(sorted(b.strip() for b in page.locator("#langs button:not([aria-disabled=true])").all_inner_texts()) == ["AR", "EN"], "header offers ar + en only")
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
    c(page.locator('#langs button[data-lang="pt"][aria-disabled=true]').count() == 1, "dropped language disabled in header")
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
    offered = sorted(b.strip().lower() for b in page.locator("#langs button:not([aria-disabled=true])").all_inner_texts())
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
            enabled = page.evaluate("[...document.querySelectorAll('#langBody .lang-btn')].filter(b => b.getAttribute('aria-disabled') !== 'true').map(b => b.dataset.pick).sort()")
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
        c(page.text_content("#langBody .cb-name").strip() == page.evaluate(f"cname('{cat['ke']['a3']}')"), "#ke: language choice for Kenya")
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
        card = page.evaluate(f"[...document.querySelectorAll('#pan1 .theme-card')].find(a => a.querySelector('h2').textContent === ed().themes[{k}].name).querySelector('.verdict-line').textContent")
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


# ------------------------------------------------------------------ cibles tactiles, clavier, petit téléphone, 320 px, couleurs
NOTES = []   # mesures du pire cas, imprimées à la fin (pas des vérifications)


def lab_of(hexcol):
    """CIE76 : couleur #rrggbb → (L, a, b), calculé ici indépendamment de l'application."""
    h = hexcol.lstrip("#")
    lin = lambda v: (v / 255 / 12.92) if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    x, y, z = f((0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047), f(0.2126 * r + 0.7152 * g + 0.0722 * b), f((0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883)
    return (116 * y - 16, 500 * (x - y), 200 * (y - z))


def lum_of(hexcol):
    h = hexcol.lstrip("#")
    lin = lambda v: (v / 255 / 12.92) if v / 255 <= 0.03928 else ((v / 255 + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_of(a, b):
    x, y = lum_of(a), lum_of(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


@test
def map_targets(c):
    """Chaque repère de la carte est une vraie cible : zone tactile de 24 px au moins, le point au centre du repère
    retombe sur son propre pays (Gambie / Guinée-Bissau / Sénégal / Cap-Vert écartés, avec un trait), à 320, 390 et 1280 px."""
    for w, h in ((320, 700), (390, 844), (1280, 900)):
        S = Session(CTX["browser"], width=w, height=h)
        page = S.page
        page.goto(CTX["base"] + "/index.html")
        page.wait_for_selector("#mapWrap .mk")
        page.wait_for_timeout(200)   # ResizeObserver : mise en place des repères
        no_overflow(page, c, f"map {w}")
        n_ids = page.evaluate("markerIds().length")
        res = page.evaluate("""() => {
          const out = [];
          for (const g of document.querySelectorAll('#mapWrap .mk')) {
            g.scrollIntoView({ block: 'center', inline: 'center' });
            const hit = g.querySelector('.mk-hit').getBoundingClientRect();
            const cx = hit.left + hit.width / 2, cy = hit.top + hit.height / 2;
            const el = document.elementFromPoint(cx, cy);
            const own = el && el.closest('[data-place]');
            out.push({ id: g.dataset.place, d: hit.width, got: own ? own.dataset.place : null, onHit: !!(el && el.closest('.mk') && el.closest('.mk') === g), ax: g.getBoundingClientRect().left + scrollX, ay: g.getBoundingClientRect().top + scrollY });
          }
          return out;
        }""")
        c(len(res) == n_ids and n_ids >= 20, f"{w}: every marker drawn ({len(res)})")
        bad = [r["id"] for r in res if r["got"] != r["id"]]
        c(not bad, f"{w}: the centre of each marker resolves to its own country, not {bad[:5]}")
        c(all(r["onHit"] for r in res), f"{w}: the point at the centre belongs to the marker itself")
        small = [(r["id"], round(r["d"], 1)) for r in res if r["d"] < 23.9]
        c(not small, f"{w}: hit circle >= 24 px: {small[:4]}")
        NOTES.append(f"map {w}px: smallest hit circle {min(r['d'] for r in res):.1f} px over {len(res)} markers")
        # deux repères ne se recouvrent jamais (leurs cercles de 24 px restent disjoints)
        pts = page.evaluate("[...document.querySelectorAll('#mapWrap .mk-hit')].map(e => { const r = e.getBoundingClientRect(); return [r.left + scrollX + r.width / 2, r.top + scrollY + r.height / 2, r.width]; })")
        tooclose = [(i, j) for i in range(len(pts)) for j in range(i + 1, len(pts)) if math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]) < 0.97 * (pts[i][2] + pts[j][2]) / 2]
        c(not tooclose, f"{w}: no two hit circles overlap ({len(tooclose)})")
        if w == 320:
            c(page.locator("#mapWrap .leads .lead").count() >= 1, "320: displaced markers are tied to their country by a leader line")
        # un vrai toucher au centre du repère de la Gambie (et de ses voisins) ouvre ce pays
        for a2 in ("gm", "gw", "sn", "cv"):
            a3 = page.evaluate(f"Object.keys(AFRICA).find(id => AFRICA[id].a2 === '{a2.upper()}')")
            if not page.evaluate(f"!!document.querySelector('#mapWrap .mk[data-place=\"{a3}\"]')"):
                continue
            page.evaluate(f"document.querySelector('#mapWrap .mk[data-place=\"{a3}\"]').scrollIntoView({{ block: 'center', inline: 'center' }})")
            box = page.locator(f'#mapWrap .mk[data-place="{a3}"] .mk-hit').bounding_box()
            page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            page.wait_for_function("() => document.getElementById('langDlg').open")
            c(page.evaluate("state.pending") == a3 and page.evaluate("location.hash") == f"#/{a2}", f"{w}: a tap on {a2.upper()} opens {a2.upper()}")
            page.click("#langCancel")
            page.wait_for_function("() => !document.getElementById('langDlg').open")
        S.close(c)


@test
def map_keyboard(c):
    """Clavier sur la carte : le premier arrêt est le lien « Aller à la liste des pays » (visible au focus) ; dans la carte,
    seuls les pays avec une élection ou un contenu sont dans l'ordre de tabulation, classés par nom ; la légende montre le ✓."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap .mk")
    page.keyboard.press("Tab")
    c(page.evaluate("document.activeElement.id") == "skip", "first Tab stop is the skip link")
    box = page.locator("#skip").bounding_box()
    c(box and box["y"] >= 0 and box["y"] + box["height"] <= 844 and box["x"] >= 0, "skip link visible on focus")
    c(page.inner_text("#skip").strip() == page.evaluate("T.en.skipList") == "Skip to the list of countries", "skip link text")
    page.keyboard.press("Enter")
    c(page.evaluate("document.getElementById('listBox').open") and page.evaluate("document.activeElement.id") == "csearch", "skip link opens the list and focuses its search")
    # ordre de tabulation dans le SVG
    info = page.evaluate("""() => {
      const els = [...document.querySelectorAll('#mapWrap svg [data-place]')].filter(e => !e.classList.contains('mk') && !e.closest('.mk'));
      const tab0 = els.filter(e => e.getAttribute('tabindex') === '0').map(e => e.dataset.place);
      const rest = els.filter(e => e.getAttribute('tabindex') !== '0');
      return { tab0, restBad: rest.filter(e => e.getAttribute('tabindex') !== '-1').length,
               want: Object.keys(AFRICA).filter(id => isUp(id) || catFor(id)).length,
               names: tab0.map(cname), sorted: tab0.map(cname).slice().sort((a, b) => a.localeCompare(b, locale())),
               mkTab: [...document.querySelectorAll('#mapWrap .mk')].filter(g => g.hasAttribute('tabindex') || g.getAttribute('aria-hidden') !== 'true').length };
    }""")
    c(len(info["tab0"]) == info["want"] and info["want"] >= 10, f"only countries with an election or content are tab stops ({len(info['tab0'])})")
    c(info["restBad"] == 0, "every other country has tabindex -1")
    c(info["names"] == info["sorted"], "tab order follows the localised names")
    c(info["mkTab"] == 0, "markers are not tab stops (hidden from assistive technology)")
    # vraie tabulation : depuis le lien d'évitement jusqu'à la carte, puis dans l'ordre
    page.evaluate("document.getElementById('skip').focus()")
    seen = []
    for _ in range(60):
        page.keyboard.press("Tab")
        got = page.evaluate("(() => { const e = document.activeElement; return e && e.closest('#mapWrap') && e.dataset ? e.dataset.place : null; })()")
        if got:
            seen.append(got)
            if len(seen) == 4:
                break
    c(seen == info["tab0"][:4], f"Tab walks the map in name order: {seen}")
    c(page.locator("#mapWrap .fring .fr-ink").count() == 1 and page.locator("#mapWrap .fring .fr-halo").count() == 1, "two-tone focus ring on the focused country")
    c(page.is_visible("#tip"), "tooltip follows keyboard focus")
    c(heading_ok(heading_levels(page)), f"heading order on the map screen {heading_levels(page)}")
    # légende : l'anneau « questionnaire disponible » porte son ✓
    c(page.locator(".legend .pin-key .pin").count() == 1 and page.locator(".legend .pin-key .pin-check").count() == 1, "legend ring shows the check mark")
    S.close(c)


def q_metrics_js():
    return """() => {
      const out = [];
      for (let k = 0; k < state.order.length; k++) {
        state.i = k; viewQuestion();
        const a = [...document.querySelectorAll('.ans')], top = document.querySelector('.q-top').getBoundingClientRect().top;
        out.push({ k, bottom: a[a.length - 1].getBoundingClientRect().bottom, visible: a.filter(x => x.getBoundingClientRect().bottom <= innerHeight && x.getBoundingClientRect().top >= 0).length,
                   need: a[a.length - 1].getBoundingClientRect().bottom - top, sw: document.documentElement.scrollWidth, vh: innerHeight });
      }
      return out;
    }"""


@test
def question_screen(c):
    """Écran de question d'une main : 360 × 640, les cinq réponses visibles pour toutes les questions du Nigeria et du Kenya
    (en et sw) ; progression en barre fine + « 12 / 38 » + liste des questions ; libellé du milieu explicite."""
    worst = {}
    for cc in ("ng", "ke"):
        for lang in ("en", "sw"):
            S = Session(CTX["browser"], width=360, height=640)
            page = S.page
            page.goto(CTX["base"] + f"/index.html#/{cc}/{lang}")
            page.wait_for_selector(".theme-grid")
            page.click(".theme-grid [data-prio]")
            page.click('[data-go="startq"]')
            wait_view(page, "question")
            res = page.evaluate(q_metrics_js())
            n = page.evaluate("state.order.length")
            c(len(res) == n, f"{cc}-{lang}: measured all {n} questions")
            c(all(r["visible"] == 5 for r in res), f"{cc}-{lang}: five answers visible on every question (min {min(r['visible'] for r in res)})")
            c(all(r["bottom"] <= r["vh"] for r in res), f"{cc}-{lang}: last answer ends inside the viewport (max {max(r['bottom'] for r in res):.0f} of 640)")
            c(all(r["sw"] <= 360 for r in res), f"{cc}-{lang}: no horizontal overflow on any question")
            w = max(res, key=lambda r: r["need"])
            worst[f"{cc}-{lang}"] = (w["need"], w["k"] + 1)
            S.close(c)
    NOTES.append("question screen 360x640: worst header-to-last-answer height " + ", ".join(f"{k} {v[0]:.0f}px (q{v[1]})" for k, v in sorted(worst.items())) + " of 640; all 5 answers visible in every case")
    # la mécanique de l'écran, en anglais sur Nigeria
    S = Session(CTX["browser"], width=360, height=640)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    open_country(page, "566", "en")
    page.wait_for_selector(".theme-grid")
    # bouton Commencer désactivé : la raison est écrite
    c(page.locator('[data-go="startq"]').is_disabled(), "Start disabled before any issue is chosen")
    c(page.inner_text("#goHint").strip() == page.evaluate("T.en.startHint") == "Choose at least one issue", "disabled Start explains why")
    page.click(".theme-grid [data-prio]")
    c(page.inner_text("#goHint").strip() != "Choose at least one issue" and page.locator('[data-go="startq"]').is_enabled(), "hint gone once an issue is chosen")
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    page.evaluate("TAP_GUARD = 0")
    n = page.evaluate("state.order.length")
    c(page.is_hidden("#steps"), "step pills hidden on question screens")
    c(page.inner_text(".q-count").strip() == f"1 / {n}", f"global count “1 / {n}”")
    pb = page.evaluate("(() => { const b = document.querySelector('.qbar'); return [b.getAttribute('role'), b.getAttribute('aria-valuenow'), b.getAttribute('aria-valuemax'), b.querySelectorAll('.tick').length]; })()")
    c(pb == ["progressbar", "1", str(n), 1], f"progress bar semantics {pb}")
    c(page.locator(".q-meta .chip").count() == 1, "block chip stays")
    c(page.locator(".slip details .q-min").count() == 1 and page.locator(".q-min").count() == 1, "ministries live inside Background")
    c(page.locator(".answers .ans").count() == 5 and not page.locator("details[open]").count(), "five answers, Background closed")
    mid = page.inner_text('.ans[data-val="0"]').strip()
    c(mid == "Neither agree nor disagree", f"middle answer label “{mid}”")
    for lang, want in (("fr", "Ni d’accord ni pas d’accord"), ("pt", "Nem concordo nem discordo"), ("sw", "Sikubali wala sikatai"), ("ar", "لا أوافق ولا أعارض")):
        got = page.evaluate(f"T.{lang}.ans[0]")
        c(got.replace("'", "’") == want, f"{lang}: middle label “{got}”")
    short = page.evaluate("T.en.ansShort")
    c(short["0"] != "Neutral" and all(short[k] for k in short), f"By-question labels stay meaningful {short}")
    c(page.evaluate("getComputedStyle(document.documentElement).scrollPaddingBottom") == "120px", "html scroll-padding-bottom")
    # liste des questions : lignes de 44 px, état écrit
    answer_one(page, 2)
    page.click('[data-val="skip"]')
    page.wait_for_function("() => state.i === 2")
    page.click(".qlist-btn")
    page.wait_for_selector("#qDlg[open]")
    rows = page.evaluate("[...document.querySelectorAll('#qDlg .qrow')].map(r => [r.getBoundingClientRect().height, r.className, r.getAttribute('aria-current')])")
    c(len(rows) == n and min(r[0] for r in rows) >= 44, f"jump list: {len(rows)} rows, min height {min(r[0] for r in rows):.0f}")
    c("done" in rows[0][1] and "skip" in rows[1][1] and "cur" in rows[2][1] and rows[2][2] == "step", "jump list: answered / skipped / current states")
    c("Answered" in page.inner_text("#qDlg .qrow.done") or "✓" in page.inner_text("#qDlg .qrow.done"), "jump list: state written out")
    page.keyboard.press("Tab")
    page.keyboard.press("Shift+Tab")
    cur = page.evaluate("(() => { const e = document.activeElement; const s = getComputedStyle(e); return [e.classList.contains('cur'), s.outlineStyle, s.outlineWidth, s.borderTopColor]; })()")
    c(cur[0] and cur[1] != "none" and cur[2] == "3px", f"the current row keeps its focus ring on top of its own indicator {cur}")
    page.click('#qDlg [data-qjump="6"]')
    page.wait_for_function("() => state.i === 6 && !document.getElementById('qDlg').open")
    c(page.inner_text(".q-count").strip() == f"7 / {n}", "jump list jumps (7 / n)")
    S.close(c)
    # petit écran en hauteur : après une réponse, la carte de la question reste en haut de l'écran
    S = Session(CTX["browser"], width=360, height=480)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    ng_start(page, "en")
    page.click('.answers .ans[data-val="1"]')
    page.wait_for_function("() => state.i === 1")
    top = page.evaluate("document.querySelector('.q-top').getBoundingClientRect().top")
    c(-1 <= top <= 120, f"after auto-advance the question card stays in view (top {top:.0f})")
    S.close(c)
    # animation d'entrée : seulement quand l'écran change vraiment, et jamais avec « réduire les animations »
    S = Session(CTX["browser"], width=390, height=844, motion="no-preference")
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    ng_start(page, "en")
    c(page.evaluate("document.querySelector('#app > section').classList.contains('enter')"), "entrance animation on a real screen change")
    c(page.evaluate("getComputedStyle(document.querySelector('#app > section')).animationName") != "none", "animation runs with no-preference")
    page.click('.answers .ans[data-val="1"]')
    page.wait_for_function("() => state.i === 1")
    c(not page.evaluate("document.querySelector('#app > section').classList.contains('enter')"), "no entrance animation from one question to the next")
    S.close(c)
    S = Session(CTX["browser"], width=390, height=844, motion="reduce")
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    ng_start(page, "en")
    c(page.evaluate("getComputedStyle(document.querySelector('#app > section')).animationName") == "none", "no animation with prefers-reduced-motion")
    S.close(c)


def heading_levels(page, root="#app"):
    return page.evaluate("r => [...document.querySelectorAll(r + ' h1, ' + r + ' h2, ' + r + ' h3, ' + r + ' h4')].filter(h => h.offsetParent !== null).map(h => +h.tagName[1])", root)


def heading_ok(levels):
    """Un seul h1 en tête, et jamais de saut de niveau vers le bas (h1 → h3)."""
    return bool(levels) and levels[0] == 1 and levels.count(1) == 1 and all(b <= a + 1 for a, b in zip(levels, levels[1:]))


@test
def layout_320(c):
    """Pas de défilement horizontal à 320 px (carte, départ, question, les quatre onglets des résultats) pour le Nigeria,
    le Kenya et le Cameroun, en anglais et en arabe ; onglets de résultats tous visibles à 390 px ; l'échelle « Par question »
    tient sans défilement."""
    cat = CTX["catalog"]
    for cc in ("ng", "ke", "cm"):
        langs = [l for l in ("en", "ar") if l in cat[cc]["langs"]]
        for lang in langs:
            for width in (320, 390):
                S = Session(CTX["browser"], width=width, height=700)
                page = S.page
                w = f"{cc}-{lang}-{width}"
                page.goto(CTX["base"] + "/index.html")
                page.wait_for_selector("#mapWrap svg")
                page.click(f'#langs [data-lang="{lang}"]')
                page.wait_for_function("l => state.ui === l", arg=lang)
                no_overflow(page, c, f"{w} map")
                open_country(page, cat[cc]["a3"], lang)
                page.wait_for_selector(".theme-grid")
                no_overflow(page, c, f"{w} start")
                if width == 390:
                    c(heading_ok(heading_levels(page)), f"{w}: heading order on the start screen {heading_levels(page)}")
                page.click(".theme-grid [data-prio]")
                page.click('[data-go="startq"]')
                wait_view(page, "question")
                page.evaluate("TAP_GUARD = 0")
                # la question la plus longue, détail ouvert
                longest = page.evaluate("state.order.map((qi, k) => [k, ed().questions[qi].text.length + ed().questions[qi].ctx.length]).sort((a, b) => b[1] - a[1])[0][0]")
                page.evaluate(f"() => {{ state.i = {longest}; viewQuestion(); }}")
                page.click(".slip summary")
                no_overflow(page, c, f"{w} question")
                if width == 390:
                    c(heading_ok(heading_levels(page)), f"{w}: heading order on the question screen {heading_levels(page)}")
                page.evaluate("() => { ed().questions.forEach((q, i) => { state.answers[i] = (i % 5) - 2; }); go('results'); }")
                wait_view(page, "results")
                if width == 390:
                    tabs = page.evaluate("[...document.querySelectorAll('.tabs .tab')].map(t => { const r = t.getBoundingClientRect(); return [r.left, r.right, r.width, r.height]; })")
                    c(len(tabs) == 4 and all(t[0] >= -0.5 and t[1] <= 390.5 and t[2] > 30 and t[3] > 20 for t in tabs), f"{w}: all four result tabs inside the viewport {[round(t[1]) for t in tabs]}")
                for k in range(4):
                    page.click(f'.tab[data-tab="{k}"]')
                    page.wait_for_function("k => state.tab === k", arg=k)
                    no_overflow(page, c, f"{w} results tab {k}")
                    if width == 390:
                        c(heading_ok(heading_levels(page)), f"{w}: heading order on results tab {k} {heading_levels(page)}")
                        c(page.evaluate("[...document.querySelectorAll('.tab')].filter(t => t.tabIndex === 0).length") == 1, f"{w}: tabs keep a roving tabindex")
                    if k == 3:
                        fm = page.evaluate("[...document.querySelectorAll('.formula')].map(e => e.getAttribute('tabindex'))")
                        c(fm and all(x == "0" for x in fm), f"{w}: scrollable formulas are keyboard-focusable ({len(fm)})")
                    if k == 2:
                        sc = page.evaluate("""[...document.querySelectorAll('.scale')].map(s => [s.scrollWidth, s.clientWidth, getComputedStyle(s).gridTemplateColumns.split(' ').length])""")
                        c(sc and all(a <= b + 1 and n == 5 for a, b, n in sc), f"{w}: By-question scale has five columns and no scroll ({len(sc)} scales)")
                S.close(c)


@test
def theme_wording(c):
    """Cartes « Par sujet » : « tu as passé » quand toutes les questions du sujet ont été passées, « pas encore répondu » sinon."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    ng_start(page, "en")
    page.evaluate("""() => {
      const th = ed().themes.map(t => t.id);
      ed().questions.forEach((q, i) => { state.answers[i] = q.theme === th[0] ? null : q.theme === th[1] ? undefined : (i % 5) - 2; });
      go('results');
    }""")
    wait_view(page, "results")
    page.click('.tab[data-tab="1"]')
    notes = page.evaluate("[...document.querySelectorAll('#pan1 .skipped-note')].map(e => e.textContent.trim())")
    L = page.evaluate("[T.en.themeSkipped, T.en.themeNotAnswered]")
    c(L[0] in notes and L[1] in notes and L[0] != L[1], f"skipped vs not answered wording per theme {notes} / {L}")
    S.close(c)


@test
def search_aliases(c):
    """Recherche de pays : sans accents ni majuscules, avec les noms usuels (Ivory Coast, Cape Verde, Swaziland, Congo-Brazzaville,
    RDC…), dans les noms des cinq langues ; message quand rien ne correspond."""
    S = Session(CTX["browser"], width=1100, height=900)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    page.click("#listBox summary")
    a3 = lambda a2: page.evaluate(f"Object.keys(AFRICA).find(id => AFRICA[id].a2 === '{a2}')")

    def found(term):
        page.fill("#csearch", term)
        return set(page.evaluate("[...document.querySelectorAll('#clist [data-place]')].map(e => e.dataset.place)"))

    ci, cv, sz, cg, cd, gw, gn, sn = (a3(x) for x in ("CI", "CV", "SZ", "CG", "CD", "GW", "GN", "SN"))
    for term, want, notwant in (
        ("Ivory Coast", ci, None), ("cote d'ivoire", ci, None), ("Côte d’Ivoire", ci, None), ("COTE", ci, None), ("cote divoire", ci, None),
        ("Cape Verde", cv, None), ("cabo verde", cv, None), ("Swaziland", sz, None), ("Eswatini", sz, None),
        ("Congo-Brazzaville", cg, cd), ("congo brazzaville", cg, cd), ("Congo-Kinshasa", cd, cg), ("RDC", cd, cg), ("DRC", cd, cg),
        ("Guinée-Bissau", gw, gn), ("guinee bissau", gw, gn), ("Guinea Bissau", gw, gn), ("Sénégal", sn, None), ("SENEGAL", sn, None), ("senegal", sn, None),
    ):
        got = found(term)
        c(want in got, f"search “{term}” finds {AFRICA_NAME(page, want)}")
        c(notwant is None or notwant not in got, f"search “{term}” leaves out {AFRICA_NAME(page, notwant) if notwant else ''}")
    c(found("zzzzqx") == set() and page.inner_text("#clist").strip() == page.evaluate("T.en.noCountry"), "no match: a message, not an empty list")
    c(len(found("")) >= 50, "empty search lists every country")
    # chaque langue : le nom localisé, en majuscules, retrouve le pays
    for lang in LANGS:
        page.click(f'#langs [data-lang="{lang}"]')
        page.wait_for_function("l => state.ui === l", arg=lang)
        if not page.evaluate("document.getElementById('listBox').open"):
            page.click("#listBox summary")
        for cc_id in (ci, sn, cv):
            name = page.evaluate(f"cname('{cc_id}')")
            c(cc_id in found(name) and cc_id in found(name.upper()), f"{lang}: “{name}” found, also in capitals")
    S.close(c)


def AFRICA_NAME(page, id):
    return page.evaluate(f"AFRICA['{id}'].en") if id else ""


@test
def copy_and_states(c):
    """Textes et états : accroche, bandeau « N pays à explorer » calculé, pages d'information (action principale = retour à la
    carte), pied de page, boutons de langue désactivés mais focalisables avec explication, sections ouvertes conservées au
    changement de langue, dates de sources lisibles."""
    cat = CTX["catalog"]
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    n_cat = page.evaluate("Object.values(CATALOG).filter(c => c.a3 && AFRICA[c.a3]).length")
    kicker = page.text_content(".kicker").strip()   # sans la mise en capitales de la feuille de style
    c(kicker == f"Elections in Africa · {n_cat} countries to explore", f"hero kicker computed: “{kicker}”")
    c("54" not in kicker, "hero kicker does not promise 54 countries")
    tag = page.inner_text(".tagline").strip()
    c("We don’t tell you who to vote for" in tag and "No voting advice" not in tag, f"tagline “{tag}”")
    c(page.inner_text(".legend li:nth-child(2)").startswith("No national election before end of 2027"), "legend: no election before end of 2027")
    c(page.evaluate("T.en.footer1") not in page.inner_text("footer"), "no coded-positions sentence in the footer on the map")
    for lang in LANGS:
        c("2027" in page.evaluate(f"T.{lang}.legNone"), f"{lang}: legend wording mentions end of 2027")
    # boutons de langue désactivés : aria-disabled, focalisables, explication visible
    open_country(page, cat["ke"]["a3"], "en")
    page.wait_for_selector(".theme-grid")
    strip = page.locator(".strip a, .strip button")
    if strip.count():
        strip.first.focus()
        st = page.evaluate("(() => { const s = getComputedStyle(document.activeElement); return [s.outlineStyle, s.outlineColor]; })()")
        c(st[0] != "none" and st[1] == "rgb(255, 255, 255)", f"focus ring on the violet strip is the on-accent colour {st}")
    dis = page.locator('#langs button[aria-disabled="true"]')
    c(dis.count() >= 1 and page.locator("#langs button[disabled]").count() == 0, f"unavailable languages are aria-disabled, not disabled ({dis.count()})")
    dis.first.focus()
    c(page.evaluate("document.activeElement.getAttribute('aria-disabled')") == "true", "a disabled language button can be focused")
    c(page.is_visible("#langTip") and page.inner_text("#langTip").strip() == "Not translated yet", "visible explanation on focus")
    before = page.evaluate("state.ui")
    dis.first.click(force=True)
    c(page.evaluate("state.ui") == before, "clicking a disabled language does nothing")
    page.keyboard.press("Escape")
    c(page.is_hidden("#langTip"), "Escape closes the explanation")
    # changement de langue : une section ouverte reste ouverte
    page.evaluate("document.querySelector('.party-list details, details') && (document.querySelector('details').open = true)")
    n_open = page.evaluate("document.querySelectorAll('#app details[open]').length")
    other = [l for l in cat["ke"]["langs"] if l != "en"][0]
    page.click(f'#langs [data-lang="{other}"]')
    page.wait_for_function("l => state.ui === l", arg=other)
    c(n_open >= 1 and page.evaluate("document.querySelectorAll('#app details[open]').length") == n_open, f"open sections stay open when the language changes ({n_open})")
    # pas de date ISO brute dans les sources
    c(not re.search(r"\b20\d\d-\d\d(-\d\d)?\b", page.inner_text("#app")), "source dates are formatted, not raw ISO")
    S.close(c)
    # page d'information : l'action principale ramène à la carte ; la démo Nigeria est un lien secondaire
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    nid = page.evaluate("Object.keys(AFRICA).filter(id => !catFor(id)).sort()[0]")
    open_country(page, nid, "en", from_list=True)
    wait_view(page, "info")
    prim = page.locator(".btn-primary")
    c(prim.count() == 1 and prim.inner_text().strip() == page.evaluate("T.en.backMap"), f"info page: primary action is “{prim.inner_text().strip()}”")
    c(page.locator('[data-go="nigeria"]').evaluate("e => e.classList.contains('link') && !e.classList.contains('btn-primary')"), "info page: Nigeria demo is a secondary link")
    c(page.inner_text("#app").count("No national election") <= 1, "info page: no repeated “no national election” lines")
    c(not re.search(r"\b20\d\d-\d\d(-\d\d)?\b", page.inner_text("#app")), "info page: no raw ISO dates")
    c(page.evaluate("T.en.footer1") not in page.inner_text("footer"), "info page: no coded-positions sentence in the footer")
    S.close(c)
    # pied de page : la phrase sur les positions codées seulement là où l'on voit des positions de partis
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    ng_start(page, "en")
    c(page.evaluate("T.en.footer1") in page.inner_text("footer"), "footer sentence on the questionnaire (party positions shown)")
    S.close(c)


@test
def party_colours(c):
    """Dans chaque édition, deux partis ne se ressemblent jamais (ΔE ≥ 20, thèmes clair et sombre) et le sigle reste lisible
    (4,5:1). Calculé ici de façon indépendante de l'application."""
    S = Session(CTX["browser"], width=1100)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    worst_de, worst_ct, kept = 999, 999, 0
    for cc, e in sorted(CTX["catalog"].items()):
        if e["kind"] != "ed":
            continue
        D = json.load(open(os.path.join(ROOT, "data", cc + ".json"), encoding="utf8"))
        ps = D["ed"]["parties"]
        maps = page.evaluate("ps => partyColours(ps)", ps)
        for k, (name, text) in enumerate((("light", "#FFFFFF"), ("dark", "#110F19"))):
            cols = [maps[k][p["id"]] for p in ps]
            ct = min(contrast_of(x, text) for x in cols)
            de = min([math.dist(lab_of(a), lab_of(b)) for i, a in enumerate(cols) for b in cols[i + 1:]] or [999])
            c(ct >= 4.5, f"{cc} {name}: badge text contrast {ct:.2f} >= 4.5")
            c(de >= 20, f"{cc} {name}: smallest colour distance ΔE {de:.1f} >= 20")
            worst_de, worst_ct = min(worst_de, de), min(worst_ct, ct)
            kept += sum(1 for p, x in zip(ps, cols) if x.lower() == (p["col"][k] if len(p["col"]) > k else p["col"][0]).lower())
    NOTES.append(f"party colours: min ΔE {worst_de:.1f}, min badge text contrast {worst_ct:.2f} over every edition, light and dark")
    S.close(c)
    # les couleurs ajustées sont bien celles de la page (thème sombre)
    S = Session(CTX["browser"], width=1100, scheme="dark")
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    open_country(page, "566", "en")
    page.wait_for_selector(".party-list .badge", state="attached")
    D = json.load(open(os.path.join(ROOT, "data", "ng.json"), encoding="utf8"))
    want = page.evaluate("ps => partyColours(ps)[1]", D["ed"]["parties"])
    got = page.evaluate("getComputedStyle(document.querySelector('.party-list .badge')).backgroundColor")
    c(got == rgb(want[D["ed"]["parties"][0]["id"]]), f"dark badge uses the fitted colour {got}")
    S.close(c)


@test
def contrast_tokens(c):
    """Contrastes des couleurs de la feuille de style (les deux thèmes) : texte 4,5:1, éléments d'interface 3:1."""
    css = open(os.path.join(ROOT, "src", "shell.html"), encoding="utf8").read()

    def tokens(block):
        return {m.group(1): m.group(2).strip() for m in re.finditer(r"--([a-z0-9-]+):\s*([^;]+);", block)}

    light = tokens(css[css.index(":root {"):css.index("@media (prefers-color-scheme: dark)")])
    dark = dict(light)
    dark.update(tokens(css[css.index(':root[data-theme="dark"]'):css.index("html { scroll-padding")]))

    def parse(v):
        v = v.strip()
        m = re.match(r"#([0-9a-fA-F]{6})$", v)
        if m:
            return [int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)], 1.0
        m = re.match(r"rgba\(([^)]+)\)", v)
        p = [float(x) for x in m.group(1).split(",")]
        return p[:3], p[3]

    def col(T, k, over=None):
        rgbv, a = parse(T[k])
        if a < 1:
            b = col(T, over) if over else [255, 255, 255]
            return [round(x * a + y * (1 - a)) for x, y in zip(rgbv, b)]
        return rgbv

    def lum(rgbv):
        f = lambda x: x / 255 / 12.92 if x / 255 <= 0.03928 else ((x / 255 + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(rgbv[0]) + 0.7152 * f(rgbv[1]) + 0.0722 * f(rgbv[2])

    def ratio(a, b):
        x, y = lum(a), lum(b)
        return (max(x, y) + 0.05) / (min(x, y) + 0.05)

    text = [("ink", "paper"), ("ink", "sheet"), ("muted", "paper"), ("muted", "sheet"), ("muted", "sheet-2"), ("accent-ink", "paper"), ("accent-ink", "sheet"),
            ("accent-ink", "accent-soft"), ("on-accent", "accent"), ("on-accent", "accent-ink"), ("paper", "ink"), ("ink", "lamp-soft"), ("on-lamp", "lamp"),
            ("warn", "warn-soft"), ("warn", "lamp-soft"), ("check", "check-soft"), ("muted", "accent-soft")]
    ui = [("ctl", "sheet"), ("ctl", "paper"), ("ctl", "sheet-2"), ("ctl", "accent-soft"), ("accent", "paper"), ("accent", "sheet"), ("on-accent", "accent"),
          ("accent", "sheet-2"), ("accent", "accent-soft"), ("warn", "lamp-soft"), ("up", "sheet"), ("up", "land-bg"), ("none", "sheet"), ("none", "land-bg"),
          ("up-edge", "map-stroke"), ("up-edge", "sheet"), ("muted", "disputed"), ("muted", "sheet"), ("ink", "sheet"), ("sheet", "up"), ("sheet", "none"), ("ink", "land-bg")]
    mins = {}
    for name, T in (("light", light), ("dark", dark)):
        for pairs, need, kind in ((text, 4.5, "text"), (ui, 3.0, "non-text")):
            for f, b in pairs:
                r = ratio(col(T, f), col(T, b))
                c(r >= need, f"{name} {f} on {b}: {r:.2f} >= {need}")
                mins[(name, kind)] = min(mins.get((name, kind), 99), r)
        # hachures du rouge : rayure claire (ou sombre) contre le fond rouge
        hat, a = parse(T["none-hatch"])
        base = col(T, "none")
        stripe = [round(x * a + y * (1 - a)) for x, y in zip(hat, base)]
        r = ratio(stripe, base)
        c(r >= 3.0, f"{name}: hatch stripe vs red {r:.2f} >= 3")
        mins[(name, "non-text")] = min(mins[(name, "non-text")], r)
    NOTES.append("contrast minimums: " + ", ".join(f"{k[0]} {k[1]} {v:.2f}" for k, v in sorted(mins.items())))


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
    for line in NOTES:
        print("  · " + line)
    print(f"\n{len(RESULTS)} tests, {len(RESULTS) - len(failed)} passed, {len(failed)} failed · "
          f"{sum(r[2] for r in RESULTS)} checks · {time.time() - t0:.1f}s · screenshots in {ARGS.shots}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
