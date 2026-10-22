#!/usr/bin/env python3
"""Vote : tests de bout en bout (Python + Playwright, Chromium).

    python3 tools/test.py [--shots DIR] [--only NAME[,NAME…]] [--headed]

Teste le site tel qu'il est construit à la racine du dépôt (lancer d'abord `node tools/build.js`),
puis construit dans un dossier temporaire un second site avec des éditions de test jetables
(`node tools/build.js --extra <fixtures> --out <tmp>/site`) : page d'information, édition « leader »,
traductions incomplètes et éditions cassées. Rien n'est écrit dans src/.
Le dépôt est servi avec `python3 -m http.server` sur un port libre. Aucune requête externe n'est
autorisée, sauf Google Fonts (remplacé par une feuille vide pendant les tests).
"""
import argparse, functools, json, math, os, random, re, shutil, socket, subprocess, sys, tempfile, time, traceback, urllib.request, zlib

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
BRAND = "Vote"
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
    c(len(idx.encode()) < 400_000, f"index.html small ({len(idx.encode())} bytes)")
    c(len(zlib.compress(idx.encode(), 9)) < 130_000, f"index.html small once compressed ({len(zlib.compress(idx.encode(), 9))} bytes)")
    NOTES.append(f"page weight: index.html {len(idx.encode()) / 1024:.1f} KB ({len(zlib.compress(idx.encode(), 9)) / 1024:.1f} KB compressed)")
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
          ("up-edge", "map-stroke"), ("up-edge", "sheet"), ("muted", "disputed"), ("muted", "sheet"), ("ink", "sheet"), ("sheet", "up"), ("sheet", "none"), ("ink", "land-bg"),
          # compteur : remplissages et repère contre la piste (fond de la barre) et contre la carte
          ("m-pro", "sheet-2"), ("m-con", "sheet-2"), ("m-pro", "sheet"), ("m-con", "sheet"), ("ink", "sheet-2"), ("ctl", "sheet-2")]
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


# ------------------------------------------------------------------ APPFIX4 A : drapeau, silhouette et bandeau du pays
BANNER_PROBE = """() => {
  const d = document.getElementById('langDlg'), b = d.querySelector('.cbanner');
  if (!b) return null;
  const r = e => { const q = e.getBoundingClientRect(); return { l: q.left, r: q.right, t: q.top, b: q.bottom, w: q.width, h: q.height }; };
  const svg = b.querySelector('.cb-shape'), pa = svg && svg.querySelector('path'), im = b.querySelector('img.flag');
  const vb = svg && svg.viewBox.baseVal, bb = pa && pa.getBBox(), nm = b.querySelector('.cb-name'), first = d.querySelector('[data-pick]');
  return { banner: r(b), dlg: r(d), svg: svg && r(svg), path: pa && r(pa), pathD: pa ? pa.getAttribute('d') : '', flag: im && r(im),
    flagSrc: im ? im.getAttribute('src') : '', flagLoaded: !!(im && im.complete && im.naturalWidth > 0), flagAlt: im ? im.getAttribute('alt') : null,
    vb: vb && [vb.x, vb.y, vb.width, vb.height], bb: bb && [bb.x, bb.y, bb.width, bb.height], name: nm ? nm.textContent : '',
    nameSize: nm ? parseFloat(getComputedStyle(nm).fontSize) : 0, nameFont: nm ? getComputedStyle(nm).fontFamily : '',
    line: (b.querySelector('.cb-line') || {}).textContent || '', firstBtn: first && r(first), dir: getComputedStyle(d).direction,
    sw: document.documentElement.scrollWidth, iw: window.innerWidth, dlgSw: d.scrollWidth, dlgCw: d.clientWidth };
}"""


def banner_checks(c, P, cc, where, ui, name=None, line=None):
    c(P is not None, f"{where}: banner present")
    c(P["flagSrc"] == f"flags/{cc}.svg" and P["flagLoaded"] and P["flagAlt"] == "", f"{where}: flag file flags/{cc}.svg loads (naturalWidth > 0), decorative alt")
    c(abs(P["flag"]["w"] - 72) <= 1 and abs(P["flag"]["h"] - 54) <= 1, f"{where}: flag is 72×54 ({P['flag']['w']:.0f}×{P['flag']['h']:.0f})")
    c(len(P["pathD"]) > 20, f"{where}: silhouette path is not empty")
    vb, bb = P["vb"], P["bb"]
    c(bb[0] >= vb[0] - 0.01 and bb[1] >= vb[1] - 0.01 and bb[0] + bb[2] <= vb[0] + vb[2] + 0.01 and bb[1] + bb[3] <= vb[1] + vb[3] + 0.01,
      f"{where}: the whole shape sits inside its viewBox")
    B = P["banner"]
    for k in ("svg", "path", "flag"):
        R = P[k]
        c(R["l"] >= B["l"] - 0.6 and R["r"] <= B["r"] + 0.6 and R["t"] >= B["t"] - 0.6 and R["b"] <= B["b"] + 0.6, f"{where}: {k} inside the banner")
    c(max(P["path"]["w"], P["path"]["h"]) >= 30, f"{where}: the silhouette is big enough to read ({P['path']['w']:.0f}×{P['path']['h']:.0f})")
    c(B["l"] >= P["dlg"]["l"] - 0.6 and B["r"] <= P["dlg"]["r"] + 0.6 and B["r"] <= P["iw"] + 0.6 and B["l"] >= -0.6, f"{where}: banner inside the dialog and the screen")
    c(P["sw"] <= P["iw"] + 1 and P["dlgSw"] <= P["dlgCw"] + 1, f"{where}: no horizontal overflow ({P['sw']} / {P['iw']}, dialog {P['dlgSw']} / {P['dlgCw']})")
    c(P["nameSize"] >= 24 and "Bricolage" in P["nameFont"], f"{where}: country name is large, in the display face ({P['nameSize']}px)")
    c(P["name"].strip() != "" and (name is None or P["name"] == name), f"{where}: country name “{P['name']}”" + (f" == “{name}”" if name else ""))
    c(P["line"].strip() != "" and (line is None or P["line"].strip() == line), f"{where}: election line “{P['line'][:50]}”")
    c(P["firstBtn"]["t"] >= B["b"] - 0.6, f"{where}: language buttons come below the banner")
    # sens de lecture : le drapeau est au début (à gauche en LTR, à droite en RTL), la silhouette après lui
    if ui == "ar":
        c(P["dir"] == "rtl" and P["flag"]["r"] >= B["r"] - 2 and P["svg"]["r"] <= P["flag"]["l"] + 0.6, f"{where}: RTL, flag at the start (right), silhouette after it")
    else:
        c(P["dir"] == "ltr" and P["flag"]["l"] <= B["l"] + 2 and P["svg"]["l"] >= P["flag"]["r"] - 0.6, f"{where}: LTR, flag at the start (left), silhouette after it")


@test
def banner_dialog(c):
    """Choix de la langue : bandeau du pays (drapeau 72×54 depuis flags/, silhouette du tracé de la carte, nom dans la langue
    de l'interface, ligne d'élection) pour le Nigeria, le Kenya, le Cap-Vert, la Libye (arabe), un pays sans élection ;
    à 320, 390 et 1280 px, en anglais, en français et en arabe (RTL), sans débordement."""
    cases = [("ng", "566"), ("ke", "404"), ("cv", "132"), ("ly", "434"), ("dz", "012")]
    fixed = {("ng", "en"): "Nigeria", ("ke", "en"): "Kenya", ("cv", "fr"): "Cap-Vert", ("ly", "ar"): "ليبيا"}
    for w, h in ((320, 700), (390, 844), (1280, 900)):
        for ui, locale in (("en", "en-GB"), ("fr", "fr-FR"), ("ar", "ar-EG")):
            if w == 1280 and ui == "fr":
                continue
            S = Session(CTX["browser"], width=w, height=h, locale=locale)
            page = S.page
            page.goto(CTX["base"] + "/index.html")
            page.wait_for_selector("#mapWrap .mk")
            page.wait_for_timeout(150)
            c(page.evaluate("state.ui") == ui and not page.evaluate("state.uiChosen"), f"{ui}: interface language follows the browser, nothing chosen yet")
            L = page.evaluate("T[state.ui]")
            for cc, a3 in cases:
                where = f"{cc} {ui} {w}px"
                if cc == "dz":   # pas de repère sur la carte pour un pays sans élection : on le touche dans la liste
                    if not page.evaluate("document.getElementById('listBox').open"):
                        page.click("#listBox summary")
                    page.click(f'#clist [data-place="{a3}"]')
                else:
                    page.click(f'#mapWrap .mk[data-place="{a3}"]')
                page.wait_for_selector("#langDlg[open] .cbanner")
                page.wait_for_function("() => { const i = document.querySelector('#langBody img.flag'); return i && i.complete; }")
                P = page.evaluate(BANNER_PROBE)
                name = page.evaluate(f"cname('{a3}')")
                line = L["legNone"] if cc == "dz" else None
                banner_checks(c, P, cc, where, ui, name=fixed.get((cc, ui)) or name, line=line)
                c(P["name"] == name, f"{where}: name comes from the app's country names")
                if cc == "ng":
                    c("2027" in P["line"], f"{where}: Nigeria election line has the date")
                if w == 390 and ui == "en" and cc in ("ng", "cv"):
                    shot(page, f"banner-{cc}-{w}-{ui}.png")
                if w == 320 and ui in ("en", "ar") and cc == "ng":
                    shot(page, f"banner-{cc}-{w}-{ui}.png")
                page.click("#langCancel")
                page.wait_for_function("() => !document.getElementById('langDlg').open")
            S.close(c)


