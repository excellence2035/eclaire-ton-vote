
/* ================== Éditions ==================
   Chaque pays a son fichier data/<cc>.json (questionnaire « ed » ou page d'information « info »), chargé à la demande.
   CATALOG, généré par tools/build.js, dit sans rien charger quels pays en ont un, dans quelles langues, et quand a lieu le vote. */
const DATA = {};
const A3CC = {};
Object.entries(CATALOG).forEach(([cc, c]) => { if (c.a3) A3CC[c.a3] = cc; });
/* Code ISO alpha-2 en minuscules → identifiant numérique de la carte (liens vers un pays sans édition, par ex. #/ao) */
const A2ID = {};
Object.entries(AFRICA).forEach(([id, c]) => { if (c.a2) A2ID[c.a2.toLowerCase()] = id; });
const ccOf = id => A3CC[id] || (AFRICA[id] && AFRICA[id].a2 ? AFRICA[id].a2.toLowerCase() : null);
const catFor = id => (A3CC[id] ? CATALOG[A3CC[id]] : null);
const UP_FROM = "2026-10", UP_TO = "2027-12-31";

/* ================== État ==================
   country : le pays affiché (null sur la carte) ; ac : le pays auquel appartiennent les réponses en cours
   (elles survivent à un passage par la carte et à un rechargement de l'onglet ; choisir un autre questionnaire les remplace). */
const state = { ui: "en", uiChosen: false, country: null, ac: null, place: null, view: null, priorities: [], order: [], nPrio: 0, i: 0, answers: {}, double: {}, tab: 0, ret: null, pending: null, loadCc: null, loadRest: "", vals: {}, vi: 0, vseen: false };
const PRIOR_ALL = 3, PRIOR_THEME = 1;
/* Lecture des résultats : couverture minimale pour être classé, égalité avec le premier, scores égaux (ordre alphabétique),
   premier aperçu, réponses presque toutes identiques. */
const COV_MIN = 0.4, TIE = 0.03, EQ = 0.005, EARLY = 8, STRAIGHT = 0.8;
let TAP_GUARD = 350;      // ms : un tapotement sur une réponse juste après l'affichage d'une question est ignoré (double tapotement)
let LOAD_TIMEOUT = 20000; // ms : au-delà, le chargement d'une édition est abandonné (écran d'erreur avec « Réessayer »)
const TABS = ["ranking", "issues", "questions", "method"];
const BRAND = "Vote";
const $ = id => document.getElementById(id);
const t = () => T[state.ui] || T.en;
const edCache = {};
const ed = () => {
  const key = state.country + ":" + state.ui;
  if (!edCache[key]) edCache[key] = localizeEdition(DATA[state.country], state.ui);
  return edCache[key];
};
const nn = n => String(n).padStart(2, "0");
const C = () => state.ui === "fr" ? " :" : ":";
const pctTxt = s => Math.round(s * 100) + '<span class="pu"> %</span>';
const pctPlain = s => Math.round(s * 100) + (state.ui === "fr" ? " %" : "%");
const esc = s => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const uniq = a => a.filter((v, i) => v && a.indexOf(v) === i);
const label = p => `${p.sigle} · ${p.nom}`;
/* Isolation bidirectionnelle (FSI … PDI) : un nom latin dans une phrase arabe garde son ordre, parenthèses comprises. */
const ISO = [String.fromCharCode(0x2068), String.fromCharCode(0x2069)];
const pname = p => ISO[0] + p.nom + ISO[1];
const plabel = p => ISO[0] + `${p.nom} (${p.sigle})` + ISO[1];
const psig = p => ISO[0] + p.sigle + ISO[1];
const hname = p => esc(pname(p));
const langOf = code => LANGS.find(l => l.code === code);
const locale = () => (langOf(state.ui) || LANGS[0]).locale;
function listFmt(a) {
  if (a.length < 2) return a.join("");
  try { return new Intl.ListFormat(locale(), { style: "long", type: "conjunction" }).format(a); } catch (e) { return a.join(", "); }
}
const now = () => (window.performance && performance.now ? performance.now() : Date.now());

/* Traduction d'une édition : le texte de base est remplacé, champ par champ, par celui de I18N quand il existe. */
function localizeEdition(D, lang) {
  const base = D.kind === "info" ? D.info : D.ed;
  const E = JSON.parse(JSON.stringify(base));
  E.kind = D.kind; E.cc = D.id; E.a3 = D.a3; E.baseLang = D.lang; E.meta = D.meta || {}; E.src = D.src || {};
  E.langs = LANGS.map(l => ({ code: l.code, label: l.code.toUpperCase(), name: l.name, ready: D.langs.includes(l.code) }));
  const L = lang !== D.lang && D.i18n && D.i18n[lang];
  E.lang = L ? lang : D.lang;
  // Note de l'édition (report, doute sur la date…) : traduite quand la traduction fournit « note »
  E.note = E.meta.note || ""; E.noteLang = D.lang;
  if (L && E.note && typeof L.note === "string" && L.note.trim()) { E.note = L.note; E.noteLang = lang; }
  if (!L) return E;
  const same = (a, b) => Array.isArray(a) && Array.isArray(b) && a.length === b.length;
  ["strip", "stripDate", "status", "why"].forEach(k => { if (typeof L[k] === "string" && L[k]) E[k] = L[k]; });
  ["facts", "system", "others"].forEach(k => { if (same(L[k], E[k])) E[k] = L[k]; });
  if (D.kind === "info") {
    if (same(L.actors, E.actors)) E.actors = E.actors.map((a, i) => [L.actors[i][0] || a[0], L.actors[i][1] || a[1], a[2]]);
    return E;
  }
  E.parties.forEach(p => {
    if (L.tags && L.tags[p.id]) p.tag = L.tags[p.id];
    if (L.commits && L.commits[p.id]) p.commit = p.commit.map((c, i) => [L.commits[p.id][i] || c[0], c[1]]);
    if (p.candNote && L.candNotes && L.candNotes[p.id]) p.candNote = L.candNotes[p.id];
  });
  E.themes.forEach(th => { if (L.themes && L.themes[th.id]) { th.name = L.themes[th.id][0]; th.min = L.themes[th.id][1]; } });
  E.questions.forEach((q, i) => {
    const tq = L.q && L.q[i];
    if (!tq) return;
    ["short", "text", "ctx"].forEach(k => { if (tq[k]) q[k] = tq[k]; });
    Object.keys(q.cells).forEach(pid => { if (tq.n && tq.n[pid]) q.cells[pid].n = tq.n[pid]; });
    if (q.nd) Object.keys(q.nd).forEach(pid => { if (tq.nd && tq.nd[pid]) q.nd[pid] = tq.nd[pid]; });
  });
  return E;
}

/* Couleurs des partis : --c-<édition>-<parti>, clair et sombre, injectées au chargement de l'édition.
   Dans une édition, deux partis doivent se distinguer (ΔE CIE76 ≥ MIN_DE, dans chaque thème) et le sigle doit rester lisible
   sur le badge (contraste ≥ 4,5:1 avec --on-party). Les couleurs de l'édition sont gardées quand elles conviennent ; sinon on
   essaie la même teinte plus claire ou plus foncée, puis une palette fixe d'une dizaine de teintes (aussi utilisée quand
   l'édition ne donne aucune couleur). Les partis sont traités dans l'ordre de l'édition : les premiers gardent leur couleur. */
const cssId = s => String(s).toLowerCase().replace(/[^a-z0-9_-]/g, "-");
const pvar = pid => `--c-${cssId(state.country)}-${cssId(pid)}`;
const hex = c => (/^#[0-9a-f]{3,8}$/i.test(c || "") ? c : "");
const MIN_DE = 20, MIN_TEXT = 4.6, ON_PARTY = ["#FFFFFF", "#110F19"];
const PALETTE = [["#B3261E", "#FF8A80"], ["#1D5FA8", "#7FB6F5"], ["#2D7D46", "#7BD389"], ["#7B3FA0", "#C792EA"], ["#B85C00", "#FFB070"],
  ["#00796B", "#5CD3C2"], ["#B0236B", "#F78DB8"], ["#7A6A00", "#E6D25A"], ["#455A64", "#9FB4BF"], ["#6D4C41", "#C9A28F"]];
const rgbOf = h => { h = h.replace("#", ""); if (h.length < 6) h = h.replace(/./g, "$&$&"); return [0, 2, 4].map(i => parseInt(h.substr(i, 2), 16)); };
const hexOf = c => "#" + c.map(v => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0")).join("");
const lin = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
const unlin = v => 255 * (v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055);
const lumOf = c => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
const contrastOf = (a, b) => { const x = lumOf(a), y = lumOf(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
function toLab(c) {
  const r = lin(c[0]), g = lin(c[1]), b = lin(c[2]);
  const f = t => (t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116);
  const x = f((0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047), y = f(0.2126 * r + 0.7152 * g + 0.0722 * b), z = f((0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883);
  return [116 * y - 16, 500 * (x - y), 200 * (y - z)];
}
function fromLab(l) {
  const fy = (l[0] + 16) / 116, fx = fy + l[1] / 500, fz = fy - l[2] / 200;
  const g = t => (t * t * t > 0.008856 ? t * t * t : (t - 16 / 116) / 7.787);
  const x = g(fx) * 0.95047, y = g(fy), z = g(fz) * 1.08883;
  return [unlin(3.2406 * x - 1.5372 * y - 0.4986 * z), unlin(-0.9689 * x + 1.8758 * y + 0.0415 * z), unlin(0.0557 * x - 0.204 * y + 1.057 * z)];
}
const deltaE = (a, b) => Math.sqrt(Math.pow(a[0] - b[0], 2) + Math.pow(a[1] - b[1], 2) + Math.pow(a[2] - b[2], 2));
/* Éclaircit (thème sombre, texte foncé) ou assombrit (thème clair, texte blanc) jusqu'à un sigle lisible ; renvoie la couleur en Lab. */
function fitLab(lab, k) {
  const on = rgbOf(ON_PARTY[k]);
  let l = lab.slice();
  for (let i = 0; i < 60 && contrastOf(fromLab(l), on) < MIN_TEXT; i++) l[0] += k ? 1.5 : -1.5;
  return toLab(fromLab(l).map(v => Math.max(0, Math.min(255, v))));
}
/* [clair, sombre] : { identifiant du parti : "#rrggbb" } */
function partyColours(parties) {
  return [0, 1].map(k => {
    const chosen = [], out = {}, on = rgbOf(ON_PARTY[k]);
    parties.forEach((p, i) => {
      const given = hex((p.col || [])[k]) || hex((p.col || [])[0]) || PALETTE[i % PALETTE.length][k];
      const base = toLab(rgbOf(given));
      const cands = [{ lab: base, hex: given.length < 7 ? hexOf(rgbOf(given)) : given.slice(0, 7) }];
      [-1, 1, -2, 2, -3, 3].forEach(m => cands.push({ lab: [base[0] + m * 9, base[1], base[2]] }));
      PALETTE.forEach(pc => cands.push({ lab: toLab(rgbOf(pc[k])) }));
      let best = null, bestD = -1;
      for (let j = 0; j < cands.length; j++) {
        const c = cands[j];
        // la couleur de l'édition est gardée telle quelle quand le sigle y est déjà lisible
        const asIs = c.hex && contrastOf(rgbOf(c.hex), on) >= MIN_TEXT;
        const lab = asIs ? c.lab : fitLab(c.lab, k);
        const d = chosen.length ? Math.min.apply(null, chosen.map(x => deltaE(x, lab))) : 999;
        if (d > bestD) { best = { lab: lab, hex: asIs ? c.hex : hexOf(fromLab(lab)) }; bestD = d; }
        if (d >= MIN_DE) break;
      }
      chosen.push(best.lab);
      out[p.id] = best.hex;
    });
    return out;
  });
}
function injectColours(D) {
  if (D.kind !== "ed" || !D.ed || $("pc-" + cssId(D.id))) return;
  const cols = partyColours(D.ed.parties);
  const vars = k => D.ed.parties.map(p => `--c-${cssId(D.id)}-${cssId(p.id)}:${cols[k][p.id]}`).join(";");
  const st = document.createElement("style");
  st.id = "pc-" + cssId(D.id);
  st.textContent = `:root{${vars(0)}}@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){${vars(1)}}}:root[data-theme="dark"]{${vars(1)}}`;
  (document.head || document.documentElement).appendChild(st);
}
/* Un seul téléchargement par pays à la fois (pays rouvert pendant le chargement) ; abandon au bout de LOAD_TIMEOUT. */
const inflight = {};
function loadEdition(cc) {
  if (DATA[cc]) return Promise.resolve(DATA[cc]);
  if (inflight[cc]) return inflight[cc];
  const ac = typeof AbortController === "function" ? new AbortController() : null;
  const p = new Promise((resolve, reject) => {
    const timer = setTimeout(() => { if (ac) ac.abort(); reject(new Error("timeout")); }, LOAD_TIMEOUT);
    fetch(`data/${encodeURIComponent(cc)}.json`, ac ? { signal: ac.signal } : {})
      .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(D => {
        if (!D || D.id !== cc || !(D.ed || D.info)) throw new Error("bad data");
        DATA[cc] = D;
        injectColours(D);
        return D;
      })
      .then(D => { clearTimeout(timer); resolve(D); }, e => { clearTimeout(timer); reject(e); });
  });
  inflight[cc] = p;
  const done = () => { delete inflight[cc]; };
  p.then(done, done);
  return p;
}

function badge(p, size) {
  return `<span class="badge ${size || ""}" style="--pc:var(${pvar(p.id)}, var(--accent))" aria-hidden="true">${esc(p.sigle)}</span>`;
}
function srcObj(id) {
  const D = state.country && DATA[state.country];
  return (D && D.src && D.src[id]) || SRC_AF[id] || null;
}
/* Date d'une source : ISO (AAAA, AAAA-MM, AAAA-MM-JJ) mise en forme dans la langue de l'interface ; un texte libre reste tel quel. */
const srcDate = d => (/^\d{4}(-\d\d){0,2}$/.test(d || "") ? fmtDate(d) : d);
function srcA(s) {
  return s ? `<a href="${esc(s.u)}" target="_blank" rel="noopener">${esc(s.o)}, ${esc(srcDate(s.d))}</a>` : "";
}
const srcLink = id => srcA(srcObj(id));
const srcLine = (ids, L, style) => {
  const links = uniq(ids || []).map(srcLink).filter(Boolean);
  return links.length ? `<p class="src muted"${style ? ` style="${style}"` : ""}>${L.source}${C()} ${links.join(" · ")}</p>` : "";
};
/* Candidat·e à la présidentielle, ou dirigeant·e du parti (élection sans présidentielle, candidat·e pas encore désigné·e). */
function candLine(p, E, L, short) {
  const lead = E.role === "leader" || !!p.candNote;
  return `${lead ? L.partyLeader : L.presCand}${C()} ${esc(p.cand)}${p.candNote && !short ? ` <span class="cand-note">(${esc(p.candNote)})</span>` : ""}`;
}
function noteHTML(E, L) {
  return E.note ? `<p class="caveat"><b>${L.noteLabel}${C()}</b> <span lang="${esc(E.noteLang)}" dir="auto">${esc(E.note)}</span></p>` : "";
}

/* ================== Pays, dates et langues ================== */
const namesCache = {};
function cname(id, lang) {
  lang = lang || state.ui;
  const c = AFRICA[id];
  if (!c) return id === "732" ? (lang === "fr" ? "Sahara occidental" : "Western Sahara") : id;
  const key = lang + id;
  if (namesCache[key]) return namesCache[key];
  let n = null;
  if (lang === "fr") n = c.fr; else if (lang === "en") n = c.en;
  else {
    try { n = new Intl.DisplayNames([(langOf(lang) || {}).locale || lang], { type: "region" }).of(c.a2); } catch (e) { n = null; }
    if (!n || n === c.a2) n = c.en;
  }
  return (namesCache[key] = n);
}
/* Nom du pays d'une édition : par son code numérique (Afrique), sinon le nom de l'édition (France). */
function edName(E) { return E.a3 && AFRICA[E.a3] ? cname(E.a3) : E.name; }
function catName(cc) {
  const c = CATALOG[cc];
  if (c && c.a3 && AFRICA[c.a3]) return cname(c.a3);
  if (DATA[cc]) return (DATA[cc].ed || DATA[cc].info).name;
  try { const n = new Intl.DisplayNames([locale()], { type: "region" }).of(String(cc).toUpperCase()); if (n) return n; } catch (e) { }
  return String(cc).toUpperCase();
}
function fmtDate(iso) {
  const parts = iso.split("-").map(Number);
  const d = new Date(Date.UTC(parts[0], (parts[1] || 1) - 1, parts[2] || 15, 12));
  const opts = parts.length === 3 ? { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" } : parts.length === 2 ? { month: "long", year: "numeric", timeZone: "UTC" } : { year: "numeric", timeZone: "UTC" };
  try { return new Intl.DateTimeFormat(locale(), opts).format(d); } catch (e) { return iso; }
}
function evText(ev) {
  const L = t();
  const ty = L.types[ev.t] || ev.t;
  const w = ev.q === "range" ? L.when.range(fmtDate(ev.d), fmtDate(ev.d2)) : (L.when[ev.q] || L.when.exact)(fmtDate(ev.d));
  return `${ty} · ${w}`;
}
/* Les dates d'une édition (META) sont plus récentes que le calendrier général (AFRICA) : elles priment. */
function evsFor(id) {
  const cat = catFor(id);
  if (cat && cat.ev && cat.ev.length) return cat.ev;
  return (AFRICA[id] && AFRICA[id].ev) || [];
}
function isUp(id) {
  const cat = catFor(id);
  if (cat && cat.ev && cat.ev.length) return cat.ev.some(e => e.d <= UP_TO && (e.d2 || e.d) >= UP_FROM);
  return !!(AFRICA[id] && AFRICA[id].up);
}
function statusLine(id) {
  const c = AFRICA[id];
  if (!c) return t().legDisputed;
  if (isUp(id) || catFor(id)) return evsFor(id).map(evText).join(state.ui === "ar" ? " ؛ " : " ; ") || t().legNone;
  return t().legNone;
}
function kindLine(cat, L) { return cat ? (cat.kind === "ed" ? "✓ " + L.legReady : "ⓘ " + L.legInfo) : ""; }

/* ================== Drapeau, silhouette et bandeau du pays ==================
   Le drapeau est un fichier flags/<cc>.svg à côté de la page (jamais incorporé) ; décoratif (alt vide) puisque le nom est toujours
   écrit à côté ; s'il ne se charge pas, il disparaît et le bandeau marche sans lui. La silhouette vient du tracé de la carte
   (src/mapdata.js) : cadre serré sur le pays, toutes ses parties (archipels compris), contour d'au moins 1 px pour les îlots. */
const FR_PTS = [[2.55, 51.1], [1.6, 50.95], [1.55, 50.2], [1.1, 49.93], [0.1, 49.5], [-1.25, 49.7], [-1.6, 49.65], [-1.5, 48.65], [-2.0, 48.65], [-3.4, 48.85], [-4.75, 48.5], [-4.7, 48.05], [-3.5, 47.75], [-3.0, 47.5], [-2.2, 47.25], [-2.2, 46.9], [-1.2, 46.15], [-1.05, 45.6], [-1.25, 44.65], [-1.78, 43.37], [-0.7, 43.05], [0.7, 42.8], [1.45, 42.45], [2.0, 42.35], [3.15, 42.43], [3.0, 43.0], [3.7, 43.4], [4.6, 43.4], [5.35, 43.3], [5.95, 43.1], [6.75, 43.4], [7.5, 43.78], [7.0, 44.2], [6.85, 45.1], [7.1, 45.9], [6.1, 46.25], [6.9, 47.3], [7.55, 47.6], [7.55, 48.1], [8.2, 48.98], [6.4, 49.45], [5.8, 49.55], [4.85, 50.1], [4.2, 50.3], [3.6, 50.45], [3.1, 50.75]];
const FR_CORSE = [[8.6, 42.95], [9.4, 43.0], [9.55, 42.2], [9.2, 41.4], [8.7, 41.6], [8.55, 42.3]];
const FR_PATH = [FR_PTS, FR_CORSE].map(poly => "M" + poly.map(q => ((q[0] + 5.2) * 20.7).toFixed(1) + " " + ((51.2 - q[1]) * 30).toFixed(1)).join("L") + "Z").join("");
const shapeBoxes = {};
/* Cadre d'un tracé (mesuré une fois, dans un svg caché : getBBox demande un élément rendu) */
function shapeBox(key, d) {
  if (shapeBoxes[key]) return shapeBoxes[key];
  let box = null;
  try {
    const NS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("width", "0"); svg.setAttribute("height", "0");
    svg.style.cssText = "position:absolute;visibility:hidden;pointer-events:none";
    const pa = document.createElementNS(NS, "path");
    pa.setAttribute("d", d);
    svg.appendChild(pa);
    document.body.appendChild(svg);
    const b = pa.getBBox();
    document.body.removeChild(svg);
    if (b.width > 0 || b.height > 0) box = [b.x, b.y, Math.max(b.width, 0.5), Math.max(b.height, 0.5)];
  } catch (e) { box = null; }
  return (shapeBoxes[key] = box);
}
const flagCc = id => id === "fr" ? "fr" : (AFRICA[id] && AFRICA[id].a2 ? AFRICA[id].a2.toLowerCase() : null);
function flagImg(cc, w, h, cls, eager) {
  if (!cc) return "";
  return `<img class="flag ${cls || ""}" src="flags/${cc}.svg" alt="" width="${w}" height="${h}" decoding="async"${eager ? "" : ' loading="lazy"'}>`;
}
/* Une image de drapeau qui ne se charge pas disparaît (pas d'icône cassée) */
document.addEventListener("error", e => { const el = e.target; if (el && el.tagName === "IMG" && el.classList.contains("flag")) el.hidden = true; }, true);
function silhouetteSVG(id) {
  const d = id === "fr" ? FR_PATH : MAP.c[id];
  if (!d) return "";
  const b = shapeBox(id, d);
  if (!b) return "";
  const pad = Math.max(b[2], b[3]) * 0.06 + 0.4;
  return `<svg class="cb-shape" viewBox="${[b[0] - pad, b[1] - pad, b[2] + 2 * pad, b[3] + 2 * pad].map(v => v.toFixed(2)).join(" ")}" aria-hidden="true" focusable="false"><path d="${d}"></path></svg>`;
}
/* Ligne d'élection du bandeau : dates connues, ou « pas d'élection nationale avant fin 2027 » */
function bannerLine(id) {
  if (id === "fr") return ((CATALOG.fr && CATALOG.fr.ev) || []).map(evText).join(state.ui === "ar" ? " ؛ " : " ; ");
  return statusLine(id);
}
/* Grand bandeau (choix de la langue) : drapeau, silhouette, nom du pays, ligne d'élection. id : identifiant de la carte, ou « fr ». */
function bannerHTML(id) {
  const name = id === "fr" ? catName("fr") : cname(id);
  const line = bannerLine(id);
  return `<div class="cbanner">
    <div class="cb-art">${flagImg(flagCc(id), 72, 54, "cb-flag", true)}${silhouetteSVG(id)}</div>
    <p class="cb-name">${esc(name)}</p>
    ${line ? `<p class="st cb-line">${esc(line)}</p>` : ""}
  </div>`;
}
/* Bandeau compact : drapeau 32 × 24 + nom (écrans du pays) */
function bandHTML(cc, name) { return `<span class="cband">${flagImg(cc, 32, 24, "cb-flag-sm")}<b>${esc(name)}</b></span>`; }
const edCc = E => (E.a3 && AFRICA[E.a3] ? flagCc(E.a3) : /^[a-z]{2}$/.test(E.cc || "") ? E.cc : null);
/* Pays affiché (code ISO alpha-2 minuscule) : l'édition ouverte, ou le pays sans édition */
function curCc() { return state.country || (state.place && AFRICA[state.place] ? flagCc(state.place) : null); }

/* ================== Mémoire : la session (cet onglet) et la langue (cet appareil) ==================
   sessionStorage garde le questionnaire en cours (langue, pays, priorités, ordre, réponses, « compte double », question,
   onglet) : un rechargement ou un onglet mis en veille par le téléphone ne perd rien ; rien ne part sur le réseau.
   localStorage garde seulement la langue choisie. Chaque accès est protégé : sans stockage (navigation privée,
   iframe en bac à sable), l'application marche quand même. */
const SKEY = "etv.session", UKEY = "etv.ui";
function getItem(kind, k) { try { const s = window[kind]; return s ? s.getItem(k) : null; } catch (e) { return null; } }
function setItem(kind, k, v) { try { const s = window[kind]; if (s) { if (v == null) s.removeItem(k); else s.setItem(k, v); } } catch (e) { } }
function save() {
  setItem("sessionStorage", SKEY, JSON.stringify({ v: 1, ui: state.ui, uiChosen: state.uiChosen, country: state.ac, priorities: state.priorities, order: state.order, nPrio: state.nPrio, answers: state.answers, double: state.double, i: state.i, tab: state.tab, ret: state.ret, vals: state.vals, vi: state.vi, vseen: state.vseen }));
}
function restore() {
  let s = null;
  try { s = JSON.parse(getItem("sessionStorage", SKEY) || "null"); } catch (e) { s = null; }
  if (!s || typeof s !== "object" || s.v !== 1) return;
  if (T[s.ui] && langOf(s.ui)) state.ui = s.ui;
  state.uiChosen = s.uiChosen === true;
  // Module « valeurs » : indépendant du pays et du questionnaire (réponses −2…2, ou null pour passée)
  state.vals = {};
  if (s.vals && typeof s.vals === "object") VALUES.forEach(v => { const a = s.vals[v.id]; if (a === null || [-2, -1, 0, 1, 2].includes(a)) state.vals[v.id] = a; });
  state.vi = Number.isInteger(s.vi) && s.vi >= 0 && s.vi < VALUES.length ? s.vi : 0;
  state.vseen = s.vseen === true;
  if (typeof s.country !== "string" || !CATALOG[s.country]) return;
  const ints = a => Array.isArray(a) && a.every(x => Number.isInteger(x) && x >= 0);
  state.ac = s.country;
  state.priorities = Array.isArray(s.priorities) ? s.priorities.filter(x => typeof x === "string").slice(0, 3) : [];
  state.order = ints(s.order) ? s.order : [];
  state.nPrio = Number.isInteger(s.nPrio) && s.nPrio >= 0 ? s.nPrio : 0;
  state.answers = {}; state.double = {};
  if (s.answers && typeof s.answers === "object") Object.keys(s.answers).forEach(k => { const v = s.answers[k]; if (/^\d+$/.test(k) && (v === null || [-2, -1, 0, 1, 2].includes(v))) state.answers[k] = v; });
  if (s.double && typeof s.double === "object") Object.keys(s.double).forEach(k => { if (/^\d+$/.test(k) && s.double[k] === true) state.double[k] = true; });
  state.i = Number.isInteger(s.i) && s.i >= 0 ? s.i : 0;
  state.tab = Number.isInteger(s.tab) && s.tab >= 0 && s.tab < TABS.length ? s.tab : 0;
  state.ret = s.ret && Number.isInteger(s.ret.until) ? { until: s.ret.until } : null;
}
/* Une session restaurée doit correspondre à l'édition chargée (nombre de questions, thèmes) ; sinon on l'écarte en partie. */
function checkSession(E) {
  const n = E.questions.length;
  const okI = x => Number.isInteger(x) && x >= 0 && x < n;
  if (state.order.length !== n || !state.order.every(okI) || new Set(state.order).size !== n) { state.order = []; state.nPrio = 0; state.i = 0; }
  state.nPrio = Math.min(state.nPrio, state.order.length);
  state.i = Math.min(state.i, Math.max(0, state.order.length - 1));
  state.priorities = state.priorities.filter(id => E.themes.some(th => th.id === id));
  Object.keys(state.answers).forEach(k => { if (!okI(+k)) delete state.answers[k]; });
  Object.keys(state.double).forEach(k => { if (!okI(+k)) delete state.double[k]; });
  if (state.ret && !okI(state.ret.until)) state.ret = null;
}
/* Langue de départ : celle choisie sur cet appareil, sinon la première langue du navigateur que l'interface connaît, sinon l'anglais. */
function initialUi() {
  const saved = getItem("localStorage", UKEY);
  if (saved && T[saved] && langOf(saved)) return saved;
  let navs = [];
  try { navs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language]; } catch (e) { navs = []; }
  for (const l of navs) {
    const p = String(l || "").toLowerCase().split(/[-_]/)[0];
    if (T[p] && langOf(p)) return p;
  }
  return "en";
}
function setUi(code, picked) {
  if (!T[code] || !langOf(code)) return;
  state.ui = code;
  if (picked) { state.uiChosen = true; setItem("localStorage", UKEY, code); }
}

/* ================== Adresse et historique ==================
   #/                              la carte
   #/<cc>                          pays choisi : choix de la langue, ou directement la suite si une langue a déjà été choisie dans cet onglet
   #/<cc>/<langue>                 départ (élection + priorités) ou page d'information
   #/<cc>/<langue>/q/<n>           question n (1 = la première dans l'ordre en cours)
   #/<cc>/<langue>/checkpoint      fin des sujets prioritaires
   #/<cc>/<langue>/results[/<onglet>]   onglets : ranking, issues, questions, method
   #/<cc>/<langue>/values[/<n>|/done]   module « valeurs » (10 questions communes) : présentation, question n, position (n'importe quel pays)
   Formes courtes acceptées (certains hébergeurs ne transmettent que « #mot ») : #ke, #cv-pt. Le prototype France : #/fr/fr.
   Les réponses ne vont jamais dans l'adresse.

   Historique, pensé pour le bouton Retour d'Android : chaque nouvel écran ajoute une entrée (pushState), mais le
   questionnaire n'en occupe qu'une, remplacée à chaque question (avance automatique, « Précédente », saut par la barre
   de progression, fin des priorités). Retour depuis une question ramène donc à l'écran d'avant le questionnaire : le
   départ, où « Reprendre » attend avec toutes les réponses, ou les résultats si l'on y corrigeait une réponse ; pas
   38 questions en arrière, ce qui obligerait à « traverser » tout le questionnaire pour en sortir. Pour revenir d'une
   question, il y a « Précédente ». Retour depuis les résultats ramène au questionnaire, là où on l'a quitté. */
let navMode = "replace";   // pour le prochain écran affiché : "push", "push-ret" (question ouverte depuis les résultats), "replace", "none"
let curHash = null;
function parseHash(h) {
  let s = String(h || "").replace(/^#/, "");
  try { s = decodeURIComponent(s); } catch (e) { }
  s = s.trim().toLowerCase();
  const m = /^([a-z]{2})(?:-([a-z]{2}))?$/.exec(s);
  if (m) return { cc: m[1], lang: m[2] || null, rest: [] };
  const parts = s.split("/").filter(Boolean);
  if (!parts.length) return {};
  if (!/^[a-z]{2}$/.test(parts[0])) return { bad: true };
  const lang = parts[1] && /^[a-z]{2}$/.test(parts[1]) ? parts[1] : null;
  return { cc: parts[0], lang, rest: lang ? parts.slice(2) : [] };
}
function hashFor() {
  const v = state.view, ui = state.ui;
  if (v === "info") return `#/${AFRICA[state.place].a2.toLowerCase()}/${ui}`;
  if (v === "loading" || v === "loaderror") return `#/${state.loadCc}/${ui}${state.loadRest}`;
  if (v === "valintro" || v === "valq" || v === "valres") {
    const vb = `#/${curCc()}/${ui}/values`;
    return v === "valq" ? `${vb}/${state.vi + 1}` : v === "valres" ? `${vb}/done` : vb;
  }
  if (!state.country) return "#/";
  const b = `#/${state.country}/${ui}`;
  if (v === "question") return `${b}/q/${state.i + 1}`;
  if (v === "checkpoint") return `${b}/checkpoint`;
  if (v === "results") return `${b}/results${state.tab ? "/" + TABS[state.tab] : ""}`;
  return b;
}
function setHash(h, push, st) {
  const cur = location.hash || "#/";   // une adresse sans # vaut la carte : on ne la touche pas au chargement
  try {
    if (push && cur !== h) history.pushState(st || {}, "", h);
    else if (cur !== h || st) history.replaceState(st || history.state || {}, "", h);
  } catch (e) { }
  curHash = location.hash;
}
function syncUrl() {
  const mode = navMode;
  navMode = "replace";
  if (mode === "none") { curHash = location.hash; return; }
  setHash(hashFor(), mode === "push" || mode === "push-ret", mode === "push-ret" ? { ret: 1 } : mode === "push" ? {} : undefined);
}
function navTo(h) { setHash(h, true, {}); route(location.hash); }
/* Affiche l'écran que décrit l'adresse. Une adresse inconnue ou qui ne correspond plus à la session (question sans
   questionnaire en cours, par ex. un lien partagé) se dégrade vers l'écran le plus proche, et l'adresse est corrigée. */
function route(h) {
  const r = parseHash(h);
  navMode = "replace";
  loadSeq++;
  clearTimeout(advanceTimer); clearTimeout(backTimer);
  closeFiche(); closeQList();
  curHash = location.hash;
  const cat = r.cc ? CATALOG[r.cc] : null;
  const id = cat ? cat.a3 : r.cc ? A2ID[r.cc] : null;
  if (!r.cc || (!cat && !id)) {
    closeLang();
    // Déjà sur la carte (choix de langue annulé, Retour) : on ne la redessine pas, défilement et focus restent en place
    if (state.view === "map" && !r.bad && (r.cc == null)) { syncUrl(); return; }
    return viewMap();
  }
  const onMap = !!(id && AFRICA[id]);
  let lang = r.lang && langOf(r.lang) ? r.lang : null;
  if (!lang) {
    const avail = cat ? cat.langs : LANGS.map(l => l.code);
    if ((state.uiChosen || !onMap) && avail.includes(state.ui)) lang = state.ui;
    else if (!onMap) lang = avail[0];
    else {
      if (location.hash !== "#/" + r.cc) setHash("#/" + r.cc, false);
      if (state.view !== "map") { navMode = "none"; viewMap(); }
      return openLang(id);
    }
    setHash(`#/${r.cc}/${lang}`, false, {});
  }
  closeLang();
  setUi(lang, false);
  const vrest = r.rest[0] === "values" ? r.rest.slice(1) : null;
  if (!cat) return vrest ? viewValues(vrest, id) : viewInfo(id);
  state.loadRest = r.rest.length ? "/" + r.rest.join("/") : "";
  openEdition(r.cc, () => vrest ? viewValues(vrest) : renderStep(r.rest));
}
function renderStep(rest) {
  const D = DATA[state.country];
  if (D.kind === "info") return viewEdInfo();
  const step = rest[0], arg = rest[1];
  const has = state.order.length > 0;
  if (step === "q" && has) {
    const n = parseInt(arg, 10);
    state.i = Math.min(Math.max((n || 1) - 1, 0), state.order.length - 1);
    return viewQuestion();
  }
  if (step === "checkpoint" && has && state.nPrio) return viewCheckpoint();
  if (step === "results" && has) { const k = TABS.indexOf(arg); state.tab = k >= 0 ? k : 0; return viewResults(); }
  return viewStart();
}

/* ================== Calcul ================== */
function accord(v, p) { return 1 - Math.abs(v - p) / 4; }
function weight(qi, inTheme) {
  const d = state.double[qi] ? 2 : 1;
  if (inTheme) return d;
  return d * (state.priorities.includes(ed().questions[qi].theme) ? 2 : 1);
}
function answeredIn(theme) {
  return ed().questions.filter((q, i) => (!theme || q.theme === theme) && typeof state.answers[i] === "number").length;
}
function score(pid, theme) {
  let num = 0, den = 0, k = 0;
  ed().questions.forEach((q, qi) => {
    const v = state.answers[qi];
    if (typeof v !== "number") return;
    if (theme && q.theme !== theme) return;
    const c = q.cells[pid];
    if (!c) return;
    const w = weight(qi, !!theme);
    num += w * accord(v, c.p);
    den += w;
    k++;
  });
  if (!k) return { s: null, k: 0 };
  const prior = theme ? PRIOR_THEME : PRIOR_ALL;
  return { s: (num + prior * 0.5) / (den + prior), k };
}
/* Groupes : « ok » (classé : au moins 2 réponses comparées, 1 par sujet, et couverture ≥ 40 %), « thin » (assez de réponses
   mais couverture < 40 % : montré à part, sans rang), « out » (trop peu). Dans un groupe : par score, puis par sigle quand
   les scores sont égaux (à 0,005 près), jamais dans l'ordre de l'édition. */
const bySig = (x, y) => (x.p.sigle < y.p.sigle ? -1 : x.p.sigle > y.p.sigle ? 1 : 0);
const GROUP = { ok: 0, thin: 1, out: 2 };
function ranking(theme) {
  const min = theme ? 1 : 2;
  const a = answeredIn(theme);
  return ed().parties.map(p => {
    const r = score(p.id, theme);
    const cov = a ? r.k / a : 0;
    const grp = r.k < min ? "out" : cov < COV_MIN ? "thin" : "ok";
    return { p, s: r.s, k: r.k, cov, grp, ok: grp === "ok" };
  }).sort((x, y) => {
    if (x.grp !== y.grp) return GROUP[x.grp] - GROUP[y.grp];
    if (x.grp === "out") return bySig(x, y);
    const d = y.s - x.s;
    return Math.abs(d) < EQ ? bySig(x, y) : d;
  });
}
/* Les partis à moins de 3 points du premier partagent la première place. */
function topGroup(rows) { return rows.filter(r => rows[0].s - r.s < TIE); }
function answeredCount() { return Object.values(state.answers).filter(v => typeof v === "number").length; }
function documented(pid) { return ed().questions.filter(q => q.cells[pid]).length; }
/* Première question pas encore vue (sinon la première passée) dans l'ordre en cours ; -1 s'il n'y en a pas. */
function firstOpen() {
  const k = state.order.findIndex(x => state.answers[x] === undefined);
  return k >= 0 ? k : state.order.findIndex(x => state.answers[x] === null);
}
function lastSeen() {
  for (let k = state.order.length - 1; k >= 0; k--) if (state.answers[state.order[k]] !== undefined) return k;
  return -1;
}

/* ================== Rendu général ================== */
function renderChrome() {
  const L = t();
  document.documentElement.lang = state.ui;
  document.documentElement.dir = (langOf(state.ui) || {}).rtl ? "rtl" : "ltr";
  $("protoTag").textContent = L.proto;
  // Pendant le chargement d'un pays, seules ses langues sont proposées. Une langue indisponible reste focalisable
  // (aria-disabled, pas disabled) : on entend et on voit pourquoi (infobulle), au lieu d'un bouton muet.
  const loadCat = (state.view === "loading" || state.view === "loaderror") && CATALOG[state.loadCc];
  const list = state.country && DATA[state.country] ? ed().langs : LANGS.map(l => ({ code: l.code, label: l.code.toUpperCase(), name: l.name, ready: !loadCat || loadCat.langs.includes(l.code) }));
  $("langs").innerHTML = list.map(l => `<button type="button" data-lang="${l.code}" aria-pressed="${state.ui === l.code}" ${l.ready ? "" : 'aria-disabled="true" aria-describedby="langTip"'} title="${l.name}${l.ready ? "" : " · " + L.langWhy}" lang="${l.code}">${l.label}</button>`).join("");
  $("langs").setAttribute("aria-label", L.langLabel);
  $("langTip").textContent = L.langWhy;
  // Le slogan de prudence sur les positions codées n'a de sens que là où des positions de partis sont affichées
  const pos = ["start", "question", "checkpoint", "results"].includes(state.view);
  $("footer").innerHTML = `${pos ? `<span>${L.footer1}</span>` : ""}<span>${METER_ENDPOINT ? L.footerMeter : L.footer2}</span>`;
  // Lien d'évitement : seulement sur la carte (premier élément focalisable de la page)
  const sk = $("skip");
  sk.textContent = L.skipList;
  sk.hidden = state.view !== "map";
  const inQ = state.view === "question" || state.view === "valq";
  document.body.classList.toggle("qv", inQ);
  // Écran de question : seulement le drapeau (24 × 18), le nom du pays reste lisible pour les lecteurs d'écran
  const tf = $("topFlag"), qc = inQ ? curCc() : null;
  tf.hidden = !qc;
  tf.innerHTML = qc ? `${flagImg(qc === "fr" ? "fr" : qc, 24, 18, "cb-flag-xs", true)}<span class="sr">${esc(qc === "fr" ? catName("fr") : cname(A2ID[qc]))}</span>` : "";
}
/* Infobulle d'une langue indisponible : au survol, au focus ou au toucher ; placée sous le bouton, sans déborder de l'écran. */
let langTipTimer = null;
function langTip(btn) {
  const tip = $("langTip");
  clearTimeout(langTipTimer);
  if (!btn) { tip.hidden = true; return; }
  tip.hidden = false;
  const r = btn.getBoundingClientRect(), w = tip.offsetWidth;
  tip.style.top = Math.round(r.bottom + 6) + "px";
  tip.style.left = Math.round(Math.max(8, Math.min(r.left + r.width / 2 - w / 2, document.documentElement.clientWidth - w - 8))) + "px";
}
function renderSteps(active) {
  const el = $("steps");
  if (active == null) { el.hidden = true; return; }
  el.hidden = false;
  el.innerHTML = t().steps.map((s, k) => `<li class="${k < active ? "done" : k === active ? "on" : ""}"${k === active ? ' aria-current="step"' : ""}><span class="n">${k < active ? "✓" : k + 1}</span>${s}</li>`).join("");
}
/* Annonces pour les lecteurs d'écran : une seule région aria-live, hors de #app, jamais recréée. */
let liveTimer = null;
function announce(msg) {
  const el = $("live");
  if (!el) return;
  el.textContent = "";
  clearTimeout(liveTimer);
  liveTimer = setTimeout(() => { el.textContent = msg; }, 60);
}
function titleOf(h) {
  let s = h.textContent.replace(/[\u2066-\u2069]/g, "").replace(/\s+/g, " ").trim().replace(/[.:]$/, "");
  if (s.length > 70) s = s.slice(0, 68).trim() + "…";
  return s ? `${s} · ${BRAND}` : BRAND;
}
/* Après un changement d'écran : le focus va au titre de l'écran (h1, tabindex -1), qui est rendu visible ; sur une
   question, la page défile jusqu'à la question (et non en haut) quand les réponses ne tiennent pas dans l'écran. */
let booted = false;
function land(h) {
  let y = 0;
  if (state.view === "question") {   // la carte de la question (et non le haut de la fenêtre) reste en vue, si les réponses ne tiennent pas dans l'écran
    const meta = $("app").querySelector(".q-top"), ans = $("app").querySelectorAll(".ans");
    const last = ans[ans.length - 1];
    if (meta && last && last.getBoundingClientRect().bottom + window.scrollY > window.innerHeight) y = Math.max(0, meta.getBoundingClientRect().top + window.scrollY - 8);
  }
  window.scrollTo({ top: y });
  if (h && booted) { try { h.focus({ preventScroll: true }); } catch (e) { h.focus(); } }
}
let lastView = null;
function show(html, step, cls, keep) {
  // Réaffichage de la même page (changement de langue, sujet coché) : les sections ouvertes (<details>) le restent
  const open = keep ? [].map.call($("app").querySelectorAll("details"), d => d.open) : [];
  // Fondu d'entrée seulement quand l'écran change vraiment (pas d'une question à la suivante, ni au réaffichage)
  const enter = !keep && state.view !== lastView;
  lastView = state.view;
  $("app").innerHTML = `<section class="${cls || "screen"}${enter ? " enter" : ""}">${html}</section>`;
  if (open.length) [].forEach.call($("app").querySelectorAll("details"), (d, i) => { if (open[i]) d.open = true; });
  renderChrome();
  renderSteps(step);
  syncUrl();
  save();
  const h = $("app").querySelector("h1");
  if (h) h.setAttribute("tabindex", "-1");
  document.title = h ? titleOf(h) : BRAND;
  if (!keep) land(h);
  booted = true;
  meterHook();
}
function rerender() {
  const y = window.scrollY;
  const v = state.view;
  navMode = "replace";
  if (v === "map") viewMap(true);
  else if (v === "info") viewInfo(state.place, true);
  else if (v === "loading") viewLoading(true);
  else if (v === "loaderror") viewLoadError(true);
  else if (v === "edinfo") viewEdInfo(true);
  else if (v === "start") viewStart(true);
  else if (v === "question") viewQuestion(true);
  else if (v === "checkpoint") viewCheckpoint(true);
  else if (v === "results") viewResults(true);
  else if (v === "valintro") viewValuesIntro(true);
  else if (v === "valq") viewValuesQ(true);
  else if (v === "valres") viewValuesDone(true);
  window.scrollTo({ top: y });
}

/* ================== Carte ==================
   Chaque pays qui a un questionnaire ou une fiche, et chaque île, a un marqueur : une zone tactile invisible d'au moins
   12 px de rayon à l'écran (quelle que soit la largeur de la carte), avec son repère (✓ ou ⓘ) par-dessus. Les marqueurs
   qui se chevauchent (Gambie et Guinée-Bissau, Cap-Vert…) sont écartés les uns des autres, un trait les relie à leur vrai
   emplacement : toucher un marqueur ouvre toujours son propre pays. Au clavier, seuls les pays avec une élection ou un
   contenu sont dans l'ordre de tabulation (par nom), les autres restent accessibles par la liste. */
const INFO_MARK = (x, y, r) => `<circle class="ring" cx="${x}" cy="${y}" r="${r}"></circle><path class="stem" d="M${x} ${y - r * .1}v${r * .55}"></path><circle class="dot" cx="${x}" cy="${y - r * .5}" r="${r * .17}"></circle>`;
const CHECK_MARK = (x, y) => `<circle class="pin" cx="${x}" cy="${y}" r="11"></circle><path class="pin-check" d="M${x - 5} ${y}l3.5 3.5L${x + 6} ${y - 5}"></path>`;
const MK_R = 18;   // rayon de la zone tactile, en unités locales du marqueur (anneau : 11)
function markerIds() {
  const ids = Object.values(CATALOG).filter(c => c.a3 && AFRICA[c.a3] && (MAP.isl[c.a3] || MAP.cent[c.a3])).map(c => c.a3);
  Object.keys(MAP.isl).forEach(id => { if (ids.indexOf(id) < 0) ids.push(id); });
  return ids.sort();
}
function mapSVG() {
  const L = t();
  const aria = id => {
    const k = kindLine(catFor(id), L);
    return esc(`${cname(id)} · ${statusLine(id)}${k ? " · " + k.slice(2) : ""}`);
  };
  const foc = id => isUp(id) || !!catFor(id);
  // Une île a sa forme (minuscule) et son point : seul le point est dans l'ordre de tabulation
  const shape = id => {
    const tab = foc(id) ? 0 : -1;
    let h = MAP.c[id] ? `<path class="ctry ${isUp(id) ? "up" : "none"}" data-place="${id}" d="${MAP.c[id]}" tabindex="${MAP.isl[id] ? -1 : tab}" role="button" aria-label="${aria(id)}"${MAP.isl[id] ? ' aria-hidden="true"' : ""}></path>` : "";
    if (MAP.isl[id]) h += `<circle class="isl ${isUp(id) ? "up" : "none"}" data-place="${id}" cx="${MAP.isl[id][0]}" cy="${MAP.isl[id][1]}" r="9" tabindex="${tab}" role="button" aria-label="${aria(id)}"></circle>`;
    return h;
  };
  const all = Object.keys(MAP.c).filter(id => id !== "732").concat(Object.keys(MAP.isl).filter(id => !MAP.c[id]));
  const sorted = all.filter(foc).sort((a, b) => cname(a).localeCompare(cname(b), locale()));
  const shapes = (MAP.c["732"] ? `<path class="disp" d="${MAP.c["732"]}"><title>${esc(cname("732"))} · ${esc(L.legDisputed)}</title></path>` : "")
    + all.filter(id => !foc(id)).map(shape).join("") + sorted.map(shape).join("");
  const marks = markerIds().map(id => {
    const [x, y] = MAP.isl[id] || MAP.cent[id];
    const cat = catFor(id);
    const sym = !cat ? "" : cat.kind === "info" ? `<g class="pin-info">${INFO_MARK(0, 0, 9)}</g>` : CHECK_MARK(0, 0);
    return `<g class="mk" data-place="${id}" data-x="${x}" data-y="${y}" transform="translate(${x} ${y})" aria-hidden="true"><circle class="mk-halo" r="16"></circle><circle class="mk-focus" r="16"></circle><circle class="mk-hit" r="${MK_R}"></circle>${sym}</g>`;
  }).join("");
  return `<svg viewBox="${MAP.vb.join(" ")}" role="group" aria-label="${esc(L.mapAria)}" dir="ltr">
    <defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="var(--none)"></rect><rect width="1.8" height="5" fill="var(--none-hatch)"></rect></pattern></defs>
    <path class="nb" d="${MAP.nb}"></path>${shapes}<g class="leads"></g><g class="marks">${marks}</g><g class="fring"></g>
  </svg><div class="tip" id="tip" hidden></div>`;
}
/* Place les marqueurs : taille d'écran constante (zone tactile ≥ 12 px de rayon), écartés quand ils se touchent. */
function layoutMarkers() {
  const wrap = $("mapWrap"), svg = wrap && wrap.querySelector("svg");
  if (!svg) return;
  const w = svg.getBoundingClientRect().width;
  if (!w) return;
  const k = w / MAP.vb[2];                       // pixels d'écran par unité de la carte
  const S = Math.max(1, 12 / (MK_R * k));         // échelle d'un marqueur
  const gap = 2 * MK_R * S;                       // distance minimale entre deux centres, en unités de la carte
  const m = [].map.call(svg.querySelectorAll(".mk"), el => ({ el: el, ax: +el.dataset.x, ay: +el.dataset.y, x: +el.dataset.x, y: +el.dataset.y }));
  const x0 = MAP.vb[0] + gap / 2, x1 = MAP.vb[0] + MAP.vb[2] - gap / 2, y0 = MAP.vb[1] + gap / 2, y1 = MAP.vb[1] + MAP.vb[3] - gap / 2;
  for (let it = 0; it < 120; it++) {
    let moved = false;
    for (let i = 0; i < m.length; i++) for (let j = i + 1; j < m.length; j++) {
      let dx = m[j].x - m[i].x, dy = m[j].y - m[i].y, d = Math.sqrt(dx * dx + dy * dy);
      if (d >= gap) continue;
      if (d < 0.01) { dx = Math.cos(i * 2.4 + j); dy = Math.sin(i * 2.4 + j); d = 1; }
      const push = (gap - d) / 2 + 0.05, ux = dx / d, uy = dy / d;
      m[i].x -= ux * push; m[i].y -= uy * push; m[j].x += ux * push; m[j].y += uy * push;
      moved = true;
    }
    for (let i = 0; i < m.length; i++) {
      if (it < 90) { m[i].x += (m[i].ax - m[i].x) * 0.03; m[i].y += (m[i].ay - m[i].y) * 0.03; }   // rappel léger vers l'emplacement réel
      m[i].x = Math.max(x0, Math.min(x1, m[i].x)); m[i].y = Math.max(y0, Math.min(y1, m[i].y));
    }
    if (!moved && it >= 90) break;
  }
  let leads = "";
  m.forEach(o => {
    o.el.setAttribute("transform", `translate(${o.x.toFixed(1)} ${o.y.toFixed(1)}) scale(${S.toFixed(3)})`);
    const far = Math.sqrt(Math.pow(o.x - o.ax, 2) + Math.pow(o.y - o.ay, 2));
    if (far > 11 * S * 0.9) leads += `<line class="lead" x1="${o.ax}" y1="${o.ay}" x2="${o.x.toFixed(1)}" y2="${o.y.toFixed(1)}"></line><circle class="lead-dot" cx="${o.ax}" cy="${o.ay}" r="${(2.6 / k).toFixed(1)}"></circle>`;
  });
  svg.querySelector(".leads").innerHTML = leads;
}
/* Recherche d'un pays : sans accents ni majuscules, tous les mots doivent se retrouver ; noms dans les 5 langues de l'interface
   et appellations courantes (anglais, français, portugais) qui ne sont pas le nom officiel. */
const fold = x => String(x == null ? "" : x).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[\u2019'`\u00b4.\-_,]/g, " ").replace(/\s+/g, " ").trim();
const ALIASES = {
  "384": "ivory coast cote d ivoire costa do marfim civ", "132": "cape verde cabo verde cap vert", "748": "swaziland eswatini",
  "178": "congo brazzaville republic of the congo republique du congo congo brazza", "180": "congo kinshasa democratic republic of the congo drc dr congo rdc rd congo zaire republique democratique du congo",
  "624": "guinea bissau guine bissau guinee bissau", "226": "equatorial guinea guinee equatoriale guine equatorial", "140": "central african republic car rca centrafrique republica centro africana",
  "854": "burkina faso upper volta", "204": "benin dahomey", "678": "sao tome and principe sao tome et principe", "710": "south africa afrique du sud africa do sul rsa",
  "728": "south sudan soudan du sud sudao do sul", "729": "sudan soudan sudao", "834": "tanzania tanzanie tanzania", "800": "uganda ouganda", "818": "egypt egypte egito",
  "504": "morocco maroc marrocos", "12": "algeria algerie argelia", "788": "tunisia tunisie tunisia", "434": "libya libye libia", "270": "gambia the gambia gambie",
  "480": "mauritius maurice ile maurice", "690": "seychelles", "174": "comoros comores", "450": "madagascar", "148": "chad tchad", "466": "mali"
};
let searchIdx = null;
function searchIndex() {
  if (searchIdx) return searchIdx;
  searchIdx = {};
  Object.keys(AFRICA).forEach(id => {
    const names = LANGS.map(l => cname(id, l.code)).concat([AFRICA[id].fr, AFRICA[id].en, AFRICA[id].a2, ALIASES[id] || ALIASES[String(+id)] || ""]);
    const f = fold(names.join(" "));
    searchIdx[id] = f + " " + f.replace(/ /g, "");   // aussi sans espaces : « cote divoire », « guineebissau »
  });
  return searchIdx;
}
function countryList(filter) {
  const L = t();
  const words = fold(filter).split(" ").filter(Boolean);
  const idx = words.length ? searchIndex() : null;
  const ids = Object.keys(AFRICA).filter(id => !idx || words.every(w => idx[id].indexOf(w) >= 0));
  const sort = arr => arr.sort((a, b) => cname(a).localeCompare(cname(b), locale()));
  const up = sort(ids.filter(isUp)), no = sort(ids.filter(id => !isUp(id)));
  const mark = id => {
    const cat = catFor(id);
    if (!cat) return "";
    return cat.kind === "ed" ? ` <span aria-hidden="true">✓</span><span class="sr">${esc(L.legReady)}</span>` : ` <span aria-hidden="true">ⓘ</span><span class="sr">${esc(L.legInfo)}</span>`;
  };
  const item = id => `<li><button type="button" class="cbtn" data-place="${id}"><span class="dot ${isUp(id) ? "up" : "none"}" aria-hidden="true"></span><span><span class="cn2">${esc(cname(id))}${mark(id)}</span><span class="cs2">${esc(isUp(id) || catFor(id) ? statusLine(id) : L.legNone)}</span></span></button></li>`;
  if (!ids.length) return `<p class="muted" role="status">${esc(L.noCountry)}</p>`;
  return `${up.length ? `<div class="clist-group"><h2>${L.legUp} · ${L.nCountries(up.length)}</h2><ul class="clist2">${up.map(item).join("")}</ul></div>` : ""}
    ${no.length ? `<div class="clist-group"><h2>${L.legNone} · ${L.nCountries(no.length)}</h2><ul class="clist2">${no.map(item).join("")}</ul></div>` : ""}`;
}
function viewMap(keep) {
  state.view = "map"; state.country = null; state.place = null;
  const L = t();
  const nUp = Object.keys(AFRICA).filter(isUp).length, nNo = Object.keys(AFRICA).length - nUp;
  const inAfrica = Object.values(CATALOG).filter(c => c.a3 && AFRICA[c.a3]);
  const nReady = inAfrica.filter(c => c.kind === "ed").length, nInfo = inAfrica.filter(c => c.kind === "info").length;
  show(`
    <div class="map-intro">
      <p class="kicker">${L.heroKicker(inAfrica.length)}</p>
      <h1 class="map-title">${L.mapTitle}</h1>
      <p class="lead">${L.mapLead}</p>
      ${meterSlot("africa", null, 2)}
    </div>
    <div class="map-card">
      <div class="map-wrap" id="mapWrap">${mapSVG()}</div>
      <p class="map-hint">${L.mapHint}</p>
    </div>
    <div class="map-side">
      <ul class="legend">
        <li><span class="sw up" aria-hidden="true"></span><span>${L.legUp}</span><span class="cnt">${nUp}</span></li>
        <li><span class="sw none" aria-hidden="true"></span><span>${L.legNone}</span><span class="cnt">${nNo}</span></li>
        <li><span class="sw ready" aria-hidden="true"><svg class="pin-key" viewBox="-13 -13 26 26">${CHECK_MARK(0, 0)}</svg></span><span>${L.legReady}</span><span class="cnt">${nReady}</span></li>
        <li class="leg-info"><span class="sw info" aria-hidden="true"><svg class="pin-info" viewBox="0 0 18 18">${INFO_MARK(9, 9, 7.6)}</svg></span><span>${L.legInfo}</span><span class="cnt">${nInfo}</span></li>
        <li><span class="sw disp" aria-hidden="true"></span><span>${L.legDisputed}</span><span class="cnt">1</span></li>
      </ul>
      <details class="clist-wrap" id="listBox">
        <summary>${L.listToggle}</summary>
        <label class="sr" for="csearch">${L.searchLabel}</label>
        <input id="csearch" type="search" placeholder="${esc(L.searchLabel)}" autocomplete="off">
        <div id="clist">${countryList("")}</div>
      </details>
      ${CATALOG.fr ? `<div class="outside"><p class="eyebrow">${L.outsideAfrica}</p><button class="link" type="button" data-go="france">${L.protoFrance}</button></div>` : ""}
      <p class="tagline">${L.tagline}</p>
    </div>
  `, null, "screen map-screen", keep);
  bindMap();
}
let mapRO = null;
function bindMap() {
  const wrap = $("mapWrap"), tip = $("tip");
  if (!wrap) return;
  layoutMarkers();
  if (mapRO) { mapRO.disconnect(); mapRO = null; }
  if (window.ResizeObserver) { mapRO = new ResizeObserver(layoutMarkers); mapRO.observe(wrap); }
  const showTip = (el, x, y) => {
    const id = el.dataset.place;
    const k = kindLine(catFor(id), t());
    tip.innerHTML = `<b>${esc(cname(id))}</b>${esc(statusLine(id))}${k ? `<span class="tx">${esc(k)}</span>` : ""}`;
    tip.hidden = false;
    const r = wrap.getBoundingClientRect();
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    let left = x - r.left + 14, top = y - r.top - th - 10;
    if (left + tw > r.width) left = Math.max(0, x - r.left - tw - 14);
    if (top < 0) top = y - r.top + 18;
    tip.style.left = left + "px"; tip.style.top = top + "px";
  };
  // Le repère du pays dont la forme a le focus au clavier : la forme d'un petit pays (Gambie) est trop fine pour porter un cadre
  const markFocus = (id, on) => { const g = wrap.querySelector(`.mk[data-place="${id}"]`); if (g) g.classList.toggle("kf", on); };
  // Cadre de focus à deux tons autour de la forme du pays (ou du point d'une île), au clavier seulement
  const ring = el => {
    const g = wrap.querySelector(".fring");
    if (!g) return;
    let vis = !!el;
    try { vis = !!el && el.matches(":focus-visible"); } catch (e) { /* ancien navigateur : toujours montré */ }
    const one = c => el.tagName.toLowerCase() === "path" ? `<path class="${c}" d="${el.getAttribute("d")}"></path>` : `<circle class="${c}" cx="${el.getAttribute("cx")}" cy="${el.getAttribute("cy")}" r="${+el.getAttribute("r") + 1}"></circle>`;
    g.innerHTML = vis ? one("fr-halo") + one("fr-ink") : "";
  };
  wrap.addEventListener("pointermove", e => {
    const el = e.target.closest("[data-place]");
    if (!el || e.pointerType === "touch") { tip.hidden = true; return; }
    showTip(el, e.clientX, e.clientY);
  });
  wrap.addEventListener("pointerleave", () => { tip.hidden = true; });
  wrap.addEventListener("focusin", e => {
    const el = e.target.closest("[data-place]");
    if (!el) return;
    markFocus(el.dataset.place, true);
    ring(el);
    const b = el.getBoundingClientRect();
    showTip(el, b.left + b.width / 2, b.top + b.height / 2);
  });
  wrap.addEventListener("focusout", e => {
    const el = e.target.closest && e.target.closest("[data-place]");
    if (el) markFocus(el.dataset.place, false);
    ring(null);
    tip.hidden = true;
  });
  wrap.addEventListener("keydown", e => {
    const el = e.target.closest("[data-place]");
    if (el && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); chooseCountry(el.dataset.place); }
  });
  const s = $("csearch");
  if (s) s.addEventListener("input", () => { $("clist").innerHTML = countryList(s.value); });
}
/* Lien d'évitement « Aller à la liste des pays » : ouvre la liste et place le focus sur sa recherche. */
function skipToList() {
  const box = $("listBox");
  if (!box) return;
  box.open = true;
  const f = $("csearch");
  if (f) f.focus();
  box.scrollIntoView({ block: "start" });
}
/* Un pays touché sur la carte ou dans la liste : nouvelle entrée d'historique #/<cc> (Retour referme le choix de langue). */
function chooseCountry(id) {
  const cc = ccOf(id);
  if (!cc) return;
  setHash(`#/${cc}`, true, { dlg: 1 });
  route(location.hash);
}

/* ================== Choix de la langue ================== */
function openLang(id) {
  state.pending = id;
  $("tip") && ($("tip").hidden = true);
  const L = t();
  const c = AFRICA[id];
  const cat = catFor(id);
  const avail = cat ? cat.langs : null;
  const note = cat ? (cat.kind === "info" ? L.langNoInfo : L.langNoQ) : "";
  const uiDir = (langOf(state.ui) || {}).rtl ? "rtl" : "ltr";
  const mine = LANGS.filter(l => c.langs.includes(l.code)).sort((a, b) => c.langs.indexOf(a.code) - c.langs.indexOf(b.code));
  const other = LANGS.filter(l => !c.langs.includes(l.code));
  const btn = l => {
    const off = !!avail && !avail.includes(l.code);
    // Langue indisponible : reste focalisable (aria-disabled) et dit pourquoi (la note visible sert de description)
    return `<button type="button" class="lang-btn${l.code === state.ui && !off ? " cur" : ""}" data-pick="${l.code}" lang="${l.code}" dir="${l.rtl ? "rtl" : "ltr"}"${off ? ` aria-disabled="true" aria-describedby="ln-${l.code}"` : ""}><span><span>${l.name}</span>${off ? `<span class="lnote" id="ln-${l.code}" lang="${state.ui}" dir="${uiDir}">${esc(note)}</span>` : ""}</span><span class="lc">${l.code.toUpperCase()}</span></button>`;
  };
  $("langBody").innerHTML = `
    ${bannerHTML(id)}
    <div><h2 id="langTitle">${L.chooseLang}</h2>${cat ? `<p class="st">${esc(kindLine(cat, L))}</p>` : ""}</div>
    <div class="lang-grid"><h3>${L.langCountry}</h3>${mine.map(btn).join("")}</div>
    <div class="lang-grid"><h3>${L.langOther}</h3>${other.map(btn).join("")}</div>
    <div><button class="btn btn-ghost" type="button" id="langCancel">${L.cancel}</button></div>`;
  const dlg = $("langDlg");
  if (typeof dlg.showModal === "function") { if (!dlg.open) dlg.showModal(); } else dlg.setAttribute("open", "");
  const first = $("langBody").querySelector(".lang-btn.cur") || $("langBody").querySelector('.lang-btn:not([aria-disabled="true"])');
  if (first) first.focus();
}
function closeLang() { const d = $("langDlg"); if (d.open) { if (typeof d.close === "function") d.close(); else d.removeAttribute("open"); } }
function pickLang(code) {
  const id = state.pending;
  const cc = ccOf(id);
  if (!cc) return closeLang();
  setUi(code, true);
  // L'entrée #/<cc> du choix de langue est remplacée : Retour depuis le pays ramène à la carte, pas au choix de langue.
  setHash(`#/${cc}/${code}`, false, {});
  closeLang();
  route(location.hash);
}
/* Fermeture du choix de langue sans choisir (Annuler, Échap, fond, Retour d'Android) : on revient à #/. */
$("langDlg").addEventListener("close", () => {
  const r = parseHash(location.hash);
  if (!r.cc || r.lang) return;
  if (history.state && history.state.dlg) { try { history.back(); return; } catch (e) { } }
  setHash("#/", false, {});
});

/* ================== Chargement d'une édition ================== */
let loadSeq = 0;
function openEdition(cc, after) {
  if (!CATALOG[cc]) return viewMap();
  closeFiche();
  const seq = ++loadSeq;
  state.loadCc = cc;
  if (!CATALOG[cc].langs.includes(state.ui)) state.ui = CATALOG[cc].langs[0];
  const ready = () => {
    if (seq !== loadSeq) return;
    const D = DATA[cc];
    state.country = cc; state.place = null;
    if (!D.langs.includes(state.ui)) state.ui = D.lang;
    if (D.kind === "ed") {
      if (state.ac !== cc) { resetAnswers(); state.priorities = []; state.ac = cc; }
      checkSession(D.ed);
    }
    if (after) after();
    else if (D.kind === "info") viewEdInfo(); else viewStart();
  };
  if (DATA[cc]) { ready(); return; }
  const timer = setTimeout(() => { if (seq === loadSeq) viewLoading(); }, 120);
  loadEdition(cc).then(() => { clearTimeout(timer); ready(); }, () => {
    clearTimeout(timer);
    if (seq !== loadSeq) return;
    viewLoadError();
    const b = document.querySelector('[data-go="retry"]'); if (b) b.focus();
  });
}
function viewLoading(keep) {
  state.view = "loading"; state.country = null;
  const L = t();
  show(`
    <div class="load-box" role="status" aria-live="polite"><span class="spinner" aria-hidden="true"></span><p class="lead">${esc(L.loading(catName(state.loadCc)))}</p></div>
    <div class="actions"><button class="btn btn-ghost" type="button" data-go="home">${L.backMap}</button></div>
  `, null, "screen", keep);
}
function viewLoadError(keep) {
  state.view = "loaderror"; state.country = null;
  const L = t(), name = catName(state.loadCc);
  show(`
    <div class="block" role="alert">
      <p class="eyebrow">${esc(name)}</p>
      <h1 class="big-title">${esc(L.loadErrTitle(name))}</h1>
      <p class="lead">${L.loadErrText}</p>
    </div>
    <div class="actions">
      <button class="btn btn-primary" type="button" data-go="retry">${L.retry}</button>
      <button class="btn btn-ghost" type="button" data-go="home">${L.backMap}</button>
    </div>
  `, null, "screen", keep);
}

/* ================== Pays sans édition ================== */
function viewInfo(id, keep) {
  state.view = "info"; state.place = id; state.country = null;
  const L = t(), c = AFRICA[id];
  const name = cname(id);
  const up = isUp(id);
  // Une seule phrase d'état (le titre) ; dessous, seulement ce qui s'y ajoute : dates, précisions, dernier et prochain scrutin
  const lines = [];
  if (up) evsFor(id).forEach(ev => lines.push(`<li><span class="dot up" aria-hidden="true"></span><span>${esc(evText(ev))}</span></li>`));
  else {
    if (c.note) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.notes[c.note])}</span></li>`);
    if (c.recent) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.recent(fmtDate(c.recent)))}</span></li>`);
    if (c.next) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.nextKnown)}${C()} ${esc(evText(c.next))}</span></li>`);
  }
  const cat = catFor(id);
  const s = (cat && cat.evSrc) || SRC_AF[c.src];
  show(`
    <div class="strip">
      <span class="cband">${flagImg(flagCc(id), 32, 24, "cb-flag-sm")}<span><b>${esc(name)}</b>${up ? `<br><span class="sd">${esc(L.upcoming)}</span>` : ""}</span></span>
      <button class="link" type="button" data-go="home">${L.changeCountry}</button>
    </div>
    <div class="block">
      <h1 class="big-title">${esc(up ? L.prepTitle(name) : L.noneTitle(name))}</h1>
    </div>
    ${lines.length ? `<ul class="ev-list">${lines.join("")}</ul>` : ""}
    ${s ? `<p class="src muted">${L.source}${C()} ${srcA(s)}</p>` : ""}
    ${up ? `<p class="lead">${L.prepText}</p>` : ""}
    ${valuesCardHTML(true)}
    <div class="actions">
      <button class="btn btn-primary" type="button" data-go="home">${L.backMap}</button>
      ${CATALOG.ng ? `<button class="link" type="button" data-go="nigeria">${L.tryNigeria}</button>` : ""}
    </div>
  `, null, "screen", keep);
}

/* ================== Page d'information (pas de comparaison possible) ================== */
function viewEdInfo(keep) {
  state.view = "edinfo";
  const E = ed(), L = t(), name = edName(E);
  const used = uniq([E.meta.src, ...(E.factsSrc || []), ...(E.systemSrc || []), ...(E.actors || []).map(a => a[2])]).filter(id => E.src[id]);
  const all = [...used, ...Object.keys(E.src).filter(id => !used.includes(id))];
  show(`
    <div class="strip">
      <span class="cband">${flagImg(edCc(E), 32, 24, "cb-flag-sm")}<span><b>${esc(name)} · ${esc(E.strip)}</b><br><span class="sd">${esc(E.stripDate)}</span></span></span>
      <button class="link" type="button" data-go="home">${L.changeCountry}</button>
    </div>
    <div class="block">
      <p class="eyebrow">${L.infoEyebrow}</p>
      <h1 class="big-title">${esc(L.infoTitle(name))}</h1>
      <p class="lead">${L.infoLead}</p>
    </div>
    ${noteHTML(E, L)}
    <section class="info-card" aria-labelledby="hFacts">
      <h2 id="hFacts">${L.infoFacts}</h2>
      <dl class="facts">${(E.facts || []).map(([a, b]) => `<div><dt>${esc(a)}</dt><dd>${esc(b)}</dd></div>`).join("")}</dl>
      ${srcLine(E.factsSrc, L)}
    </section>
    <section class="info-card" aria-labelledby="hSys">
      <h2 id="hSys">${L.aboutElection}</h2>
      <ul class="sys">${(E.system || []).map(([a, b]) => `<li><b>${esc(a)}</b><span>${esc(b)}</span></li>`).join("")}</ul>
      ${srcLine(E.systemSrc, L)}
    </section>
    <section class="info-card" aria-labelledby="hActors">
      <h2 id="hActors">${L.infoActors}</h2>
      <ul class="sys actors">${(E.actors || []).map(([a, b, s]) => `<li><b>${esc(a)}</b><span>${esc(b)}${srcLink(s) ? `<span class="src">${L.source}${C()} ${srcLink(s)}</span>` : ""}</span></li>`).join("")}</ul>
    </section>
    <section class="why-box" aria-labelledby="hWhy">
      <h2 id="hWhy">${L.infoWhy}</h2>
      <p>${esc(E.why)}</p>
    </section>
    <section class="info-src" aria-labelledby="hSrc">
      <h2 id="hSrc">${L.mSrcTitle}</h2>
      <ol class="src-list">${all.map(id => { const s = E.src[id]; return `<li><a href="${esc(s.u)}" target="_blank" rel="noopener">${esc(s.t)}</a> · ${esc(s.o)}, ${esc(srcDate(s.d))}</li>`; }).join("")}</ol>
      ${E.lang !== E.baseLang ? `<p class="caveat">${L.mTransl}</p>` : ""}
    </section>
    ${valuesCardHTML(true)}
    <div class="actions">
      <button class="btn btn-primary" type="button" data-go="home">${L.backMap}</button>
      ${CATALOG.ng && E.cc !== "ng" ? `<button class="link" type="button" data-go="nigeria">${L.tryNigeria}</button>` : ""}
    </div>
  `, null, "screen", keep);
}

/* ================== Départ : élection + priorités ================== */
function viewStart(keep) {
  state.view = "start";
  const E = ed(), L = t();
  const full = state.priorities.length >= 3;
  const n = state.priorities.length;
  const done = answeredCount();
  show(`
    <div class="strip">
      <span class="cband">${flagImg(edCc(E), 32, 24, "cb-flag-sm")}<span><b>${esc(edName(E))} · ${esc(E.strip)}</b><br><span class="sd">${esc(E.stripDate)}</span></span></span>
      <button class="link" type="button" data-go="home">${L.changeCountry}</button>
    </div>
    ${noteHTML(E, L)}
    <div class="about">
      <details>
        <summary>${L.aboutElection}</summary>
        <dl class="facts">${E.facts.map(([a, b]) => `<div><dt>${esc(a)}</dt><dd>${esc(b)}</dd></div>`).join("")}</dl>
        <ul class="sys">${E.system.map(([a, b]) => `<li><b>${esc(a)}</b><span>${esc(b)}</span></li>`).join("")}</ul>
        ${srcLine([...(E.factsSrc || []), ...(E.systemSrc || [])], L, "margin-top:8px")}
      </details>
      <details>
        <summary>${L.whoCompared(E.parties.length)}</summary>
        <p class="basis">${E.role === "leader" ? L.partyBasisLeader : L.partyBasis}</p>
        <ul class="party-list">${E.parties.map(p => `
          <li><button class="party-btn" type="button" data-fiche="${esc(p.id)}">
            ${badge(p)}
            <span class="pb-text"><span class="pb-name">${hname(p)} ${p.chip ? `<span class="chip warn">${esc(p.chip)}</span>` : ""}</span><span class="pb-sub">${candLine(p, E, L)}</span></span>
          </button></li>`).join("")}
        </ul>
        <p class="caveat" style="margin-top:10px">${esc(E.status)}</p>
        ${(E.others || []).length ? `<details style="margin-top:10px"><summary>${L.alsoRunning}</summary><ul class="others">${E.others.map(o => `<li>${esc(o)}</li>`).join("")}</ul>${srcLine([E.othersSrc], L, "margin-top:6px")}</details>` : ""}
      </details>
    </div>
    <div class="block">
      <h1 class="big-title">${L.themesTitle}</h1>
      <p class="lead">${L.themesLead}</p>
    </div>
    ${meterSlot("country", edCc(E), 2)}
    ${done && state.order.length ? `<div class="resume"><p>${esc(L.resumeText(done))}</p><button class="btn btn-primary" type="button" data-go="resume">${L.resumeBtn}</button></div>` : ""}
    <div class="theme-grid">${E.themes.map(th => {
      const on = state.priorities.includes(th.id);
      const rank = state.priorities.indexOf(th.id) + 1;
      const nq = E.questions.filter(q => q.theme === th.id).length;
      return `<button type="button" class="theme-opt" data-prio="${esc(th.id)}" aria-pressed="${on}" ${!on && full ? "disabled" : ""}>
        <span class="box" aria-hidden="true">${CHECK}</span>
        <span class="tn">${esc(th.name)} ${on ? `<span class="rank-badge">· ${L.prioN(rank)}</span>` : ""}</span>
        <span class="tm">${esc(th.min)}</span>
        <span class="tq">${L.nQ(nq)}</span>
      </button>`;
    }).join("")}</div>
    <div class="sticky-go">
      <button class="btn btn-${done && state.order.length ? "ghost" : "primary"}" type="button" data-go="startq" aria-describedby="goHint" ${n ? "" : "disabled"}>${L.startPrio}</button>
      <span class="mono muted" id="goHint" style="font-size:.85rem">${n ? L.chosen(n) : L.startHint}</span>
    </div>
  `, 0, "screen", keep);
}
function buildOrder() {
  const E = ed();
  const idx = th => E.questions.map((q, i) => q.theme === th ? i : -1).filter(i => i >= 0);
  const pr = state.priorities.flatMap(idx);
  const rest = E.themes.map(th => th.id).filter(id => !state.priorities.includes(id)).flatMap(idx);
  state.order = [...pr, ...rest];
  state.nPrio = pr.length;
}

/* ================== Questionnaire ================== */
let advanceTimer = null, backTimer = null, qShownAt = 0;
function viewQuestion(keep) {
  state.view = "question";
  const E = ed(), L = t();
  const qi = state.order[state.i];
  const q = E.questions[qi];
  const th = E.themes.find(x => x.id === q.theme);
  const inPrio = state.i < state.nPrio;
  const v = state.answers[qi];
  const allPrioSeen = state.order.slice(0, state.nPrio).every(x => state.answers[x] !== undefined);
  const n = state.order.length, pos = state.i + 1;
  // Une seule ligne de progression : « 12 / 38 », une fine barre (repère à la fin des sujets prioritaires) et la liste des questions
  const tick = state.nPrio > 0 && state.nPrio < n ? `<i class="tick" style="inset-inline-start:${(state.nPrio / n * 100).toFixed(1)}%"></i>` : "";
  // « Compte double » : bouton à bascule à côté de l'énoncé, lié à CETTE question (data-dbl), jamais à state.i au moment du clic
  show(`
    <div class="q-top">
      <span class="q-count mono" dir="ltr">${pos} / ${n}</span>
      <div class="qbar" role="progressbar" aria-label="${esc(L.steps[1])}" aria-valuemin="1" aria-valuemax="${n}" aria-valuenow="${pos}" aria-valuetext="${esc(L.qOf(pos, n))}"><span style="width:${(pos / n * 100).toFixed(1)}%"></span>${tick}</div>
      <button type="button" class="qlist-btn" data-go="qlist" aria-haspopup="dialog">${L.qList}</button>
    </div>
    <div class="q-meta">
      <span class="q-theme">${esc(th.name)}</span> <span class="chip ${inPrio ? "" : "grey"}">${inPrio ? L.blockPrio : L.blockMore}</span>
    </div>
    <div class="slip">
      <h1>${esc(q.text)}</h1>
      <div class="slip-row">
        <button type="button" class="star" data-dbl="${qi}" aria-pressed="${!!state.double[qi]}"><span class="st" aria-hidden="true">★</span><span>${L.double}</span></button>
        <details><summary>${L.background}</summary><p class="q-min">${L.ministries}${C()} ${esc(th.min)}</p><p>${esc(q.ctx)}</p></details>
      </div>
    </div>
    <fieldset class="answers" data-q="${qi}"><legend class="sr">${L.yourAnswer}</legend>
      ${[2, 1, 0, -1, -2].map(val => `<button type="button" class="ans" data-val="${val}" aria-pressed="${v === val}"><span class="box" aria-hidden="true">${CHECK}</span><span>${L.ans[val]}</span></button>`).join("")}
    </fieldset>
    <div class="q-nav">
      <button class="btn btn-ghost" type="button" data-go="prev" ${state.i === 0 ? "disabled" : ""}>${L.prev}</button>
      <div class="actions">
        <button class="btn btn-ghost" type="button" data-val="skip" data-q="${qi}">${v === null ? L.skipped : L.skip}</button>
        ${allPrioSeen ? `<button class="btn btn-primary" type="button" data-go="results">${L.seeResults}</button>` : ""}
      </div>
    </div>
  `, null, "screen q-screen", keep);
  qShownAt = now();
  if (!keep) announce(L.qOf(state.i + 1, state.order.length));
}
/* Liste des questions : toutes, avec leur état (répondue, passée, pas encore) ; chaque ligne mesure au moins 44 px. */
function openQList() {
  const E = ed(), L = t();
  const row = k => {
    const qi = state.order[k], a = state.answers[qi], q = E.questions[qi];
    const st = typeof a === "number" ? "done" : a === null ? "skip" : "open";
    const label = st === "done" ? L.qStateDone : st === "skip" ? L.qStateSkip : L.qStateOpen;
    const cur = k === state.i;
    return `<li><button type="button" class="qrow ${st}${cur ? " cur" : ""}" data-qjump="${k}"${cur ? ' aria-current="step"' : ""}><span class="qn mono" dir="ltr">${k + 1}</span><span class="qt">${esc(q.short)}</span>${state.double[qi] ? `<span class="qd" title="${esc(L.double)}" aria-label="${esc(L.double)}">★</span>` : ""}<span class="qs">${st === "done" ? "✓ " : st === "skip" ? "↷ " : ""}${esc(label)}</span></button></li>`;
  };
  const ks = state.order.map((x, k) => k);
  const prio = ks.slice(0, state.nPrio), rest = ks.slice(state.nPrio);
  $("qBody").innerHTML = `
    <div class="qdlg-head"><h2 id="qDlgTitle">${L.qJumpTitle}</h2><button class="close" type="button" id="qClose" aria-label="${esc(L.ficheClose)}">×</button></div>
    ${prio.length ? `<h3 class="qgrp">${L.blockPrio}</h3><ul class="qlist">${prio.map(row).join("")}</ul>` : ""}
    ${rest.length ? `<h3 class="qgrp">${L.blockMore}</h3><ul class="qlist">${rest.map(row).join("")}</ul>` : ""}`;
  const dlg = $("qDlg");
  if (typeof dlg.showModal === "function") { if (!dlg.open) dlg.showModal(); } else dlg.setAttribute("open", "");
  const cur = dlg.querySelector(".qrow.cur");
  if (cur) { cur.focus({ preventScroll: true }); cur.scrollIntoView({ block: "center" }); }
}
function closeQList() { const d = $("qDlg"); if (d && d.open) { if (typeof d.close === "function") d.close(); else d.removeAttribute("open"); } }
function answer(val, qi) {
  if (state.view !== "question" || qi !== state.order[state.i]) return;
  state.answers[qi] = val;
  document.querySelectorAll(".ans").forEach(b => b.setAttribute("aria-pressed", String(+b.dataset.val === val)));
  save();
  clearTimeout(advanceTimer);
  advanceTimer = setTimeout(nextQ, 240);
}
function nextQ() {
  if (state.view !== "question") return;
  const last = state.order.length - 1;
  // Correction lancée depuis les résultats : retour aux résultats à la fin de la plage corrigée
  if (state.ret && state.i >= state.ret.until) return toResults();
  if (state.i === state.nPrio - 1 && state.nPrio < state.order.length && !state.order.slice(state.nPrio).some(x => state.answers[x] !== undefined)) {
    viewCheckpoint(); return;
  }
  if (state.i < last) { state.i++; viewQuestion(); }
  else finishParty();
}
/* Fin du questionnaire de partis : une fois par session, l'invitation (facultative) aux 10 questions sur les valeurs, puis les résultats */
function finishParty() {
  if (!state.vseen && !Object.keys(state.vals).length) { navMode = "push"; return viewValuesIntro(); }
  toResults();
}
/* Vers les résultats. Si la question affichée a été ouverte depuis les résultats (entrée d'historique marquée « ret »),
   on revient en arrière dans l'historique au lieu d'empiler un second écran de résultats. */
function toResults() {
  clearTimeout(advanceTimer);
  const back = !!(state.ret && history.state && history.state.ret);
  state.ret = null;
  if (back) {
    try { history.back(); } catch (e) { }
    // Repli si l'hébergeur bloque l'historique : afficher quand même les résultats. Annulé dès que Retour aboutit
    // (route) ou que l'utilisateur fait autre chose (go) : sinon il pourrait surgir sur un écran ouvert ensuite.
    clearTimeout(backTimer);
    backTimer = setTimeout(() => { if (state.view === "question") { navMode = "push"; viewResults(); } }, 500);
    return;
  }
  navMode = "push";
  viewResults();
}
function viewCheckpoint(keep) {
  state.view = "checkpoint";
  const L = t();
  const rest = state.order.length - state.nPrio;
  show(`
    <div class="block">
      <p class="eyebrow">${L.cpEyebrow}</p>
      <h1 class="big-title">${L.cpTitle}</h1>
      <p class="lead">${L.cpText(rest)}</p>
    </div>
    <div class="actions">
      <button class="btn btn-primary" type="button" data-go="results">${L.seeResults}</button>
      <button class="btn btn-ghost" type="button" data-go="more">${L.cpMore(rest)}</button>
    </div>
  `, 1, "screen", keep);
}

/* ================== Résultats ================== */
/* Le titre (souvent partagé en capture d'écran) reste court et ne dit jamais plus que ce que les données permettent. */
function headline(rank, a) {
  const E = ed(), L = t();
  const ranked = rank.filter(r => r.grp === "ok"), thin = rank.filter(r => r.grp === "thin");
  const pr = state.priorities.map(id => (E.themes.find(x => x.id === id) || {}).name).filter(Boolean).join(", ") || L.none;
  const nums = Object.values(state.answers).filter(v => typeof v === "number");
  const most = nums.length ? Math.max(...[-2, -1, 0, 1, 2].map(v => nums.filter(x => x === v).length)) : 0;
  const H = { summary: L.resSummary(a, E.questions.length, pr), early: a < EARLY, straight: a >= 6 && most / a >= STRAIGHT, more: firstOpen() >= 0 };
  if (!ranked.length) {
    H.title = thin.length ? L.resThin : L.resNone;
    H.summary = thin.length ? L.resThinText : L.resNoneText;
    return H;
  }
  const lead = topGroup(ranked);
  const who = lead.length > 1 ? listFmt(lead.map(r => psig(r.p))) : plabel(lead[0].p);
  const pct = pctPlain(ranked[0].s);
  if (a < EARLY) H.title = L.resEarly(a, who, lead.length);
  else if (ranked[0].s < 0.5) H.title = L.resFar(who, pct, lead.length);
  else if (lead.length > 1) H.title = L.resTie(who, pct);
  else H.title = L.resClosest(who);
  return H;
}
function viewResults(keep) {
  state.view = "results";
  state.ret = null;
  clearTimeout(advanceTimer);
  const E = ed(), L = t();
  const a = answeredCount();
  const rank = ranking();
  const H = headline(rank, a);
  show(`
    <div class="res-head">
      <div class="cband cb-res">${flagImg(edCc(E), 32, 24, "cb-flag-sm")}<b>${esc(edName(E))}</b></div>
      <p class="eyebrow">${L.resEyebrow}</p>
      <h1 class="big-title">${esc(H.title)}</h1>
      ${H.straight ? `<p class="notice">${L.straight}</p>` : ""}
      <p>${esc(H.summary)}</p>
      ${H.early && H.more ? `<div class="early"><p>${L.earlyText(EARLY)}</p><button class="btn btn-primary" type="button" data-go="continue">${L.earlyBtn}</button></div>` : ""}
    </div>
    <div class="tabs" role="tablist">${L.tabs.map((x, k) => `<button class="tab" role="tab" id="tab${k}" aria-controls="pan${k}" aria-selected="${state.tab === k}" tabindex="${state.tab === k ? 0 : -1}" type="button" data-tab="${k}">${x}</button>`).join("")}</div>
    <div class="panel" role="tabpanel" id="pan0" aria-labelledby="tab0" ${state.tab === 0 ? "" : "hidden"}>${panelRanking(rank, a)}</div>
    <div class="panel" role="tabpanel" id="pan1" aria-labelledby="tab1" ${state.tab === 1 ? "" : "hidden"}>${panelThemes()}</div>
    <div class="panel" role="tabpanel" id="pan2" aria-labelledby="tab2" ${state.tab === 2 ? "" : "hidden"}>${panelQuestions()}</div>
    <div class="panel" role="tabpanel" id="pan3" aria-labelledby="tab3" ${state.tab === 3 ? "" : "hidden"}>${panelMethod()}</div>
    ${valuesCardHTML()}
    <div class="actions">
      <button class="btn btn-ghost" type="button" data-go="edit">${L.actEdit}</button>
      <button class="btn btn-ghost" type="button" data-go="restart">${L.actRestart}</button>
      <button class="btn btn-ghost" type="button" data-go="home">${L.changeCountry}</button>
    </div>
  `, 2, "screen", keep);
  if (!keep) announce(L.resReady);
}
function panelRanking(rank, a) {
  const E = ed(), L = t();
  const ranked = rank.filter(r => r.grp === "ok"), thin = rank.filter(r => r.grp === "thin"), out = rank.filter(r => r.grp === "out");
  const lead = ranked.length ? topGroup(ranked) : [];
  const tie = lead.length > 1;
  const row = (r, pos, cls) => {
    const shown = r.grp !== "out";
    return `<li class="${cls}">
      <span class="pos">${pos}</span>
      ${badge(r.p)}
      <div class="rank-main">
        <div class="rank-head"><b>${hname(r.p)}</b><span class="pct">${shown ? pctTxt(r.s) : "–"}</span></div>
        <div class="bar" style="--pc:var(${pvar(r.p.id)}, var(--accent))" role="img" aria-label="${shown ? Math.round(r.s * 100) + " " + L.pctWord : L.notRanked}"><span style="width:${shown ? (r.s * 100).toFixed(1) : 0}%"></span></div>
        <div class="rank-sub"><span>${candLine(r.p, E, L, true)}</span><span>${shown ? L.compared(r.k, a) : L.notRanked}</span>${r.grp === "ok" && r.cov < 0.5 ? `<span class="chip warn">${L.partial}</span>` : ""}${r.p.chip ? `<span class="chip grey">${esc(r.p.chip)}</span>` : ""}<button class="link" type="button" data-fiche="${esc(r.p.id)}">${L.seeProfile}</button></div>
      </div>
    </li>`;
  };
  const pos = (r, i) => tie && lead.includes(r) ? `<span aria-hidden="true" dir="ltr">1=</span><span class="sr">${L.posTie}</span>` : String(i + 1);
  return `${ranked.length ? `<ol class="rank">${ranked.map((r, i) => row(r, pos(r, i), lead.includes(r) ? "top" : "")).join("")}</ol>` : ""}
  ${thin.length ? `<h2 class="rank-h">${L.thinTitle}</h2><p class="rank-hp">${L.thinText}</p><ul class="rank">${thin.map(r => row(r, "", "thin")).join("")}</ul>` : ""}
  ${out.length ? `<ul class="rank">${out.map(r => row(r, "–", "out")).join("")}</ul>` : ""}
  <p class="caveat">${L.rankCaveat}</p>`;
}
function panelThemes() {
  const E = ed(), L = t();
  const order = [...state.priorities.map(id => E.themes.find(x => x.id === id)), ...E.themes.filter(x => !state.priorities.includes(x.id))];
  return `<p class="verdict-line">${L.byThemeIntro}</p>
  <div class="theme-cards">${order.map(th => {
    const on = state.priorities.includes(th.id);
    const qIdx = E.questions.map((q, i) => q.theme === th.id ? i : -1).filter(i => i >= 0);
    const answered = qIdx.some(i => typeof state.answers[i] === "number");
    const head = `<div class="tc-head"><h2>${esc(th.name)}</h2>${on ? `<span class="chip">${L.prio}</span>` : ""}</div>`;
    if (!answered) {
      const ks = qIdx.map(i => state.order.indexOf(i)).filter(k => k >= 0);
      // toutes les questions du sujet ont été vues et passées, ou certaines n'ont pas encore été vues
      const allSkipped = qIdx.every(i => state.answers[i] === null);
      return `<article class="theme-card${on ? " prio-on" : ""}">${head}<p class="skipped-note">${allSkipped ? L.themeSkipped : L.themeNotAnswered}</p><div><button class="link" type="button" data-goto="${Math.min(...ks)}" data-until="${Math.max(...ks)}">${L.answerTheme}</button></div></article>`;
    }
    const r = ranking(th.id);
    const ok = r.filter(x => x.grp === "ok"), thin = r.filter(x => x.grp === "thin");
    let phrase;
    if (!ok.length) phrase = thin.length ? L.themeThin : L.themeNoData;
    else {
      const lead = topGroup(ok);
      phrase = lead.length > 1
        ? L.themeTie(esc(th.name), listFmt(lead.map(x => `<b>${hname(x.p)}</b>`)), pctTxt(ok[0].s))
        : L.themeVerdict(esc(th.name), esc(plabel(ok[0].p)), pctTxt(ok[0].s), ok[0].k);
    }
    return `<article class="theme-card${on ? " prio-on" : ""}">${head}
      <p class="verdict-line">${phrase}</p>
      <div class="mini">${r.map(x => x.grp !== "out"
        ? `<div class="mini-row${x.grp === "thin" ? " thin" : ""}">${badge(x.p, "sm")}<span class="name">${hname(x.p)}${x.grp === "thin" ? ` <span class="chip warn">${L.partial}</span>` : ""}</span><div class="bar" style="--pc:var(${pvar(x.p.id)}, var(--accent))"><span style="width:${(x.s * 100).toFixed(1)}%"></span></div><span class="pct">${pctTxt(x.s)}</span></div>`
        : `<div class="mini-row nd">${badge(x.p, "sm")}<span class="name">${hname(x.p)}</span><span class="ndt" style="font-size:.82rem;font-style:italic">${L.notDoc}</span><span></span></div>`).join("")}
      </div>
    </article>`;
  }).join("")}</div>`;
}
function panelQuestions() {
  const E = ed(), L = t();
  return state.order.map((qi, k) => {
    const q = E.questions[qi];
    const v = state.answers[qi];
    const th = E.themes.find(x => x.id === q.theme);
    const cols = [2, 1, 0, -1, -2].map(val => {
      const ps = E.parties.filter(p => q.cells[p.id] && q.cells[p.id].p === val);
      return `<div class="scale-col"><span class="lbl">${L.ansShort[val]}</span><div class="stack">${v === val ? `<span class="you">${L.you}</span>` : ""}${ps.map(p => badge(p, "sm")).join("")}</div></div>`;
    }).join("");
    const nd = E.parties.filter(p => !q.cells[p.id]);
    const yours = typeof v === "number"
      ? `<p style="font-size:.92rem">${L.yourAnswer}${C()} <b>${L.ans[v]}</b></p>`
      : `<p class="skipped-note">${v === null ? L.youSkipped : L.youNotYet}</p>`;
    return `<article class="qa">
      <div class="qa-meta"><span class="mono">${nn(k + 1)}</span><span>${esc(th.name)}</span>${state.priorities.includes(q.theme) ? `<span class="chip">${L.prio}</span>` : ""}${state.double[qi] ? `<span class="chip grey">×2</span>` : ""}</div>
      <p class="qa-text">${esc(q.text)}</p>
      ${yours}
      <div class="scale-wrap"><div class="scale">${cols}</div></div>
      ${nd.length ? `<p class="nd-line">${L.noDocLine} ${nd.map(p => `<span class="chip grey">${esc(p.sigle)}</span>`).join("")}</p>` : ""}
      <details><summary>${L.whatTheySay}</summary>
        <ul class="why-list">${E.parties.map(p => {
          const c = q.cells[p.id];
          if (c) return `<li>${badge(p, "sm")}<div><span class="pos-label">${hname(p)} · ${L.ans[c.p]}</span> <span class="kind">· ${L.kinds[c.k] || esc(c.k)}</span><p>${esc(c.n)}</p>${srcLine([c.s], L)}</div></li>`;
          const note = q.nd && q.nd[p.id];
          return `<li>${badge(p, "sm")}<div><span class="pos-label" style="font-weight:400;font-style:italic">${hname(p)} · ${L.notDoc}</span>${note ? `<p>${esc(note)}</p>` : ""}</div></li>`;
        }).join("")}</ul>
      </details>
      <div><button class="link" type="button" data-goto="${k}">${typeof v === "number" ? L.edit : L.answerIt}</button></div>
    </article>`;
  }).join("");
}
function panelMethod() {
  const E = ed(), L = t();
  const used = uniq([...(E.factsSrc || []), ...(E.systemSrc || []), E.othersSrc, ...E.parties.map(p => p.tagSrc), ...E.questions.flatMap(q => Object.values(q.cells).map(c => c.s)), ...E.parties.flatMap(p => p.commit.map(c => c[1])), E.meta.src]).filter(id => E.src[id]);
  const coding = E.role === "leader" ? [L.mCodingLead, ...L.mCoding.slice(1)] : L.mCoding;
  return `<div class="method">
    <h2>${L.mFormulaTitle}</h2>
    <p>${L.mFormula1}</p>
    <p class="formula" dir="ltr" tabindex="0">${L.formula}</p>
    <p>${L.mFormula2}</p>
    <h2>${L.mRulesTitle}</h2>
    <ul class="rules">${L.mRules.map(x => `<li>${x}</li>`).join("")}</ul>
    <h2>${L.mCodingTitle}</h2>
    <ul>${coding.map(x => `<li>${x}</li>`).join("")}${E.lang !== E.baseLang ? `<li class="transl">${L.mTransl}</li>` : ""}</ul>
    <h2>${L.mCovTitle}</h2>
    <div class="tbl-wrap"><table class="cov"><thead><tr><th>${L.mCovParty}</th><th style="text-align:end">${L.mCovN}</th></tr></thead><tbody>
      ${E.parties.map(p => ({ p, n: documented(p.id) })).sort((x, y) => y.n - x.n).map(({ p, n }) => `<tr><td>${esc(label(p))}</td><td class="num">${n} / ${E.questions.length}</td></tr>`).join("")}
    </tbody></table></div>
    <h2>${L.mNotTitle}</h2>
    <ul>${L.mNot.map(x => `<li>${x}</li>`).join("")}</ul>
    <h2>${L.mSrcTitle}</h2>
    <ol class="src-list">${used.map(id => { const s = E.src[id]; return `<li><a href="${esc(s.u)}" target="_blank" rel="noopener">${esc(s.t)}</a> · ${esc(s.o)}, ${esc(srcDate(s.d))}</li>`; }).join("")}</ol>
  </div>`;
}

/* ================== Module « valeurs » et compteur collectif ==================
   10 énoncés identiques dans tous les pays (src/values.js). Les réponses ne servent jamais à classer les partis : elles vivent
   à part (state.vals) et donnent une position personnelle sur cinq niveaux, que l'on peut — si une adresse de compteur est
   configurée (meter.config.json) — ajouter, anonymement, au compteur de toute l'Afrique. Rien ne part sans un geste explicite,
   et seuls partent le code du pays et un niveau (jamais les réponses). */
const VAL_MIN = 6;      // réponses minimum pour avoir une position
const METER_MIN = 30;   // contributions minimum avant d'afficher un compteur
/* Position : v = ax × réponse / 2, s = moyenne de v sur les énoncés répondus (les passés sont ignorés), au moins 6 réponses.
   Seuils : s ≥ 0,5 → 2 ; 0,15 < s < 0,5 → 1 ; |s| ≤ 0,15 → 0 ; −0,5 < s < −0,15 → −1 ; s ≤ −0,5 → −2.
   Calculé en entiers (S = Σ ax × réponse, n réponses : s = S / 2n) pour que les seuils soient exacts. */
function valuesLevel(vals) {
  let S = 0, n = 0;
  VALUES.forEach(v => { const a = vals && vals[v.id]; if (typeof a === "number" && a >= -2 && a <= 2) { S += v.ax * a; n++; } });
  const out = { n: n, need: Math.max(0, VAL_MIN - n), s: n ? S / (2 * n) : 0, level: null };
  if (n < VAL_MIN) return out;
  out.level = S >= n ? 2 : 10 * S > 3 * n ? 1 : 10 * S >= -3 * n ? 0 : S > -n ? -1 : -2;
  return out;
}
const vtext = v => v[state.ui] || v.en;
const valStarted = () => Object.keys(state.vals).length > 0;

/* ---------- Compteur collectif : lecture (GET <adresse>/counts, une fois par session) ---------- */
const meter = { status: METER_ENDPOINT ? "idle" : "off", data: null, p: null, sent: {} };
function normCounts(j) {
  const num = o => { const r = {}; [-2, -1, 0, 1, 2].forEach(k => { const v = o && +o[k]; r[k] = v > 0 && isFinite(v) ? Math.floor(v) : 0; }); return r; };
  if (!j || typeof j !== "object" || !j.total || typeof j.total !== "object") throw new Error("bad counts");
  const by = {};
  if (j.byCountry && typeof j.byCountry === "object") Object.keys(j.byCountry).forEach(c => { if (/^[a-z]{2}$/.test(c)) by[c] = num(j.byCountry[c]); });
  return { updated: typeof j.updated === "string" ? j.updated : "", total: num(j.total), byCountry: by };
}
function loadMeter(force) {
  if (!METER_ENDPOINT) return Promise.resolve(null);
  if (force) { meter.status = "idle"; meter.p = null; }
  if (meter.p) return meter.p;
  if (meter.status === "fail") return Promise.resolve(null);
  meter.status = "loading";
  const ac = typeof AbortController === "function" ? new AbortController() : null;
  let timer = null;
  const timeout = new Promise((_, rej) => { timer = setTimeout(() => { if (ac) ac.abort(); rej(new Error("timeout")); }, 6000); });
  const get = fetch(METER_ENDPOINT + "/counts", ac ? { credentials: "omit", mode: "cors", signal: ac.signal } : { credentials: "omit", mode: "cors" })
    .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); }).then(normCounts);
  meter.p = Promise.race([get, timeout]).then(d => { clearTimeout(timer); meter.data = d; meter.status = "ok"; return d; },
    () => { clearTimeout(timer); meter.status = "fail"; meter.p = null; return null; });
  return meter.p;
}
function retryMeter() { loadMeter(true).then(fillMeters); fillMeters(); }
const nfmt = n => { try { return new Intl.NumberFormat(locale()).format(n); } catch (e) { return String(n); } };
const fillSpan = (kind, w) => `<span class="mfill ${kind}${w > 0 ? "" : " z"}" style="--w:${w.toFixed(1)}%"></span>`;
function meterShares(c) {
  const g = k => (c && +c[k]) || 0;
  return { tot: g(-2) + g(-1) + g(0) + g(1) + g(2), pro: g(1) + g(2), con: g(-1) + g(-2), bal: g(0) };
}
/* Emplacement d'un compteur (rempli quand les chiffres sont arrivés) : « africa » = toute l'Afrique, « country » = ce pays */
function meterSlot(scope, cc, h) {
  if (!METER_ENDPOINT) return "";
  return `<div class="meter-slot" data-meter="${scope}"${cc ? ` data-cc="${esc(cc)}"` : ""}${h ? ` data-h="${h}"` : ""}${meter.status === "ok" || meter.status === "fail" ? "" : ' data-state="loading"'}></div>`;
}
function meterHTML(scope, cc, h) {
  h = h || 3;
  const L = t(), d = meter.data;
  if (!d) return "";
  const africa = scope === "africa";
  const m = meterShares(africa ? d.total : d.byCountry[cc]);
  if (!africa && m.tot < METER_MIN) return "";
  if (m.tot < METER_MIN) {
    return `<section class="meter meter-wait" aria-labelledby="mt-${scope}">
      <h${h} class="mt" id="mt-${scope}">${L.meterTitle}</h${h}>
      <p>${L.meterOpens(nfmt(m.tot))}</p>
      <div class="mprog" role="progressbar" aria-label="${esc(L.meterTitle)}" aria-valuemin="0" aria-valuemax="${METER_MIN}" aria-valuenow="${m.tot}"><span style="inline-size:${(m.tot / METER_MIN * 100).toFixed(1)}%"></span></div>
      <p class="m-cav">${L.meterCaveat}</p>
    </section>`;
  }
  const pct = k => pctPlain(m[k] / m.tot);
  const countries = Object.keys(d.byCountry).filter(c => meterShares(d.byCountry[c]).tot > 0).length;
  const people = L.meterPeople(nfmt(m.tot), africa ? countries : 1);
  const when = d.updated && /^\d{4}-\d\d-\d\d/.test(d.updated) ? L.meterUpdated(fmtDate(d.updated.slice(0, 10))) : "";
  const label = africa ? L.meterAfrica : cname(A2ID[cc]);
  const aria = L.meterAria(label, pct("pro"), pct("con"), pct("bal"), people, when || "");
  return `<section class="meter" aria-labelledby="mt-${scope}">
    <h${h} class="mt" id="mt-${scope}">${africa ? L.meterTitle : esc(label)}</h${h}>
    ${africa ? "" : `<p class="m-scope">${L.meterTitle}</p>`}
    <div class="m-ends"><span class="m-end m-pro"><b dir="ltr">${pct("pro")}</b> ${L.meterPro}</span><span class="m-end m-con"><b dir="ltr">${pct("con")}</b> ${L.meterCon}</span></div>
    <div class="mwrap"><div class="mbar" role="img" aria-label="${esc(aria)}"><div class="mhalf">${fillSpan("pro", m.pro / m.tot * 100)}</div><div class="mhalf">${fillSpan("con", m.con / m.tot * 100)}</div><i class="mtick"></i></div></div>
    <p class="m-sub">${esc(L.meterBal(pct("bal")))} · ${esc(people)}${when ? " · " + esc(when) : ""}</p>
    <p class="m-cav">${L.meterCaveat}</p>
    <details class="m-defs"><summary>${L.meterDefsSummary}</summary><p>${L.meterDefs}</p></details>
  </section>`;
}
function fillMeters() {
  const slots = document.querySelectorAll("[data-meter]");
  if (!slots.length) return;
  slots.forEach(el => {
    const html = meter.status === "ok" ? meterHTML(el.dataset.meter, el.dataset.cc, +el.dataset.h || 3) : "";
    if (meter.status === "ok" || meter.status === "fail") el.removeAttribute("data-state");
    el.innerHTML = html;
    el.hidden = !html && meter.status !== "idle" && meter.status !== "loading";
    // Remplissage animé une seule fois (mouvement autorisé seulement) : la barre garde sa place, rien ne bouge autour
    const box = el.firstElementChild;
    if (box && box.classList.contains("meter")) { box.classList.remove("go"); window.requestAnimationFrame(() => window.requestAnimationFrame(() => box.classList.add("go"))); }
  });
  // « Réessayer » dans le texte « comment ça marche » seulement quand le chargement a échoué
  document.querySelectorAll("[data-meterfail]").forEach(el => { el.hidden = meter.status !== "fail"; });
}
/* Après chaque affichage : remplit les compteurs présents (depuis la mémoire, ou après le chargement) */
function meterHook() {
  if (!METER_ENDPOINT || !document.querySelector("[data-meter],[data-meterfail]")) return;
  if (meter.status === "ok" || meter.status === "fail") fillMeters();
  else loadMeter().then(fillMeters);
}

/* ---------- Compteur collectif : envoi (POST <adresse>/v, {c, l}), un seul par pays et par navigateur ---------- */
const sentKey = cc => "etv.sent." + cc;
const alreadySent = cc => !!cc && (meter.sent[cc] || getItem("localStorage", sentKey(cc)) === "1");
function sendBlockHTML() {
  if (!METER_ENDPOINT) return "";
  const L = t(), cc = curCc();
  return `<div class="vsend">
    <p class="m-sentwhat">${L.meterSentWhat}</p>
    ${alreadySent(cc) ? `<p class="m-ok" role="status">✓ ${L.meterThanks}</p>` : `<button class="btn btn-primary" type="button" data-go="vsend">${L.meterSend}</button>`}
    <p class="m-err" role="status" id="meterErr" hidden></p>
  </div>`;
}
function sendMeter(btn) {
  const L = t(), cc = curCc(), r = valuesLevel(state.vals);
  if (!METER_ENDPOINT || !cc || r.level === null || (btn && btn.disabled)) return;
  const err = $("meterErr");
  if (err) err.hidden = true;
  if (btn) { btn.disabled = true; btn.textContent = L.meterSending; }
  const fail = () => {
    if (btn) { btn.disabled = false; btn.textContent = L.meterRetry; btn.focus({ preventScroll: true }); }
    if (err) { err.textContent = L.meterErr; err.hidden = false; }
  };
  let req;
  try {
    req = fetch(METER_ENDPOINT + "/v", { method: "POST", headers: { "Content-Type": "text/plain" }, body: JSON.stringify({ c: cc, l: r.level }), keepalive: true, credentials: "omit", mode: "cors" });
  } catch (e) { return fail(); }
  req.then(res => {
    if (!res.ok) throw new Error("HTTP " + res.status);
    meter.sent[cc] = true;
    setItem("localStorage", sentKey(cc), "1");
    const box = btn && btn.closest(".vsend");
    if (box) { const ok = document.createElement("p"); ok.className = "m-ok"; ok.setAttribute("role", "status"); ok.setAttribute("tabindex", "-1"); ok.textContent = "✓ " + L.meterThanks; btn.replaceWith(ok); ok.focus({ preventScroll: true }); }
    announce(L.meterThanks);
    loadMeter(true).then(fillMeters);
  }).catch(fail);
}

/* ---------- Position personnelle : barre à deux sens (comme le compteur), avec un repère ---------- */
const MY_FILL = { "2": 100, "1": 50, "0": 0, "-1": 50, "-2": 100 };
const MY_POS = { "2": 0, "1": 25, "0": 50, "-1": 75, "-2": 100 };   // % depuis le côté « début » de la barre
function myBarHTML(level) {
  const L = t();
  const side = k => (k === "pro" ? level > 0 : level < 0) ? MY_FILL[level] : 0;
  return `<div class="mwrap"><div class="mbar" role="img" aria-label="${esc(L.valBarLabel + " : " + L.valLevels[level])}"><div class="mhalf">${fillSpan("pro", side("pro"))}</div><div class="mhalf">${fillSpan("con", side("con"))}</div><i class="mtick"></i></div><i class="mmark" style="inset-inline-start:${MY_POS[level]}%"></i></div>
    <div class="m-ends"><span class="m-end m-pro">${L.meterPro}</span><span class="m-end m-con">${L.meterCon}</span></div>`;
}
/* « Comment ça marche ? » : le module mesure des valeurs, pas la gauche ou la droite économique ; le compteur montre des participants volontaires */
function valHowHTML() {
  const L = t();
  return `<details class="v-how"><summary>${L.valHowSummary}</summary>${L.valHow.map(x => `<p>${x}</p>`).join("")}<p class="m-defs-p">${L.meterDefs}</p>
    <p data-meterfail hidden><button class="link" type="button" data-go="vretry">${L.meterRetryLoad}</button></p></details>`;
}
function valWhichHTML() {
  const L = t();
  return `<details class="v-which"><summary>${L.valWhich}</summary><ol class="v-list">${VALUES.map(v => {
    const a = state.vals[v.id], tx = vtext(v);
    const ans = typeof a === "number" ? L.ans[a] : L.valSkippedA;
    return `<li><span class="vq-t">${esc(tx.text)}</span><span class="vq-d">${v.ax === 1 ? L.valDirPro : L.valDirCon}</span><span class="vq-a">${L.valYourAns}${C()} <b>${esc(ans)}</b></span></li>`;
  }).join("")}</ol></details>`;
}
/* La carte « Où tu te situes sur les valeurs » (résultats, fin du module, pages de pays) */
function valuesCardHTML(quiet) {
  const L = t(), r = valuesLevel(state.vals);
  const intro = METER_ENDPOINT ? L.valIntroText : L.valIntroTextLocal;
  if (r.level === null) {
    const started = valStarted();
    return `<section class="vcard" aria-labelledby="vcT">
      <h2 id="vcT">${started ? L.valCardTitle : L.valIntroTitle}</h2>
      <p>${started ? L.valNeedMore(r.need) : intro}</p>
      <div class="actions"><button class="btn btn-${quiet ? "ghost" : "primary"}" type="button" data-go="vopen">${started ? L.valContinue : L.valAnswerCta}</button></div>
      ${valHowHTML()}
      ${meterSlot("africa")}${meterSlot("country", curCc())}
    </section>`;
  }
  return `<section class="vcard" aria-labelledby="vcT">
    <h2 id="vcT">${L.valCardTitle}</h2>
    <p class="v-level"><b>${L.valLevels[r.level]}</b></p>
    ${myBarHTML(r.level)}
    <p class="muted">${L.valBasis(r.n)}</p>
    ${valWhichHTML()}
    ${sendBlockHTML()}
    ${meterSlot("africa")}${meterSlot("country", curCc())}
    ${valHowHTML()}
    <div class="actions"><button class="btn btn-ghost" type="button" data-go="vedit">${L.valChange}</button></div>
  </section>`;
}

/* ---------- Écrans : présentation, questions, position ---------- */
const hasPartyResults = () => !!(state.country && DATA[state.country] && DATA[state.country].kind === "ed" && state.order.length && answeredCount() > 0);
function valBand() {
  const cc = curCc();
  if (!cc) return "";
  const name = cc === "fr" ? catName("fr") : cname(A2ID[cc]);
  return `<div class="cband cb-res">${flagImg(cc, 32, 24, "cb-flag-sm")}<b>${esc(name)}</b></div>`;
}
function viewValues(rest, id) {
  if (id) { state.place = id; state.country = null; }
  const a = rest[0];
  if (a === "done") return viewValuesDone();
  const n = parseInt(a, 10);
  if (n >= 1 && n <= VALUES.length) { state.vi = n - 1; return viewValuesQ(); }
  return viewValuesIntro();
}
function viewValuesIntro(keep) {
  state.view = "valintro";
  state.vseen = true;
  const L = t();
  show(`
    ${valBand()}
    <div class="block">
      <p class="eyebrow">${L.valBonusEyebrow}</p>
      <h1 class="big-title">${L.valIntroTitle}</h1>
      <p class="lead">${METER_ENDPOINT ? L.valIntroText : L.valIntroTextLocal}</p>
    </div>
    ${METER_ENDPOINT ? `<p class="muted">${L.meterSentWhat}</p>` : ""}
    ${valHowHTML()}
    <div class="actions">
      <button class="btn btn-primary" type="button" data-go="vstart">${L.valStart}</button>
      <button class="btn btn-ghost" type="button" data-go="${hasPartyResults() ? "vresults" : "vback"}">${hasPartyResults() ? L.valSkipResults : L.valBackCountry}</button>
    </div>
  `, null, "screen", keep);
}
function viewValuesQ(keep) {
  state.view = "valq";
  const L = t(), v = VALUES[state.vi], tx = vtext(v), cur = state.vals[v.id];
  const n = VALUES.length, pos = state.vi + 1;
  show(`
    <div class="q-top">
      <span class="q-count mono" dir="ltr">${pos} / ${n}</span>
      <div class="qbar" role="progressbar" aria-label="${esc(L.valProgress)}" aria-valuemin="1" aria-valuemax="${n}" aria-valuenow="${pos}" aria-valuetext="${esc(L.qOf(pos, n))}"><span style="width:${(pos / n * 100).toFixed(1)}%"></span></div>
    </div>
    <div class="q-meta"><span class="chip val">${L.valChip}</span></div>
    <div class="slip"><h1>${esc(tx.text)}</h1></div>
    <fieldset class="answers" data-vq="${v.id}"><legend class="sr">${L.yourAnswer}</legend>
      ${[2, 1, 0, -1, -2].map(val => `<button type="button" class="ans" data-vv="${val}" aria-pressed="${cur === val}"><span class="box" aria-hidden="true">${CHECK}</span><span>${L.ans[val]}</span></button>`).join("")}
    </fieldset>
    <div class="q-nav">
      <button class="btn btn-ghost" type="button" data-go="vprev" ${state.vi === 0 ? "disabled" : ""}>${L.prev}</button>
      <div class="actions"><button class="btn btn-ghost" type="button" data-vv="skip">${cur === null ? L.skipped : L.skip}</button></div>
    </div>
  `, null, "screen q-screen", keep);
  qShownAt = now();
  if (!keep) announce(L.qOf(pos, n));
}
function valAnswer(val, id) {
  if (state.view !== "valq" || VALUES[state.vi].id !== id) return;
  state.vals[id] = val;
  document.querySelectorAll(".answers .ans").forEach(b => b.setAttribute("aria-pressed", String(+b.dataset.vv === val)));
  save();
  clearTimeout(advanceTimer);
  advanceTimer = setTimeout(nextV, 240);
}
function nextV() {
  if (state.view !== "valq") return;
  if (state.vi < VALUES.length - 1) { state.vi++; viewValuesQ(); }
  else viewValuesDone();
}
function viewValuesDone(keep) {
  state.view = "valres";
  const L = t();
  show(`
    ${valBand()}
    <div class="block">
      <h1 class="big-title">${L.valDoneTitle}</h1>
    </div>
    ${valuesCardHTML()}
    <div class="actions">
      ${hasPartyResults() ? `<button class="btn btn-primary" type="button" data-go="vresults">${L.valToResults}</button>` : `<button class="btn btn-primary" type="button" data-go="vback">${L.valBackCountry}</button>`}
    </div>
  `, null, "screen", keep);
}

/* ================== Fiche parti ================== */
function openFiche(pid) {
  const E = ed(), L = t();
  const p = E.parties.find(x => x.id === pid);
  if (!p) return;
  const sc = answeredCount() ? score(pid) : { s: null, k: 0 };
  $("ficheBody").innerHTML = `
    <div class="fiche-head">
      ${badge(p, "lg")}
      <div><h2 id="ficheTitle">${hname(p)}</h2><p>${candLine(p, E, L)}${p.vp ? ` · ${L.runningMate}${C()} ${esc(p.vp)}` : ""}</p></div>
      <button class="close" type="button" id="ficheClose" aria-label="${L.ficheClose}">×</button>
    </div>
    ${p.chip ? `<p><span class="chip warn">${esc(p.chip)}</span></p>` : ""}
    <p style="font-size:.95rem">${esc(p.tag)}${p.tagSrc && srcLink(p.tagSrc) ? ` <span class="src muted">(${srcLink(p.tagSrc)})</span>` : ""}</p>
    ${sc.k >= 2 ? `<div class="fiche-score"><span class="pct">${pctTxt(sc.s)}</span><span>${L.ficheScore}</span></div>` : ""}
    <p class="mono muted" style="font-size:.85rem">${L.ficheDoc(documented(pid), E.questions.length)}</p>
    <section><h3>${L.ficheCommit}</h3><ul class="commit">${p.commit.map(([c, s]) => `<li><span>${esc(c)}</span>${srcLink(s) ? `<span class="src muted">${L.source}${C()} ${srcLink(s)}</span>` : ""}</li>`).join("")}</ul></section>
    <section><h3>${L.fichePos}</h3><ul class="pos-table">${E.questions.map(q => {
      const c = q.cells[pid];
      return `<li><span>${esc(q.short)}</span><span class="pv${c ? "" : " nd"}">${c ? L.ans[c.p] : L.notDoc}</span></li>`;
    }).join("")}</ul></section>`;
  const dlg = $("fiche");
  if (typeof dlg.showModal === "function") { if (!dlg.open) dlg.showModal(); } else dlg.setAttribute("open", "");
  dlg.scrollTop = 0;
  $("ficheClose").focus();
}
function closeFiche() { const d = $("fiche"); if (d.open) { if (typeof d.close === "function") d.close(); else d.removeAttribute("open"); } }

/* ================== Confirmation avant d'effacer des réponses ==================
   Dans la page (confirm() est bloqué chez certains hébergeurs) : une ligne sous le bouton, avec « Effacer… » et « Annuler ». */
let confirmFrom = null;
function needsConfirm() { return ["start", "question", "checkpoint", "results"].includes(state.view) && answeredCount() > 0; }
function dropConfirm(refocus) {
  const box = $("confirmBox");
  if (box) box.remove();
  if (refocus && confirmFrom && document.contains(confirmFrom)) confirmFrom.focus();
  confirmFrom = null;
}
function askConfirm(kind, el) {
  const L = t();
  dropConfirm();
  confirmFrom = el || null;
  const box = document.createElement("div");
  box.className = "confirm"; box.id = "confirmBox";
  box.setAttribute("role", "group"); box.setAttribute("aria-labelledby", "confirmMsg");
  box.innerHTML = `<p id="confirmMsg" tabindex="-1" data-focus-target>${esc(L.confirmLose(answeredCount()))}</p><div class="actions"><button class="btn btn-primary" type="button" data-go="${kind}!">${kind === "home" ? L.confirmHome : L.confirmRestart}</button><button class="btn btn-ghost" type="button" data-go="noconfirm">${L.cancel}</button></div>`;
  const anchor = el && $("app").contains(el) ? el.closest(".actions, .strip, .q-nav") : null;
  if (anchor) anchor.insertAdjacentElement("afterend", box);
  else { const sec = $("app").firstElementChild; sec.insertBefore(box, sec.firstChild); }
  $("confirmMsg").focus({ preventScroll: true });
  box.scrollIntoView({ block: "nearest" });
}

/* ================== Navigation ================== */
function resetAnswers() { state.answers = {}; state.double = {}; state.i = 0; state.tab = 0; state.order = []; state.nPrio = 0; state.ret = null; state.vals = {}; state.vi = 0; state.vseen = false; }
function goHome(clear) {
  loadSeq++;
  closeFiche();
  if (clear) { resetAnswers(); state.priorities = []; state.ac = null; }
  navMode = state.view === "map" ? "replace" : "push";
  viewMap();
}
function go(where, el) {
  clearTimeout(advanceTimer); clearTimeout(backTimer);
  switch (where) {
    case "home": if (needsConfirm()) return askConfirm("home", el); return goHome(false);
    case "home!": return goHome(true);
    case "restart": if (needsConfirm()) return askConfirm("restart", el);
    // falls through
    case "restart!": resetAnswers(); state.priorities = []; navMode = "push"; return viewStart();
    case "noconfirm": return dropConfirm(true);
    case "france": return navTo("#/fr/fr");
    case "nigeria": return navTo(`#/ng/${CATALOG.ng.langs.includes(state.ui) ? state.ui : CATALOG.ng.langs[0]}`);
    case "retry": return route(location.hash);
    case "startq": buildOrder(); state.i = 0; state.ret = null; navMode = "push"; return viewQuestion();
    case "resume": {
      const qi = state.order[state.i];
      buildOrder();
      state.i = Math.max(0, state.order.indexOf(qi));
      state.ret = null; navMode = "push";
      return viewQuestion();
    }
    case "qlist": return openQList();
    case "vstart": state.vi = 0; navMode = "push"; return viewValuesQ();
    case "vopen": { const k = VALUES.findIndex(v => state.vals[v.id] === undefined); state.vi = k >= 0 ? k : 0; navMode = "push"; return viewValuesQ(); }
    case "vprev": if (state.vi > 0) { state.vi--; viewValuesQ(); } return;
    case "vedit": state.vi = 0; navMode = "push"; return viewValuesQ();
    case "vresults": state.tab = 0; state.ret = null; navMode = state.view === "valintro" ? "replace" : "push"; return viewResults();
    case "vback": return navTo(`#/${curCc()}/${state.ui}`);
    case "vsend": return sendMeter(el);
    case "vretry": return retryMeter();
    case "prev": if (state.i > 0) { state.i--; viewQuestion(); } return;
    case "more": state.i = state.nPrio; return viewQuestion();
    case "results": state.tab = 0; return toResults();
    case "edit": {
      const u = lastSeen();
      state.ret = { until: u >= 0 ? u : state.order.length - 1 };
      state.i = 0; navMode = "push-ret";
      return viewQuestion();
    }
    case "continue": {
      const k = firstOpen();
      if (k < 0) return;
      state.ret = { until: state.order.length - 1 };
      state.i = k; navMode = "push-ret";
      return viewQuestion();
    }
  }
}
document.addEventListener("click", e => {
  if (e.target === $("langDlg")) return closeLang();
  if (e.target === $("fiche")) return closeFiche();
  if (e.target === $("qDlg")) return closeQList();
  const el = e.target.closest("[data-pick],[data-place],[data-lang],[data-go],[data-prio],[data-val],[data-vv],[data-dbl],[data-goto],[data-tab],[data-fiche],[data-qjump],#ficheClose,#langCancel,#qClose,#skip,#brand");
  if (!el) return;
  if (el.id === "skip") { e.preventDefault(); return skipToList(); }
  if (el.id === "qClose") return closeQList();
  if (el.dataset.qjump !== undefined) { closeQList(); state.i = +el.dataset.qjump; return viewQuestion(); }
  if (el.id === "ficheClose") return closeFiche();
  if (el.id === "langCancel") return closeLang();
  if (el.id === "brand") return go("home", el);
  if (el.dataset.pick) return el.getAttribute("aria-disabled") === "true" ? undefined : pickLang(el.dataset.pick);
  if (el.dataset.place) return chooseCountry(el.dataset.place);
  if (el.dataset.lang) {
    // Langue pas encore traduite : le bouton reste focalisable, un toucher explique (infobulle, 3 s) au lieu de ne rien faire
    if (el.getAttribute("aria-disabled") === "true") { langTip(el); langTipTimer = setTimeout(() => langTip(null), 3000); return; }
    const code = el.dataset.lang;
    setUi(code, true);
    rerender();
    const b = document.querySelector(`#langs [data-lang="${code}"]`); if (b) b.focus({ preventScroll: true });
    return;
  }
  if (el.dataset.go) return go(el.dataset.go, el);
  if (el.dataset.fiche) return openFiche(el.dataset.fiche);
  if (el.dataset.prio) {
    const id = el.dataset.prio;
    const k = state.priorities.indexOf(id);
    if (k >= 0) state.priorities.splice(k, 1); else if (state.priorities.length < 3) state.priorities.push(id);
    const y = window.scrollY;
    viewStart(true);
    window.scrollTo({ top: y });
    const again = document.querySelector(`[data-prio="${CSS.escape(id)}"]`); if (again) again.focus({ preventScroll: true });
    announce(t().chosen(state.priorities.length));
    return;
  }
  if (el.dataset.vv !== undefined) {
    if (e.detail > 0 && now() - qShownAt < TAP_GUARD) return;
    const host = el.closest("[data-vq]");
    return valAnswer(el.dataset.vv === "skip" ? null : +el.dataset.vv, host ? host.dataset.vq : VALUES[state.vi].id);
  }
  if (el.dataset.val) {
    // Un second tapotement juste après l'affichage (double tapotement) ne répond pas à la question suivante ; le clavier (detail 0) n'est pas freiné
    if (e.detail > 0 && now() - qShownAt < TAP_GUARD) return;
    const host = el.closest("[data-q]");
    return answer(el.dataset.val === "skip" ? null : +el.dataset.val, host ? +host.dataset.q : state.order[state.i]);
  }
  if (el.dataset.dbl) {
    const qi = +el.dataset.dbl;
    if (state.double[qi]) delete state.double[qi]; else state.double[qi] = true;
    el.setAttribute("aria-pressed", String(!!state.double[qi]));
    save();
    return;
  }
  if (el.dataset.goto) {
    closeFiche();
    if (!state.order.length) buildOrder();
    const k = +el.dataset.goto;
    // Depuis les résultats : nouvel écran, et retour aux résultats une fois la question (ou le sujet) corrigée
    if (state.view === "results") { state.ret = { until: el.dataset.until ? +el.dataset.until : k }; navMode = "push-ret"; }
    state.i = k; return viewQuestion();
  }
  if (el.dataset.tab) {
    state.tab = +el.dataset.tab;
    document.querySelectorAll('[role="tab"]').forEach((b, k) => { b.setAttribute("aria-selected", String(k === state.tab)); b.tabIndex = k === state.tab ? 0 : -1; });
    document.querySelectorAll('[role="tabpanel"]').forEach((p, k) => { p.hidden = k !== state.tab; });
    setHash(hashFor(), false);
    save();
  }
});
/* Onglets : tabindex mobile, flèches (inversées de droite à gauche), Début et Fin. */
document.addEventListener("keydown", e => {
  if (!e.target.closest || !e.target.closest('[role="tablist"]')) return;
  if (!["ArrowRight", "ArrowLeft", "Home", "End"].includes(e.key)) return;
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const k = tabs.indexOf(document.activeElement);
  if (k < 0) return;
  e.preventDefault();
  const fwd = (e.key === "ArrowRight") !== (document.documentElement.dir === "rtl");
  const n = e.key === "Home" ? 0 : e.key === "End" ? tabs.length - 1 : (k + (fwd ? 1 : tabs.length - 1)) % tabs.length;
  tabs[n].focus(); tabs[n].click();
});
/* Langue indisponible : infobulle au survol et au focus clavier. */
$("langs").addEventListener("mouseover", e => { const b = e.target.closest && e.target.closest('[aria-disabled="true"]'); if (b) langTip(b); });
$("langs").addEventListener("mouseout", () => langTip(null));
$("langs").addEventListener("focusin", e => { const b = e.target.closest && e.target.closest('[aria-disabled="true"]'); langTip(b || null); });
$("langs").addEventListener("focusout", () => langTip(null));
document.addEventListener("keydown", e => { if (e.key === "Escape") langTip(null); });
window.addEventListener("popstate", () => route(location.hash));
window.addEventListener("hashchange", () => { if (location.hash !== curHash) route(location.hash); });
try { history.scrollRestoration = "manual"; } catch (e) { }

/* Pour les tests : le calcul de la position et les parts du compteur sont des fonctions pures */
window.__etv = { valuesLevel: valuesLevel, meterShares: meterShares, VALUES: VALUES, METER_ENDPOINT: METER_ENDPOINT, METER_MIN: METER_MIN, VAL_MIN: VAL_MIN };

/* Démarrage : langue (appareil → navigateur → anglais), session de cet onglet, puis l'écran que décrit l'adresse. */
state.ui = initialUi();
restore();
route(location.hash);
</script>