@test
def banner_all_countries(c):
    """Les 54 pays de la carte : drapeau présent dans flags/ et chargé, silhouette non vide (îles et archipels compris),
    tout dans le bandeau à 320 px ; la France a le même bandeau (fonction du bandeau) ; un drapeau qui ne se charge pas
    disparaît sans casser le bandeau."""
    S = Session(CTX["browser"], width=320, height=800)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    page.wait_for_timeout(150)
    ids = page.evaluate("Object.keys(AFRICA)")
    c(len(ids) >= 54, f"{len(ids)} countries on the map")
    small = []
    for a3 in ids:
        page.evaluate(f"openLang('{a3}')")
        page.wait_for_function("() => { const i = document.querySelector('#langBody img.flag'); return i && i.complete; }")
        P = page.evaluate(BANNER_PROBE)
        cc = page.evaluate(f"AFRICA['{a3}'].a2.toLowerCase()")
        banner_checks(c, P, cc, f"{cc} (all countries, 320px)", "en")
        small.append((max(P["path"]["w"], P["path"]["h"]), cc))
        page.evaluate("closeLang()")
    small.sort()
    NOTES.append("smallest silhouettes at 320 px: " + ", ".join(f"{cc} {s:.0f}px" for s, cc in small[:4]))
    # France : même bandeau (pas de choix de langue pour la France : une seule langue, hors carte)
    page.evaluate("""() => { const d = document.createElement('div'); d.id = 'frProbe'; d.style.cssText = 'position:absolute;top:0;left:0;width:300px;background:#fff';
        d.innerHTML = bannerHTML('fr'); document.body.appendChild(d); }""")
    page.wait_for_function("() => { const i = document.querySelector('#frProbe img.flag'); return i && i.complete; }")
    fr = page.evaluate("""() => { const b = document.querySelector('#frProbe .cbanner'), im = b.querySelector('img.flag'), pa = b.querySelector('path'), q = e => e.getBoundingClientRect();
        return { src: im.getAttribute('src'), ok: im.naturalWidth > 0, d: pa.getAttribute('d').length, pw: q(pa).width, ph: q(pa).height, inside: q(pa).right <= q(b).right + 0.6 && q(pa).bottom <= q(b).bottom + 0.6 && q(pa).left >= q(b).left - 0.6,
          name: b.querySelector('.cb-name').textContent, line: b.querySelector('.cb-line').textContent }; }""")
    c(fr["src"] == "flags/fr.svg" and fr["ok"] and fr["d"] > 50 and fr["inside"] and max(fr["pw"], fr["ph"]) > 30, f"France banner: flag, outline, inside the banner {fr}")
    c(fr["name"] == "France" and "2027" in fr["line"], f"France banner: name and date ({fr['name']}, {fr['line']})")
    page.evaluate("document.getElementById('frProbe').remove()")
    # un drapeau qui ne se charge pas disparaît (pas d'icône cassée) ; nom, silhouette et boutons restent
    page.route("**/flags/ng.svg", lambda r: r.abort())
    page.evaluate("openLang('566')")
    page.wait_for_function("() => document.querySelector('#langBody img.flag').hidden === true")
    P = page.evaluate("""() => ({ name: document.querySelector('#langBody .cb-name').textContent, shape: !!document.querySelector('#langBody .cb-shape path'),
        btn: document.querySelectorAll('#langBody [data-pick]').length, shown: getComputedStyle(document.querySelector('#langBody img.flag')).display })""")
    c(P["name"] == "Nigeria" and P["shape"] and P["btn"] == 5 and P["shown"] == "none", f"a flag that fails to load is hidden, the rest stays: {P}")
    page.evaluate("closeLang()")
    S.close(c, allow_console=True)
    # fichiers : un SVG par pays de la carte + la France, jamais incorporés, léger, avec la licence
    fl = os.path.join(ROOT, "flags")
    idx = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
    c("flags/" not in idx.split("<script>", 1)[0] and 'viewBox="0 0 640 480"' not in idx, "no flag is inlined in index.html")
    files = sorted(f for f in os.listdir(fl) if f.endswith(".svg"))
    c(len(files) >= 55 and "fr.svg" in files and "ng.svg" in files, f"{len(files)} flag files")
    sizes = {f: os.path.getsize(os.path.join(fl, f)) for f in files}
    c(max(sizes.values()) <= 15 * 1024, f"no flag over 15 KB (largest {max(sizes, key=sizes.get)} {max(sizes.values()) / 1024:.1f} KB)")
    c(all(open(os.path.join(fl, f), encoding="utf8").read(200).lstrip().startswith("<svg") for f in files), "flag files are SVG")
    c("MIT" in open(os.path.join(fl, "LICENSE"), encoding="utf8").read(), "flags/LICENSE (MIT) shipped with the flags")
    NOTES.append(f"flags: {len(files)} files, {sum(sizes.values()) / 1024:.1f} KB in all, largest {max(sizes, key=sizes.get)} {max(sizes.values()) / 1024:.1f} KB")


@test
def banner_screens(c):
    """Bandeau compact (drapeau 32×24 + nom) au départ, sur les résultats, sur la page d'information et pour la France ; drapeau seul
    (24×18, nom en texte caché) dans l'en-tête de l'écran de question ; absent sur la carte ; arabe : le drapeau reste du côté du début."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    c(page.evaluate("document.getElementById('topFlag').hidden"), "map: no flag in the header")

    def band(where, cc, name, w=32, h=24):
        page.wait_for_function("() => [...document.querySelectorAll('#app .cband img.flag')].some(i => i.complete)")
        P = page.evaluate("""() => { const b = document.querySelector('#app .cband'), i = b.querySelector('img.flag'), q = i.getBoundingClientRect(), t = b.getBoundingClientRect();
            return { src: i.getAttribute('src'), ok: i.naturalWidth > 0, w: q.width, h: q.height, text: b.textContent.trim(), fl: q.left, fr: q.right, bl: t.left, br: t.right, dir: getComputedStyle(b).direction }; }""")
        c(P["src"] == f"flags/{cc}.svg" and P["ok"], f"{where}: band flag flags/{cc}.svg loads")
        c(abs(P["w"] - w) <= 1 and abs(P["h"] - h) <= 1, f"{where}: band flag is {w}×{h} ({P['w']:.0f}×{P['h']:.0f})")
        c(P["text"].startswith(name), f"{where}: band shows “{name}” ({P['text'][:40]})")
        c((P["fr"] >= P["br"] - 1) if P["dir"] == "rtl" else (P["fl"] <= P["bl"] + 1), f"{where}: flag at the start of the band ({P['dir']})")

    def top_flag(where, cc, name):
        P = page.evaluate("""() => { const t = document.getElementById('topFlag'), i = t.querySelector('img.flag'), s = t.querySelector('.sr'), q = i && i.getBoundingClientRect();
            return { hidden: t.hidden, src: i && i.getAttribute('src'), ok: !!(i && i.naturalWidth > 0), alt: i && i.getAttribute('alt'), w: q && q.width, h: q && q.height,
                     sr: s ? s.textContent : '', inView: !!q && q.left >= 0 && q.right <= innerWidth }; }""")
        c(not P["hidden"] and P["src"] == f"flags/{cc}.svg" and P["ok"] and P["alt"] == "", f"{where}: header flag loads, decorative")
        c(abs(P["w"] - 24) <= 1 and abs(P["h"] - 18) <= 1 and P["inView"], f"{where}: header flag is 24×18 and on screen ({P['w']:.0f}×{P['h']:.0f})")
        c(P["sr"] == name, f"{where}: the country name is there as text for screen readers ({P['sr']})")

    open_country(page, "566", "en")
    page.wait_for_selector(".theme-grid")
    band("Nigeria start", "ng", "Nigeria")
    D = json.load(open(os.path.join(ROOT, "data", "ng.json"), encoding="utf8"))
    page.click(f'[data-prio="{D["ed"]["themes"][0]["id"]}"]')
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    top_flag("Nigeria question", "ng", "Nigeria")
    set_answers(page, find_answers(D, "closest"))
    band("Nigeria results", "ng", "Nigeria")
    c(page.evaluate("document.querySelector('#app .cband').classList.contains('cb-res')"), "results: compact band above the headline")
    c(page.evaluate("document.getElementById('topFlag').hidden"), "results: the band carries the flag, the header one is hidden (no double)")
    # page d'information (Kenya) et pays sans page (Algérie : « pas d'élection nationale »)
    page.goto(CTX["base"] + "/index.html#/ke/en")
    page.wait_for_selector("#app .cband")
    band("Kenya start", "ke", "Kenya")
    page.goto(CTX["base"] + "/index.html#/ao/en")
    page.wait_for_selector("#app .cband")
    band("Angola information page", "ao", "Angola")
    page.goto(CTX["base"] + "/index.html#/dz/en")
    page.wait_for_selector("#app .cband")
    band("Algeria page", "dz", "Algeria")
    # France : une seule langue, hors carte
    page.goto(CTX["base"] + "/index.html#/fr/fr")
    page.wait_for_selector(".theme-grid")
    band("France start", "fr", "France")
    # arabe : drapeau du côté du début, nom lisible
    page.goto(CTX["base"] + "/index.html#/ng/ar")
    page.wait_for_selector(".theme-grid")
    band("Nigeria start (ar)", "ng", page.evaluate("cname('566')"))
    c(page.evaluate("document.documentElement.dir") == "rtl", "ar: page is RTL")
    S.close(c)


# ------------------------------------------------------------------ APPFIX4 B : module « valeurs » (10 énoncés) et compteur collectif
def vset(page, answers):
    """Remplace les réponses « valeurs » (liste de 10 valeurs ou None) et les enregistre dans la session."""
    page.evaluate("""a => { state.vals = {}; VALUES.forEach((v, i) => { if (a[i] !== null && a[i] !== undefined) state.vals[v.id] = a[i]; }); save(); }""", answers)


def vlevel(page, answers):
    return page.evaluate("""a => { const vals = {}; VALUES.forEach((v, i) => { if (a[i] !== null && a[i] !== undefined) vals[v.id] = a[i]; });
        const r = __etv.valuesLevel(vals); return [r.level, r.n]; }""", answers)


@test
def values_logic(c):
    """Position sur les valeurs : v = ax × réponse / 2, moyenne s, au moins 6 réponses, seuils 0,5 / 0,15 (exacts, en entiers) ;
    accord ou désaccord avec tout = centre ; séries libérale et conservatrice ; réponses passées ignorées ;
    les réponses « valeurs » n'entrent jamais dans les scores des partis."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    V = page.evaluate("VALUES.map(v => ({id: v.id, ax: v.ax, topic: v.topic}))")
    ax = [v["ax"] for v in V]
    c(len(V) == 10 and sum(1 for a in ax if a == 1) == 5 and sum(1 for a in ax if a == -1) == 5, "10 statements, 5 / 5 balance")
    c(len({v["id"] for v in V}) == 10, "unique ids")
    c(page.evaluate("VALUES.every(v => ['fr','en','pt','sw','ar'].every(l => v[l] && v[l].short && v[l].text))"), "every statement is written in the five languages")
    c(page.evaluate("typeof __etv.valuesLevel") == "function", "window.__etv.valuesLevel is exported")
    pro = [2 * a for a in ax]        # d'accord (fort) avec les énoncés libéraux, pas d'accord avec les conservateurs
    con = [-2 * a for a in ax]
    c(vlevel(page, [2] * 10) == [0, 10], f"agree with everything → 0 (got {vlevel(page, [2] * 10)})")
    c(vlevel(page, [-2] * 10) == [0, 10], "disagree with everything → 0")
    c(vlevel(page, [0] * 10) == [0, 10], "neither → 0")
    c(vlevel(page, pro) == [2, 10], f"crafted liberal-progressive set → 2 (got {vlevel(page, pro)})")
    c(vlevel(page, con) == [-2, 10], "crafted conservative-nationalist set → −2")
    c(vlevel(page, [a for a in ax]) == [2, 10], "mild agreement with each liberal statement (s = 0.5) → 2")
    mild = [a if i < 5 else 0 for i, a in enumerate(ax)]
    c(vlevel(page, mild) == [1, 10], f"s between 0.15 and 0.5 → 1 (got {vlevel(page, mild)})")
    c(vlevel(page, [-a if i < 5 else 0 for i, a in enumerate(ax)]) == [-1, 10], "s between −0.5 and −0.15 → −1")
    # seuils exacts : 10 réponses, S = Σ ax×réponse ; s = S / 20. S = 3 → s = 0,15 → 0 ; S = 4 → 0,2 → 1 ; S = −3 → 0 ; S = −4 → −1 ; S = 9 → 0,45 → 1 ; S = 10 → 2
    def with_sum(S):
        rem, out = S, [0] * 10
        for i in range(10):
            take = max(-2, min(2, rem * ax[i]))
            out[i] = take
            rem -= take * ax[i]
        assert rem == 0
        return out
    for S_, want in ((3, 0), (4, 1), (9, 1), (10, 2), (-3, 0), (-4, -1), (-9, -1), (-10, -2), (0, 0), (20, 2), (-20, -2)):
        c(vlevel(page, with_sum(S_)) == [want, 10], f"S = {S_} → {want} (got {vlevel(page, with_sum(S_))})")
    # au moins 6 réponses ; les réponses passées sont ignorées
    c(vlevel(page, pro[:5] + [None] * 5) == [None, 5], "5 answered → no level")
    c(vlevel(page, pro[:6] + [None] * 4) == [2, 6], "6 answered → a level; skipped are ignored")
    c(vlevel(page, [None, None, None, None] + pro[4:]) == [2, 6], "the same with the first four skipped")
    c(vlevel(page, [None] * 10) == [None, 0] and page.evaluate("__etv.valuesLevel({}).need") == 6 and page.evaluate("__etv.valuesLevel({}).level") is None, "nothing answered → no level, 6 needed")
    c(page.evaluate("__etv.valuesLevel(null).level") is None, "null is accepted")
    c(page.evaluate("__etv.valuesLevel({v1: 7, v2: 'x', v3: 2, nope: 2}).n") == 1, "out-of-range, non-numeric and unknown ids are ignored")
    # un mélange de skippées et de neutres : 6 répondues dont 3 neutres
    c(vlevel(page, [0, 0, 0] + pro[3:6] + [None] * 4)[1] == 6, "neutral answers count as answered")
    # les scores des partis ne changent pas, quelles que soient les réponses « valeurs »
    D = json.load(open(os.path.join(ROOT, "data", "ng.json"), encoding="utf8"))
    open_country(page, "566", "en")
    page.wait_for_selector(".theme-grid")
    ans = find_answers(D, "closest")
    set_answers(page, ans)
    base_rank = [tuple(r) for r in displayed_ranking(page)]
    base_state = page.evaluate("JSON.stringify([state.answers, state.double, state.priorities, state.order])")
    c(base_rank == expected_ranking(D, ans, {}, []), "party ranking matches the model before any values answer")
    for name, vals in (("liberal", pro), ("conservative", con), ("neutral", [0] * 10)):
        vset(page, vals)
        page.evaluate("rerender()")
        page.wait_for_selector("#pan0 .rank li")
        c([tuple(r) for r in displayed_ranking(page)] == base_rank, f"party ranking unchanged with {name} values answers")
        c(page.evaluate("JSON.stringify([state.answers, state.double, state.priorities, state.order])") == base_state, f"{name}: party answers untouched")
    c(not page.evaluate("Object.keys(state.answers).some(k => /^v/.test(k))") and page.evaluate("Object.keys(state.vals).length") == 10, "values answers live in state.vals, apart")
    S.close(c)


def to_bonus(page):
    """Répond à chaque question de partis (« plutôt d'accord ») jusqu'à l'invitation aux 10 questions sur les valeurs."""
    page.evaluate("TAP_GUARD = 0")
    for _ in range(80):
        view = page.evaluate("state.view")
        if view == "valintro":
            return
        if view == "checkpoint":
            page.click('[data-go="more"]')
            wait_view(page, "question")
            continue
        assert view == "question", f"unexpected view {view} on the way to the bonus screen"
        answer_one(page, 1)
    raise AssertionError("the bonus screen never came")


def answer_values(page, answers):
    """Répond aux 10 énoncés (None = passer), un par un, jusqu'à l'écran « valres »."""
    page.evaluate("TAP_GUARD = 0")   # Playwright clique plus vite qu'un double tapotement (protection testée à part)
    for i, a in enumerate(answers):
        page.wait_for_function("([i]) => state.view === 'valq' && state.vi === i", arg=[i], timeout=5000)
        page.click('[data-vv="skip"]' if a is None else f'.answers .ans[data-vv="{a}"]')
    wait_view(page, "valres")


def to_bonus_fast(page):
    """Comme to_bonus, sans cliquer 38 fois : réponses posées dans l'état, dernière question répondue au clic."""
    page.evaluate("""() => { TAP_GUARD = 0; buildOrder(); state.order.slice(0, -1).forEach(q => { state.answers[q] = 1; });
        state.i = state.order.length - 1; state.nPrio = 0; viewQuestion(); }""")
    wait_view(page, "question")
    answer_one(page, 1)
    wait_view(page, "valintro")


@test
def values_flow(c):
    """Invitation après la dernière question de partis (une fois), écran des 10 énoncés (pastille « Valeurs », pas de ★),
    position, carte des résultats, rechargement, modification, « Recommencer » ; adresses #/…/values ; sans adresse de compteur :
    carte personnelle seule, aucun bouton d'envoi, aucune requête externe."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    L = page.evaluate("T.en")
    c(page.evaluate("__etv.METER_ENDPOINT") == "", "repository build: endpoint empty, collective features off")
    D, th = ng_start(page)
    to_bonus(page)
    c(page.evaluate("[state.view, location.hash]") == ["valintro", "#/ng/en/values"], "after the last party question: the invitation, #/ng/en/values")
    c(heading_ok(heading_levels(page)), f"invitation: heading order {heading_levels(page)}")
    c(page.inner_text("#app h1").strip() == L["valIntroTitle"], "invitation title")
    btn = page.evaluate("[...document.querySelectorAll('#app .actions button')].map(b => b.textContent.trim())")
    c(btn == [L["valStart"], L["valSkipResults"]], f"two choices: start the 10 / skip to my results ({btn})")
    c(page.locator("[data-meter],.vsend").count() == 0, "no collective part without an endpoint")
    c(L["valIntroTextLocal"] in page.inner_text("#app"), "the local wording (nothing is sent) is used")
    shot(page, "values-intro-390.png", full=True)
    # passer : résultats ; l'invitation ne revient pas pendant cette session
    page.click('[data-go="vresults"]')
    wait_view(page, "results")
    ans = {int(k): v for k, v in page.evaluate("state.answers").items()}
    base_rank = [tuple(r) for r in displayed_ranking(page)]
    c(base_rank == expected_ranking(D, ans, {}, [th]), "party ranking as the model says (values skipped)")
    c(page.locator(".vcard").count() == 1 and page.inner_text(".vcard h2").strip() == L["valIntroTitle"], "results: the values card invites to answer")
    c(heading_ok(heading_levels(page)), f"results with the card: heading order {heading_levels(page)}")
    # depuis la carte : les 10 énoncés, à partir du premier
    page.click('.vcard [data-go="vopen"]')
    wait_view(page, "valq")
    c(page.evaluate("location.hash") == "#/ng/en/values/1", "first statement at #/ng/en/values/1")
    q = page.evaluate("""() => ({ chip: [...document.querySelectorAll('#app .chip')].map(e => e.textContent.trim()), star: document.querySelectorAll('#app .star').length,
        h1: document.querySelector('#app h1').textContent.trim(), count: document.querySelector('.q-count').textContent.trim() })""")
    c(q["chip"] == [L["valChip"]] and q["star"] == 0, f"‘Values’ chip, no ★ ({q['chip']}, {q['star']})")
    c(q["h1"] == page.evaluate("vtext(VALUES[0]).text") and q["count"] == "1 / 10", "statement 1 of 10")
    c(page.locator(".q-meta .mini, .q-meta .min, #app .minis").count() == 0, "no ministries line")
    c(heading_ok(heading_levels(page)), f"statement screen: heading order {heading_levels(page)}")
    c(page.evaluate("[...document.querySelectorAll('.answers .ans')].map(b => b.dataset.vv).join()") == "2,1,0,-1,-2", "five answers, strongly agree first")
    c(page.evaluate("document.getElementById('topFlag').hidden") is False, "the country flag stays in the header")
    shot(page, "values-question-390.png")
    # reculer et revenir
    page.click('.answers .ans[data-vv="2"]')
    page.wait_for_function("state.vi === 1")
    page.click('[data-go="vprev"]')
    page.wait_for_function("state.vi === 0")
    c(page.get_attribute('.answers .ans[data-vv="2"]', "aria-pressed") == "true", "Previous shows the answer already given")
    # série libérale
    ax = page.evaluate("VALUES.map(v => v.ax)")
    pro = [2 * a for a in ax]
    answer_values(page, pro)
    c(page.evaluate("[location.hash, Object.keys(state.vals).length]") == ["#/ng/en/values/done", 10], "after the tenth: #/ng/en/values/done, 10 answers saved")
    c(heading_ok(heading_levels(page)), f"values result: heading order {heading_levels(page)}")
    c(page.inner_text(".v-level").strip() == L["valLevels"]["2"], "level: clearly liberal–progressive")
    bar = page.evaluate("""() => { const m = document.querySelector('.vcard .mbar'), k = document.querySelector('.vcard .mmark'), q = e => e.getBoundingClientRect();
        return { role: m.getAttribute('role'), label: m.getAttribute('aria-label'), mark: (q(k).left + q(k).right) / 2, l: q(m).left, r: q(m).right }; }""")
    c(bar["role"] == "img" and L["valLevels"]["2"] in bar["label"], "the bar says its level in text")
    c(abs(bar["mark"] - bar["l"]) < 18, f"the marker sits at the start end for level 2 ({bar['mark'] - bar['l']:.0f}px)")
    c(page.evaluate("T.en.valBasis(10)") in page.inner_text(".vcard"), "‘computed from your 10 answers…’")
    page.click(".v-which summary")
    c(page.locator(".v-list li").count() == 10, "‘Which questions counted?’ lists the 10 statements")
    c(page.evaluate("[...document.querySelectorAll('.v-list .vq-a b')].every(b => b.textContent.trim() !== '')"), "…with the answer given to each")
    c(page.locator(".vsend, [data-go='vsend'], [data-meter]").count() == 0, "no send button, no meter without an endpoint")
    shot(page, "values-result-390.png", full=True)
    # vers les résultats : le classement n'a pas bougé, la carte est là avec le repère
    page.click('[data-go="vresults"]')
    wait_view(page, "results")
    c([tuple(r) for r in displayed_ranking(page)] == base_rank, "party ranking unchanged after the values answers")
    c(page.locator(".vcard .mmark").count() == 1 and page.inner_text(".vcard .v-level").strip() == L["valLevels"]["2"], "results: the card shows the marker and the level")
    shot(page, "values-card-results-390.png", full=True)
    # rechargement : tout est restitué
    page.reload()
    page.wait_for_function("state.view === 'results'")
    c(page.evaluate("Object.keys(state.vals).length") == 10 and page.locator(".vcard .mmark").count() == 1, "reload: values answers restored")
    # modifier : retour aux énoncés (depuis le premier), position à jour
    page.click('.vcard [data-go="vedit"]')
    wait_view(page, "valq")
    c(page.evaluate("state.vi") == 0, "‘Change my answers’ starts again at the first statement")
    answer_values(page, [-a for a in pro])
    c(page.inner_text(".v-level").strip() == L["valLevels"]["-2"], "changed answers → clearly conservative–nationalist")
    page.click('[data-go="vresults"]')
    wait_view(page, "results")
    c([tuple(r) for r in displayed_ranking(page)] == base_rank, "party ranking still unchanged")
    # recommencer : tout est effacé, l'invitation reviendra
    page.click('#app [data-go="restart"]')
    page.click('#confirmBox [data-go="restart!"]')
    page.wait_for_function("state.view !== 'results'")
    c(page.evaluate("[Object.keys(state.vals).length, state.vseen, Object.keys(state.answers).length]") == [0, False, 0], "Start over erases the values answers too")
    saved = page.evaluate("(() => { const s = JSON.parse(sessionStorage.getItem(SKEY) || '{}'); return [Object.keys(s.vals || {}).length, !!s.vseen]; })()")
    c(saved == [0, False], f"…and from the saved session ({saved})")
    # deuxième passage : l'invitation revient ; « Commencer les 10 » mène au premier énoncé
    page.click(f'[data-prio="{th}"]')
    page.click('[data-go="startq"]')
    wait_view(page, "question")
    to_bonus_fast(page)
    c(page.evaluate("location.hash") == "#/ng/en/values", "after a restart the invitation comes back")
    page.click('[data-go="vstart"]')
    wait_view(page, "valq")
    c(page.evaluate("[location.hash, state.vi]") == ["#/ng/en/values/1", 0], "‘Start the 10’ opens statement 1")
    page.go_back()
    wait_view(page, "valintro")
    c(page.evaluate("location.hash") == "#/ng/en/values", "Back from statement 1 returns to the invitation")
    page.go_forward()
    wait_view(page, "valq")
    answer_values(page, [None] * 4 + pro[4:])
    c(page.inner_text(".v-level").strip() == L["valLevels"]["2"], "4 skipped, 6 answered: still a level, skipped ones ignored")
    c(page.evaluate("T.en.valBasis(6)") in page.inner_text(".vcard"), "…and it says it is computed from 6 answers")
    page.click('[data-go="vresults"]')
    wait_view(page, "results")
    # adresses directes
    page = S.new_page()   # nouvel onglet : session vide
    page.goto(CTX["base"] + "/index.html#/ng/en/values/3")
    wait_view(page, "valq")
    c(page.evaluate("[state.vi, document.querySelector('.q-count').textContent.trim()]") == [2, "3 / 10"], "#/ng/en/values/3 opens the third statement")
    page = S.new_page()
    page.goto(CTX["base"] + "/index.html#/ng/en/values/99")
    wait_view(page, "valintro")
    c(page.locator('[data-go="vback"]').count() == 1 and page.locator('[data-go="vresults"]').count() == 0, "no party answers: the invitation offers to go back to the country, not to results")
    page.click('[data-go="vback"]')
    page.wait_for_selector(".theme-grid")
    c(page.evaluate("location.hash") == "#/ng/en", "back to the country page")
    # pas assez de réponses : pas de niveau
    page.goto(CTX["base"] + "/index.html#/ng/en/values/1")
    wait_view(page, "valq")
    answer_values(page, [2, 2, 2, 2, 2] + [None] * 5)
    c(page.locator(".v-level").count() == 0 and page.locator(".mbar").count() == 0, "5 answers: no level, no bar")
    c(page.evaluate("T.en.valNeedMore(1)") in page.inner_text(".vcard"), "…it says how many more are needed")
    c(page.locator(".vcard [data-go='vopen']").count() == 1, "…and offers to continue")
    S.close(c)


@test
def values_cards(c):
    """Carte « Où tu te situes sur les valeurs » sur chaque page de pays sans questionnaire (page d'information, pays sans élection),
    sans rien de collectif quand l'adresse du compteur est vide ; un seul bouton principal par page ; arabe en RTL."""
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap svg")
    L = page.evaluate("T.en")
    ax = page.evaluate("VALUES.map(v => v.ax)")
    for cc, kind in (("ao", "information page"), ("dz", "country without election")):
        page.goto(CTX["base"] + f"/index.html#/{cc}/en")
        page.wait_for_selector("#app .cband")
        c(page.locator(".vcard").count() == 1, f"{kind}: the values card is on the page")
        c(heading_ok(heading_levels(page)), f"{kind}: heading order {heading_levels(page)}")
        c(page.locator("#app .btn-primary").count() == 1, f"{kind}: still one primary button")
        page.click('.vcard [data-go="vopen"]')
        wait_view(page, "valq")
        c(page.evaluate("location.hash") == f"#/{cc}/en/values/1", f"{kind}: the card opens #/{cc}/en/values/1")
        c(page.locator("#topFlag img.flag").count() == 1, f"{kind}: flag in the header")
        answer_values(page, [2 * a for a in ax])
        c(page.inner_text(".v-level").strip() == L["valLevels"]["2"], f"{kind}: position computed")
        c(page.locator('[data-go="vback"]').count() == 1 and page.locator('[data-go="vresults"]').count() == 0, f"{kind}: the way back is the country page")
        page.click('[data-go="vback"]')
        page.wait_for_selector("#app .cband")
        c(page.locator(".vcard .mmark").count() == 1, f"{kind}: back on the page, the card shows the position")
        c(page.evaluate("location.hash") == f"#/{cc}/en", f"{kind}: back at #/{cc}/en")
        page.evaluate("state.vals = {}; save()")
    # arabe : RTL, barre en miroir
    page.goto(CTX["base"] + "/index.html#/ng/ar/values/done")
    wait_view(page, "valres")
    vset(page, [2 * a for a in ax])
    page.evaluate("rerender()")
    page.wait_for_selector(".vcard .mmark")
    R = page.evaluate("""() => { const m = document.querySelector('.vcard .mbar').getBoundingClientRect(), k = document.querySelector('.vcard .mmark').getBoundingClientRect(),
        e = [...document.querySelectorAll('.vcard .m-end')].map(x => x.getBoundingClientRect().left + x.getBoundingClientRect().width / 2);
        return { dir: document.documentElement.dir, mark: (k.left + k.right) / 2, l: m.left, r: m.right, ends: e }; }""")
    c(R["dir"] == "rtl" and abs(R["mark"] - R["r"]) < 18, f"ar: liberal–progressive is at the start = right end ({R['r'] - R['mark']:.0f}px)")
    c(R["ends"][0] > R["ends"][1], "ar: the liberal–progressive label is on the right, conservative on the left")
    no_overflow(page, c, "values card ar 390")
    S.close(c)


# ---- compteur collectif : site de test construit avec une adresse fictive, API simulée par des routes Playwright
EP = "https://meter.example.test"
Z = {"-2": 0, "-1": 0, "0": 0, "1": 0, "2": 0}
UPD = "2026-10-20T08:00:00Z"


def dist(m2=0, m1=0, z=0, p1=0, p2=0):
    """Répartition par niveau : −2, −1, 0, 1, 2 (2 = nettement libéral–progressiste)."""
    return {"-2": m2, "-1": m1, "0": z, "1": p1, "2": p2}


DIST = {
    # majorité progressiste : 200 personnes, 83,5 % progressistes (niveaux 1 et 2), 6,5 % conservateurs, 10 % équilibrés
    "prog": {"updated": UPD, "total": dist(m2=4, m1=9, z=20, p1=60, p2=107), "byCountry": {"ng": dist(m2=2, m1=5, z=9, p1=22, p2=12), "ke": dist(p1=3)}},
    # majorité conservatrice : 80 % conservateurs, 7,5 % progressistes, 12,5 % équilibrés
    "cons": {"updated": UPD, "total": dist(m2=90, m1=70, z=25, p1=12, p2=3), "byCountry": {"ng": dist(m2=20, m1=15, z=5, p1=3, p2=1)}},
    # à égalité : 40 % / 40 % / 20 %
    "even": {"updated": UPD, "total": dist(m2=40, m1=40, z=40, p1=40, p2=40), "byCountry": {"ng": dist(m2=8, m1=8, z=8, p1=8, p2=8)}},
    # pas encore 30 réponses
    "wait": {"updated": UPD, "total": dist(m2=1, m1=2, z=3, p1=5, p2=2), "byCountry": {"ng": dist(p1=2)}},
}


class MeterMock:
    """Fausse API du compteur : GET /counts et POST /v, avec la liste de ce qui a été demandé."""

    def __init__(self, ctx, counts, get="ok", post="ok"):
        self.counts = json.loads(json.dumps(counts)) if counts else None
        self.get_mode, self.post_mode = get, post
        self.gets, self.posts, self.other, self.pending = [], [], [], []
        ctx.route(re.compile(r"^https://meter\.example\.test/"), self.handle)

    def release(self):
        """Répond aux lectures retenues (mode « hold »)."""
        for r in self.pending:
            r.fulfill(status=200, content_type="application/json", headers={"Access-Control-Allow-Origin": "*"}, body=json.dumps(self.counts))
        self.pending = []

    def handle(self, route):
        req = route.request
        cors = {"Access-Control-Allow-Origin": "*"}
        path = req.url[len(EP):]
        if req.method == "GET" and path == "/counts":
            self.gets.append(dict(req.headers))
            if self.get_mode == "abort":
                return route.abort()
            if self.get_mode in ("hang", "hold"):
                self.pending.append(route)   # « hang » ne répond jamais (rendue par abort à la fin du test) ; « hold » répond après release()
                return None
            if self.get_mode == "500":
                return route.fulfill(status=500, headers=cors, body="oops")
            if self.get_mode == "garbage":
                return route.fulfill(status=200, content_type="application/json", headers=cors, body='{"nope": 1}')
            return route.fulfill(status=200, content_type="application/json", headers=cors, body=json.dumps(self.counts))
        if req.method == "POST" and path == "/v":
            self.posts.append({"body": req.post_data, "headers": dict(req.headers), "ok": self.post_mode == "ok"})
            if self.post_mode != "ok":
                return route.fulfill(status=500, headers=cors, body="")
            try:
                j = json.loads(req.post_data)
                for tgt in (self.counts["total"], self.counts["byCountry"].setdefault(j["c"], dict(Z))):
                    tgt[str(j["l"])] += 1
            except Exception:
                pass
            return route.fulfill(status=204, headers=cors)
        self.other.append((req.method, req.url))
        return route.fulfill(status=404, headers=cors, body="")


def meter_base():
    """Site construit avec --endpoint (adresse fictive), servi à part ; nettoyé à la fin des tests."""
    if "meter_base" not in CTX:
        d = tempfile.mkdtemp(prefix="etv-meter-")
        r = subprocess.run(["node", os.path.join(ROOT, "tools", "build.js"), "--endpoint", EP, "--out", d], capture_output=True, text=True, timeout=180)
        assert r.returncode == 0 and "WARN" not in r.stdout + r.stderr, f"meter site build failed: {(r.stdout + r.stderr)[-400:]}"
        proc, base = serve(d)
        CTX["meter_base"], CTX["meter_dir"], CTX["meter_proc"] = base, d, proc
    return CTX["meter_base"]


METER_GEOM = """() => { const root = document.querySelector('[data-meter="africa"] .meter'), bar = root.querySelector('.mbar'), halves = bar.querySelectorAll('.mhalf'),
  pro = bar.querySelector('.mfill.pro'), con = bar.querySelector('.mfill.con'), tick = bar.querySelector('.mtick'), q = e => e.getBoundingClientRect(), t = q(tick), tc = (t.left + t.right) / 2;
  const cs = e => getComputedStyle(e);
  return { pro: q(pro).width / q(halves[0]).width, con: q(con).width / q(halves[1]).width, tc, barL: q(bar).left, barR: q(bar).right,
    proL: q(pro).left, proR: q(pro).right, conL: q(con).left, conR: q(con).right, h0: [q(halves[0]).left, q(halves[0]).right], h1: [q(halves[1]).left, q(halves[1]).right],
    proImg: cs(pro).backgroundImage, conImg: cs(con).backgroundImage, conCap: parseFloat(cs(con).borderInlineEndWidth), proRad: cs(pro).borderTopLeftRadius + '|' + cs(pro).borderTopRightRadius,
    role: bar.getAttribute('role'), label: bar.getAttribute('aria-label'), pctPro: root.querySelector('.m-end.m-pro b').textContent, pctCon: root.querySelector('.m-end.m-con b').textContent,
    sub: root.querySelector('.m-sub').textContent, cav: root.querySelector('.m-cav').textContent, title: root.querySelector('.mt').textContent, h: root.querySelector('.mt').tagName,
    transition: cs(pro).transitionDuration, go: root.classList.contains('go') }; }"""


@test
def meter_states(c):
    """Compteur d'Afrique sous le titre de la carte : moins de 30 réponses (« s'ouvre à 30 », ligne de progression), puis trois
    répartitions fabriquées (majorité progressiste, majorité conservatrice, égalité) : longueurs des remplissages proportionnelles,
    pourcentages et équilibrés en texte, étiquette aria, motifs différents (pas seulement la teinte), une seule lecture par session ;
    en arabe la barre est en miroir ; mouvement : remplissage animé en 600 ms au plus, seulement si le mouvement est permis."""
    base = meter_base()
    for key in ("prog", "cons", "even"):
        S = Session(CTX["browser"], width=390, height=844)
        M = MeterMock(S.ctx, DIST[key])
        page = S.page
        page.goto(base + "/index.html")
        page.wait_for_selector('[data-meter="africa"] .mbar')
        L = page.evaluate("T.en")
        d = DIST[key]["total"]
        tot = sum(d.values())
        pro, con, bal = d["1"] + d["2"], d["-1"] + d["-2"], d["0"]
        G = page.evaluate(METER_GEOM)
        pc = lambda x: page.evaluate(f"pctPlain({x})")
        c(abs(G["pro"] - pro / tot) < 0.01 and abs(G["con"] - con / tot) < 0.01, f"{key}: fills are proportional to the shares (pro {G['pro']:.3f} vs {pro / tot:.3f}, con {G['con']:.3f} vs {con / tot:.3f})")
        c(G["pctPro"] == pc(pro / tot) and G["pctCon"] == pc(con / tot), f"{key}: end percentages {G['pctPro']} / {G['pctCon']}")
        c(page.evaluate(f"T.en.meterBal({json.dumps(pc(bal / tot))})") in G["sub"] and f"{tot}" in G["sub"].replace(",", ""), f"{key}: balanced share and number of people are printed ({G['sub']})")
        c("2 countries" in G["sub"] if key == "prog" else "1 country" in G["sub"], f"{key}: country count ({G['sub']})")
        c("20 October 2026" in G["sub"], f"{key}: update date ({G['sub']})")
        c(G["role"] == "img" and pc(pro / tot) in G["label"] and pc(con / tot) in G["label"] and pc(bal / tot) in G["label"] and str(tot) in G["label"], f"{key}: aria-label states the numbers ({G['label']})")
        c("representative" in G["cav"], f"{key}: caveat ‘not a representative poll’")
        c(G["h"] == "H2", f"{key}: meter title is an h2 ({G['h']})")
        # sens : le côté progressiste est au début (gauche), son remplissage part du centre vers le début ; l'autre à la fin
        c(abs(G["proR"] - G["tc"]) < 3 and G["proL"] < G["tc"], f"{key}: progressive fill grows from the centre towards the start (left)")
        c(abs(G["conL"] - G["tc"]) < 3 and G["conR"] > G["tc"], f"{key}: conservative fill grows from the centre towards the end (right)")
        c(abs(G["tc"] - (G["barL"] + G["barR"]) / 2) < 2, f"{key}: the centre tick is in the middle")
        # pas seulement la teinte : rayures + bout arrondi d'un côté, points + bout carré marqué de l'autre
        c("repeating-linear-gradient" in G["proImg"] and "radial-gradient" in G["conImg"], f"{key}: stripes vs dots")
        c(G["conCap"] >= 3, f"{key}: conservative side has a marked square end ({G['conCap']}px)")
        c(len(M.gets) == 1 and "cookie" not in M.gets[0] and "authorization" not in M.gets[0], f"{key}: one GET /counts, no cookie ({len(M.gets)})")
        c(page.inner_text("#footer").strip().endswith(L["footerMeter"]) and "nowhere" not in page.inner_text("#footer"), f"{key}: the footer no longer says ‘sent nowhere’ once an optional send exists")
        c(not M.posts, f"{key}: nothing is sent just by looking")
        if key == "prog":
            shot(page, "meter-prog-390.png")
            # une seule lecture par session : la navigation ne redemande rien
            page.goto(base + "/index.html#/ng/en")
            page.wait_for_selector(".theme-grid")
            page.goto(base + "/index.html#/")
            page.wait_for_selector('[data-meter="africa"] .mbar')
            c(len(M.gets) == 1, f"GET /counts once per session ({len(M.gets)})")
            # carte du pays sur l'écran de départ : 50 contributions pour le Nigeria → barre « Nigeria » ; Kenya (3) → rien
            page.goto(base + "/index.html#/ng/en")
            page.wait_for_selector('[data-meter="country"] .mbar')
            nt = page.inner_text('[data-meter="country"] .mt').strip()
            c(nt == "Nigeria" and page.locator('[data-meter="country"] .m-scope').count() == 1, f"Nigeria start screen: country meter (≥ 30 answers) titled ‘{nt}’")
            c(page.evaluate("document.querySelector('[data-meter=country] .mt').tagName") == "H2", "start screen: standalone meter title is an h2")
            page.goto(base + "/index.html#/ke/en")
            page.wait_for_selector("#app .cband")
            page.wait_for_timeout(200)
            c(page.evaluate("[...document.querySelectorAll('[data-meter=country]')].every(e => e.hidden || !e.querySelector('.meter'))"), "Kenya (3 answers): no country meter")
            c(page.locator(".meter-slot[data-state='loading']").count() == 0, "no loading placeholder left behind")
            c(len(M.gets) == 1, "still a single GET")
        S.close(c)
    # pas de saut de mise en page quand les chiffres arrivent (place réservée pendant le chargement) : décalage cumulé quasi nul
    cls_js = ("window.__cls = 0; window.__src = []; new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) { window.__cls += e.value; "
              "window.__src.push(e.value.toFixed(4) + ' ' + (e.sources || []).map(s => (s.node && (s.node.id || s.node.className || s.node.tagName)) + ' y' + Math.round(s.previousRect.y) + '→' + Math.round(s.currentRect.y)).join(', ')); } }).observe({type: 'layout-shift', buffered: true});")
    for w in (320, 390, 1280):
        S = Session(CTX["browser"], width=w, height=900, motion="no-preference", init=cls_js)
        M = MeterMock(S.ctx, DIST["prog"], get="hold")
        page = S.page
        page.goto(base + "/index.html")
        page.wait_for_selector("#mapWrap svg")
        page.wait_for_function("meter.status === 'loading'")
        c(page.locator('.meter-slot[data-meter="africa"][data-state="loading"]').count() == 1, "space is reserved while the numbers load")
        before = page.evaluate("window.__cls")   # le décalage du démarrage de la page elle-même (en-tête) n'est pas celui du compteur
        M.release()
        page.wait_for_selector('[data-meter="africa"] .mbar')
        page.wait_for_timeout(900)
        cls = page.evaluate("window.__cls") - before
        c(cls < 0.02, f"layout shift when the meter arrives at {w}px: {cls:.4f} < 0.02 {page.evaluate('window.__src')[:4]}")
        NOTES.append(f"meter layout shift at {w}px: {cls:.4f}")
        S.close(c)
    # sous 30 réponses : barre d'attente
    S = Session(CTX["browser"], width=390, height=844)
    M = MeterMock(S.ctx, DIST["wait"])
    page = S.page
    page.goto(base + "/index.html")
    page.wait_for_selector(".meter-wait")
    W = page.evaluate("""() => { const r = document.querySelector('[data-meter=africa] .meter-wait'), p = r.querySelector('[role=progressbar]');
        return { text: r.textContent, now: p.getAttribute('aria-valuenow'), max: p.getAttribute('aria-valuemax'), bar: r.querySelectorAll('.mbar').length, w: p.firstElementChild.style.inlineSize,
                 line: !!p.querySelector('span') }; }""")
    c("30" in W["text"] and "13" in W["text"], f"below 30: ‘The meter opens at 30 answers — 13 so far’ ({W['text'][:80]})")
    c(W["now"] == "13" and W["max"] == "30" and W["bar"] == 0 and W["line"] and abs(float(W["w"].rstrip("%")) - 13 / 30 * 100) < 0.2, f"below 30: thin progress line, no bar ({W})")
    c("representative" in W["text"], "below 30: the caveat is there too")
    shot(page, "meter-wait-390.png")
    S.close(c)
    # arabe : barre en miroir
    S = Session(CTX["browser"], width=390, height=844, locale="ar-EG")
    M = MeterMock(S.ctx, DIST["prog"])
    page = S.page
    page.goto(base + "/index.html")
    page.wait_for_selector('[data-meter="africa"] .mbar')
    G = page.evaluate(METER_GEOM)
    c(page.evaluate("document.documentElement.dir") == "rtl", "ar: RTL")
    c(abs(G["proL"] - G["tc"]) < 3 and G["proR"] > G["tc"], "ar: progressive fill grows from the centre towards the start (right)")
    c(abs(G["conR"] - G["tc"]) < 3 and G["conL"] < G["tc"], "ar: conservative fill grows towards the end (left)")
    ends = page.evaluate("[...document.querySelectorAll('[data-meter=africa] .m-end')].map(e => (e.getBoundingClientRect().left + e.getBoundingClientRect().right) / 2)")
    c(ends[0] > ends[1], "ar: the progressive percentage is on the right, the conservative one on the left")
    c(abs(G["pro"] - 167 / 200) < 0.01, "ar: same proportions")
    c(page.evaluate("document.querySelector('[data-meter=africa] .m-end b').dir") == "ltr", "ar: numbers keep their own direction")
    no_overflow(page, c, "meter ar 390")
    shot(page, "meter-ar-390.png")
    S.close(c)
    # mouvement : permis → 600 ms au plus ; réduit → pas de transition
    for motion, check in (("no-preference", lambda t: 0 < float(t.rstrip("s")) <= 0.6), ("reduce", lambda t: float(t.rstrip("s")) == 0)):
        S = Session(CTX["browser"], width=390, height=844, motion=motion)
        MeterMock(S.ctx, DIST["prog"])
        page = S.page
        page.goto(base + "/index.html")
        page.wait_for_selector('[data-meter="africa"] .mbar')
        page.wait_for_timeout(900)
        G = page.evaluate(METER_GEOM)
        c(check(G["transition"]), f"motion {motion}: fill transition lasts {G['transition']}")
        c(abs(G["pro"] - 167 / 200) < 0.01 and G["go"] is not None, f"motion {motion}: the fill ends at its share ({G['pro']:.3f})")
        S.close(c)
    # sombre : mêmes motifs, mêmes proportions
    S = Session(CTX["browser"], width=390, height=844, scheme="dark")
    MeterMock(S.ctx, DIST["prog"])
    page = S.page
    page.goto(base + "/index.html")
    page.wait_for_selector('[data-meter="africa"] .mbar')
    G = page.evaluate(METER_GEOM)
    c(abs(G["pro"] - 167 / 200) < 0.01 and "gradient" in G["proImg"], "dark theme: same bar")
    shot(page, "meter-dark-390.png")
    S.close(c)


@test
def meter_send(c):
    """Envoi anonyme : bouton seulement avec une adresse configurée ; POST <adresse>/v avec {c, l} et rien d'autre (text/plain, sans cookie) ;
    un seul envoi par pays et par navigateur ; « Merci » puis le compteur se met à jour ; échec : message calme et bouton « Réessayer »."""
    base = meter_base()
    S = Session(CTX["browser"], width=390, height=844)
    M = MeterMock(S.ctx, DIST["prog"])
    page = S.page
    page.goto(base + "/index.html")
    page.wait_for_selector('[data-meter="africa"] .mbar')
    L = page.evaluate("T.en")
    c(page.evaluate("__etv.METER_ENDPOINT") == EP, "the build put the endpoint in the page")
    src = page.evaluate("sendMeter.toString()")
    c("keepalive: true" in src and 'credentials: "omit"' in src and 'mode: "cors"' in src and '"Content-Type": "text/plain"' in src, "request options: keepalive, credentials omit, cors, text/plain")
    ax = page.evaluate("VALUES.map(v => v.ax)")
    pro = [2 * a for a in ax]
    page.goto(base + "/index.html#/ng/en/values/done")
    wait_view(page, "valres")
    c(page.locator(".vsend").count() == 0, "no values answers yet: nothing to send")
    vset(page, [2] * 5 + [None] * 5)
    page.evaluate("rerender()")
    c(page.locator("[data-go='vsend']").count() == 0, "fewer than 6 answers (no level): no send button")
    vset(page, pro)
    page.evaluate("rerender()")
    page.wait_for_selector("[data-go='vsend']")
    box = page.inner_text(".vsend")
    c(L["meterSend"] in box and L["meterSentWhat"] in box, "the button says what it does, and what is sent (country code + one of five levels)")
    c("country code" in L["meterSentWhat"] and "five levels" in L["meterSentWhat"], "…wording: only the country code and one of five levels")
    c(page.evaluate("document.querySelector('[data-go=vsend]').tagName") == "BUTTON", "send button is a real button")
    c(len(M.posts) == 0, "nothing is sent before the click")
    page.click("[data-go='vsend']")
    page.wait_for_selector(".vsend .m-ok")
    c(len(M.posts) == 1, "one POST")
    P = M.posts[0]
    c(P["body"] == '{"c":"ng","l":2}', f"payload is exactly {{c, l}}: {P['body']}")
    c(P["headers"].get("content-type", "").startswith("text/plain") and "cookie" not in P["headers"] and "authorization" not in P["headers"], f"text/plain, no cookie, no authorization ({P['headers'].get('content-type')})")
    c(L["meterThanks"] in page.inner_text(".vsend .m-ok") and page.locator("[data-go='vsend']").count() == 0, "‘Thanks — counted’ replaces the button")
    page.wait_for_function(f"document.querySelector('[data-meter=africa] .m-sub') && document.querySelector('[data-meter=africa] .m-sub').textContent.includes('201')")
    c(len(M.gets) == 2, f"the meter is read again after a send ({len(M.gets)} GETs)")
    c(page.evaluate("localStorage.getItem('etv.sent.ng')") == "1", "one contribution per country per browser: remembered in this browser")
    # un second envoi pour le même pays est impossible : rechargement, nouvel onglet, nouvelle session
    page.reload()
    wait_view(page, "valres")
    c(page.locator("[data-go='vsend']").count() == 0 and page.locator(".vsend .m-ok").count() == 1, "after a reload: no button, still ‘counted’")
    page2 = S.new_page()
    page2.goto(base + "/index.html#/ng/en/values/done")
    wait_view(page2, "valres")
    vset(page2, pro)
    page2.evaluate("rerender()")
    c(page2.locator("[data-go='vsend']").count() == 0, "another tab of the same browser: no button for Nigeria")
    # un autre pays : un nouvel envoi, avec son propre code
    page2.goto(base + "/index.html#/ke/en/values/done")
    page2.wait_for_function("state.view === 'valres' && curCc() === 'ke'")
    vset(page2, [-2 * a for a in ax])
    page2.evaluate("rerender()")
    page2.wait_for_selector("[data-go='vsend']")
    page2.click("[data-go='vsend']")
    page2.wait_for_selector(".vsend .m-ok")
    c([p["body"] for p in M.posts] == ['{"c":"ng","l":2}', '{"c":"ke","l":-2}'], f"Kenya gets its own contribution ({[p['body'] for p in M.posts]})")
    c(not M.other, f"no other request to the endpoint ({M.other})")
    S.close(c)
    # échec : message calme, bouton « Réessayer », rien n'est mémorisé ; puis réussite
    S = Session(CTX["browser"], width=390, height=844)
    M = MeterMock(S.ctx, DIST["prog"], post="fail")
    page = S.page
    page.goto(base + "/index.html#/ng/en/values/done")
    wait_view(page, "valres")
    vset(page, pro)
    page.evaluate("rerender()")
    page.click("[data-go='vsend']")
    page.wait_for_function("() => { const e = document.getElementById('meterErr'); return e && !e.hidden; }")
    c(page.inner_text("#meterErr").strip() == L["meterErr"], "failure: a calm message")
    btn = page.locator("[data-go='vsend']")
    c(btn.count() == 1 and btn.is_enabled() and btn.inner_text().strip() == L["meterRetry"], "failure: the button comes back as ‘Try again’")
    c(page.evaluate("localStorage.getItem('etv.sent.ng')") is None, "failure: nothing is remembered as sent")
    M.post_mode = "ok"
    btn.click()
    page.wait_for_selector(".vsend .m-ok")
    c([p["ok"] for p in M.posts] == [False, True] and M.posts[0]["body"] == M.posts[1]["body"], "retry sends the same payload once more")
    S.close(c, allow_console=True)


@test
def meter_failures(c):
    """Compteur injoignable (erreur réseau, erreur 500, réponse absurde, aucune réponse en 6 s) : la partie collective disparaît sans bruit,
    sans erreur de page, la carte et le reste marchent ; « Réessayer » dans « Comment ça marche ? » ; adresse vide : aucune requête externe."""
    base = meter_base()
    for mode in ("abort", "500", "garbage"):
        S = Session(CTX["browser"], width=390, height=844)
        M = MeterMock(S.ctx, DIST["prog"], get=mode)
        page = S.page
        page.goto(base + "/index.html")
        page.wait_for_selector("#mapWrap .mk")
        page.wait_for_function("meter.status === 'fail'")
        c(page.locator("[data-meter] .meter, [data-meter] .meter-wait").count() == 0, f"{mode}: no meter shown")
        c(page.locator(".meter-slot:not([hidden])").count() == 0, f"{mode}: the slot is gone, no placeholder left")
        c(not S.errors, f"{mode}: no page error ({S.errors[:2]})")
        c(page.locator("#mapWrap .mk").count() >= 15, f"{mode}: the map works as usual")
        open_country(page, "566", "en")
        page.wait_for_selector(".theme-grid")
        c(page.locator('[data-meter="country"] .meter').count() == 0, f"{mode}: no country meter on the start screen")
        c(len(M.gets) == 1, f"{mode}: no retry storm ({len(M.gets)} GET)")
        if mode == "abort":
            # « Réessayer » apparaît dans « Comment ça marche ? » seulement après un échec, et recharge
            page.goto(base + "/index.html#/ng/en/values/done")
            wait_view(page, "valres")
            ax = page.evaluate("VALUES.map(v => v.ax)")
            vset(page, [2 * a for a in ax])
            page.evaluate("rerender()")
            page.click(".v-how summary")
            retry = page.locator("[data-go='vretry']")
            c(retry.is_visible(), "after a failure: ‘Try loading it again’ inside the ‘How does this work?’ disclosure")
            M.get_mode = "ok"
            retry.click()
            page.wait_for_selector('.vcard [data-meter="africa"] .mbar')
            c(len(M.gets) == 2 and page.locator("[data-go='vretry']:visible").count() == 0, "retry reads the meter again; the link goes away")
            c(heading_ok(heading_levels(page)), f"values result with meters: heading order {heading_levels(page)}")
        S.close(c, allow_console=True)
    # aucune réponse : abandon au bout de 6 s
    S = Session(CTX["browser"], width=390, height=844)
    M = MeterMock(S.ctx, DIST["prog"], get="hang")
    page = S.page
    t0 = time.time()
    page.goto(base + "/index.html")
    page.wait_for_selector("#mapWrap .mk")
    c(page.locator('.meter-slot[data-meter="africa"][data-state="loading"]').count() == 1, "while loading: space is reserved (placeholder)")
    page.wait_for_function("meter.status === 'fail'", timeout=9000)
    dt = time.time() - t0
    c(5.5 <= dt <= 8.5, f"gives up after about 6 s ({dt:.1f} s)")
    c(page.locator(".meter-slot:not([hidden])").count() == 0 and not S.errors, "…and hides the slot without an error")
    for r in M.pending:
        r.abort()
    S.close(c, allow_console=True)
    # adresse vide (le site du dépôt) : aucune requête externe, aucun bouton, aucun compteur
    S = Session(CTX["browser"], width=390, height=844)
    page = S.page
    page.goto(CTX["base"] + "/index.html")
    page.wait_for_selector("#mapWrap .mk")
    page.wait_for_timeout(300)
    c(page.evaluate("[meter.status, __etv.METER_ENDPOINT]") == ["off", ""], "empty endpoint: collective features are off")
    c(page.locator("[data-meter], .meter, .meter-slot, [data-go='vsend']").count() == 0, "empty endpoint: no meter, no slot, no send button on the map")
    page.goto(CTX["base"] + "/index.html#/ng/en/values/done")
    wait_view(page, "valres")
    page.evaluate("VALUES.forEach(v => state.vals[v.id] = v.ax * 2); save(); rerender()")
    page.wait_for_selector(".vcard .mmark")
    c(page.locator("[data-meter], .vsend, [data-go='vsend']").count() == 0, "empty endpoint: the personal bar shows, nothing collective")
    c(page.evaluate("document.querySelector('.v-how')") is not None and page.locator("[data-go='vretry']:visible").count() == 0, "empty endpoint: no retry link")
    page.wait_for_timeout(200)
    S.close(c)    # Session.close vérifie qu'aucune requête externe n'est partie


@test
def meter_build(c):
    """Le build : lit meter.config.json (--endpoint le remplace), refuse une adresse non https, écrit meter/countries.json et recopie flags/ ;
    il valide src/values.js (10 énoncés, identifiants uniques, 5 sens +1 et 5 sens −1, 5 langues) et échoue sinon."""
    node = os.path.join(ROOT, "tools", "build.js")
    cfg = json.load(open(os.path.join(ROOT, "meter.config.json"), encoding="utf8"))
    c(cfg == {"endpoint": ""}, f"meter.config.json is empty in the repository: collective features off ({cfg})")
    idx = open(os.path.join(ROOT, "index.html"), encoding="utf8").read()
    c('const METER_ENDPOINT = "";' in idx, "repository build: METER_ENDPOINT is empty")

    def build(*args):
        out = tempfile.mkdtemp(prefix="etv-b4-")
        return subprocess.run(["node", node, "--out", out, *args], capture_output=True, text=True, timeout=180), out

    r, out = build("--endpoint", "https://m.example.test/")
    try:
        page_ = open(os.path.join(out, "index.html"), encoding="utf8").read()
        c(r.returncode == 0 and 'const METER_ENDPOINT = "https://m.example.test";' in page_, "--endpoint: used, trailing slash removed")
        c("meter endpoint https://m.example.test" in r.stdout, "the build says which endpoint it uses")
        art = open(os.path.join(out, "artifact.html"), encoding="utf8").read()
        c('const METER_ENDPOINT = "https://m.example.test";' in art, "artifact.html gets it too")
        cc = json.load(open(os.path.join(out, "meter", "countries.json"), encoding="utf8"))
        c(cc == sorted(cc) and "ng" in cc and "fr" in cc and "ke" in cc and len(cc) == len(set(cc)) and len(cc) >= 55 and all(re.fullmatch(r"[a-z]{2}", x) for x in cc), f"meter/countries.json: {len(cc)} codes, sorted, with France")
        repo_cc = json.load(open(os.path.join(ROOT, "meter", "countries.json"), encoding="utf8"))
        c(repo_cc == cc, "the committed meter/countries.json is up to date")
        c(sorted(os.listdir(os.path.join(out, "flags"))) == sorted(os.listdir(os.path.join(ROOT, "flags"))), "flags/ copied next to the page in --out")
    finally:
        shutil.rmtree(out, ignore_errors=True)
    r, out = build("--endpoint", "http://insecure.example.test")
    try:
        page_ = open(os.path.join(out, "index.html"), encoding="utf8").read()
        c(r.returncode == 0 and 'const METER_ENDPOINT = "";' in page_ and "WARN" in r.stdout and "https" in r.stdout, "an address that is not https turns the feature off with a warning")
    finally:
        shutil.rmtree(out, ignore_errors=True)
    r, out = build("--endpoint", "")
    try:
        c('const METER_ENDPOINT = "";' in open(os.path.join(out, "index.html"), encoding="utf8").read() and "WARN" not in r.stdout, "--endpoint '' keeps it off, no warning")
    finally:
        shutil.rmtree(out, ignore_errors=True)
    # copie du dépôt : le fichier de configuration et le validateur des valeurs
    cp = tempfile.mkdtemp(prefix="etv-b4-repo-")
    try:
        for d in ("src", "tools"):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(cp, d))
        shutil.copy(os.path.join(ROOT, "meter.config.json"), cp)

        def run(label, want_ok, needle=None):
            r = subprocess.run(["node", os.path.join(cp, "tools", "build.js"), "--out", os.path.join(cp, "out")], capture_output=True, text=True, timeout=180)
            out_ = r.stdout + r.stderr
            c((r.returncode == 0) == want_ok, f"{label}: exit code {r.returncode} ({out_[-200:]})")
            if needle:
                c(re.search(needle, out_, re.I) is not None, f"{label}: message mentions {needle} ({out_[-200:]})")
            return r

        json.dump({"endpoint": "https://cfg.example.test/"}, open(os.path.join(cp, "meter.config.json"), "w"))
        run("config file with an endpoint", True)
        c('const METER_ENDPOINT = "https://cfg.example.test";' in open(os.path.join(cp, "out", "index.html"), encoding="utf8").read(), "meter.config.json: endpoint read from the file")
        json.dump({"endpoint": ""}, open(os.path.join(cp, "meter.config.json"), "w"))
        run("config file empty", True)
        vf = os.path.join(cp, "src", "values.js")
        orig = open(vf, encoding="utf8").read()
        c(re.search(r"ax:\s*-1", orig) is not None, "values.js uses ax: -1 / +1")
        first_minus = re.search(r"ax:\s*-1", orig)
        open(vf, "w", encoding="utf8").write(orig[:first_minus.start()] + "ax: 1" + orig[first_minus.end():])
        run("values.js with 6 liberal and 4 conservative statements", False, r"values|ax|balance|5")
        open(vf, "w", encoding="utf8").write(re.sub(r"\n\s*sw:\s*\{[^}]*\},?", "\n", orig, count=1))
        run("values.js with a missing translation", False, r"values|sw")
        open(vf, "w", encoding="utf8").write(orig)
        run("values.js restored", True)
    finally:
        shutil.rmtree(cp, ignore_errors=True)


@test
def meter_worker(c):
    """Le code serveur (meter/worker.js, schema.sql) : test Node avec une fausse base D1 et, si Node a node:sqlite, un vrai SQLite."""
    r = subprocess.run(["node", "--no-warnings", os.path.join(ROOT, "meter", "test.mjs")], capture_output=True, text=True, timeout=120)
    out = (r.stdout + r.stderr).strip()
    m = re.search(r"meter worker: (\d+) checks passed", out)
    c(r.returncode == 0 and m is not None, f"node meter/test.mjs: {out[-300:]}")
    c(int(m.group(1)) >= 100, f"{m.group(1)} checks in the Worker test")
    NOTES.append("meter worker: " + out.splitlines()[-1] + (" (real SQLite included)" if "real SQLite" in out else " (fake D1 only)"))
    for f in ("worker.js", "schema.sql", "wrangler.toml", "README.md", "test.mjs", "countries.json"):
        c(os.path.exists(os.path.join(ROOT, "meter", f)), f"meter/{f} exists")
    toml = open(os.path.join(ROOT, "meter", "wrangler.toml"), encoding="utf8").read()
    c("[observability]" in toml and "enabled = false" in toml and 'binding = "DB"' in toml, "wrangler.toml: no request logs, DB binding")
    rd = open(os.path.join(ROOT, "meter", "README.md"), encoding="utf8").read()
    c(all(k in rd for k in ("wrangler d1 create", "schema.sql", "wrangler deploy", "meter.config.json", "48")), "meter/README.md walks through the steps")


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
        for p in procs + ([CTX["meter_proc"]] if CTX.get("meter_proc") else []):
            p.terminate()
        for d in (CTX.get("tmp"), CTX.get("meter_dir")):
            if d:
                shutil.rmtree(d, ignore_errors=True)
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
