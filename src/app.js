
/* ================== Éditions ==================
   Chaque pays a son fichier data/<cc>.json (questionnaire « ed » ou page d'information « info »), chargé à la demande.
   CATALOG, généré par tools/build.js, dit sans rien charger quels pays en ont un, dans quelles langues, et quand a lieu le vote. */
const DATA = {};
const A3CC = {};
Object.entries(CATALOG).forEach(([cc, c]) => { if (c.a3) A3CC[c.a3] = cc; });
const catFor = id => (A3CC[id] ? CATALOG[A3CC[id]] : null);
const UP_FROM = "2026-10", UP_TO = "2027-12-31";

/* ================== État ================== */
const state = { ui: "fr", country: null, place: null, view: "map", priorities: [], order: [], nPrio: 0, i: 0, answers: {}, double: {}, tab: 0, pending: null, loadCc: null };
const PRIOR_ALL = 3, PRIOR_THEME = 1;
const $ = id => document.getElementById(id);
const t = () => T[state.ui] || T.fr;
const edCache = {};
const ed = () => {
  const key = state.country + ":" + state.ui;
  if (!edCache[key]) edCache[key] = localizeEdition(DATA[state.country], state.ui);
  return edCache[key];
};
const nn = n => String(n).padStart(2, "0");
const C = () => state.ui === "fr" ? " :" : ":";
const pctTxt = s => Math.round(s * 100) + '<span class="pu"> %</span>';
const esc = s => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const uniq = a => a.filter((v, i) => v && a.indexOf(v) === i);
const label = p => `${p.sigle} · ${p.nom}`;
const ISO = [String.fromCharCode(0x2068), String.fromCharCode(0x2069)];
const pname = p => ISO[0] + p.nom + ISO[1];
const hname = p => esc(pname(p));
const langOf = code => LANGS.find(l => l.code === code);
const locale = () => (langOf(state.ui) || LANGS[1]).locale;

/* Traduction d'une édition : le texte de base est remplacé, champ par champ, par celui de I18N quand il existe. */
function localizeEdition(D, lang) {
  const base = D.kind === "info" ? D.info : D.ed;
  const E = JSON.parse(JSON.stringify(base));
  E.kind = D.kind; E.cc = D.id; E.a3 = D.a3; E.baseLang = D.lang; E.meta = D.meta || {}; E.src = D.src || {};
  E.langs = LANGS.map(l => ({ code: l.code, label: l.code.toUpperCase(), name: l.name, ready: D.langs.includes(l.code) }));
  const L = lang !== D.lang && D.i18n && D.i18n[lang];
  E.lang = L ? lang : D.lang;
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

/* Couleurs des partis : --c-<édition>-<parti>, clair et sombre, injectées au chargement de l'édition. */
const cssId = s => String(s).toLowerCase().replace(/[^a-z0-9_-]/g, "-");
const pvar = pid => `--c-${cssId(state.country)}-${cssId(pid)}`;
const hex = c => (/^#[0-9a-f]{3,8}$/i.test(c || "") ? c : "");
function injectColours(D) {
  if (D.kind !== "ed" || !D.ed || $("pc-" + cssId(D.id))) return;
  const vars = k => D.ed.parties.map(p => {
    const c = hex((p.col || [])[k]) || hex((p.col || [])[0]);
    return c ? `--c-${cssId(D.id)}-${cssId(p.id)}:${c}` : "";
  }).filter(Boolean).join(";");
  const st = document.createElement("style");
  st.id = "pc-" + cssId(D.id);
  st.textContent = `:root{${vars(0)}}@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){${vars(1)}}}:root[data-theme="dark"]{${vars(1)}}`;
  (document.head || document.documentElement).appendChild(st);
}
function loadEdition(cc) {
  if (DATA[cc]) return Promise.resolve(DATA[cc]);
  return fetch(`data/${encodeURIComponent(cc)}.json`)
    .then(r => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(D => {
      if (!D || D.id !== cc || !(D.ed || D.info)) throw new Error("bad data");
      DATA[cc] = D;
      injectColours(D);
      return D;
    });
}

function badge(p, size) {
  return `<span class="badge ${size || ""}" style="--pc:var(${pvar(p.id)}, var(--accent))" aria-hidden="true">${esc(p.sigle)}</span>`;
}
function srcObj(id) {
  const D = state.country && DATA[state.country];
  return (D && D.src && D.src[id]) || SRC_AF[id] || null;
}
function srcA(s) {
  return s ? `<a href="${esc(s.u)}" target="_blank" rel="noopener">${esc(s.o)}, ${esc(s.d)}</a>` : "";
}
const srcLink = id => srcA(srcObj(id));
const srcLine = (ids, L, style) => {
  const links = uniq(ids || []).map(srcLink).filter(Boolean);
  return links.length ? `<p class="src muted"${style ? ` style="${style}"` : ""}>${L.source}${C()} ${links.join(" · ")}</p>` : "";
};
/* Candidat·e à la présidentielle, ou dirigeant·e du parti (élection sans présidentielle, candidat·e pas encore désigné·e). */
function candLine(p, E, L) {
  const lead = E.role === "leader" || !!p.candNote;
  return `${lead ? L.partyLeader : L.presCand}${C()} ${esc(p.cand)}${p.candNote ? ` <span class="cand-note">(${esc(p.candNote)})</span>` : ""}`;
}
function noteHTML(E, L) {
  const n = E.meta && E.meta.note;
  return n ? `<p class="caveat"><b>${L.noteLabel}${C()}</b> <span lang="${esc(E.baseLang)}">${esc(n)}</span></p>` : "";
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
  const opts = parts.length === 3 ? { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" } : { month: "long", year: "numeric", timeZone: "UTC" };
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
  if (isUp(id) || catFor(id)) return evsFor(id).map(evText).join(" ; ") || t().legNone;
  return t().legNone;
}
function kindLine(cat, L) { return cat ? (cat.kind === "ed" ? "✓ " + L.legReady : "ⓘ " + L.legInfo) : ""; }

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
function ranking(theme) {
  const min = theme ? 1 : 2;
  const a = answeredIn(theme) || 1;
  return ed().parties.map(p => {
    const r = score(p.id, theme);
    return { p, ...r, ok: r.k >= min, partial: r.k / a < 0.5 };
  }).sort((x, y) => (x.ok !== y.ok) ? (x.ok ? -1 : 1) : ((y.s ?? -1) - (x.s ?? -1)));
}
function answeredCount() { return Object.values(state.answers).filter(v => typeof v === "number").length; }
function documented(pid) { return ed().questions.filter(q => q.cells[pid]).length; }

/* ================== Rendu général ================== */
function renderChrome() {
  const L = t();
  document.documentElement.lang = state.ui;
  document.documentElement.dir = (langOf(state.ui) || {}).rtl ? "rtl" : "ltr";
  $("protoTag").textContent = L.proto;
  const list = state.country && DATA[state.country] ? ed().langs : LANGS.map(l => ({ code: l.code, label: l.code.toUpperCase(), name: l.name, ready: true }));
  $("langs").innerHTML = list.map(l => `<button type="button" data-lang="${l.code}" aria-pressed="${state.ui === l.code}" ${l.ready ? "" : "disabled"} title="${l.name}${l.ready ? "" : " · " + L.soonLang}" lang="${l.code}">${l.label}</button>`).join("");
  $("langs").setAttribute("aria-label", L.langLabel);
  $("footer").innerHTML = `<span>${L.footer1}</span><span>${L.footer2}</span>`;
}
function renderSteps(active) {
  const el = $("steps");
  if (active == null) { el.hidden = true; return; }
  el.hidden = false;
  el.innerHTML = t().steps.map((s, k) => `<li class="${k < active ? "done" : k === active ? "on" : ""}"${k === active ? ' aria-current="step"' : ""}><span class="n">${k < active ? "✓" : k + 1}</span>${s}</li>`).join("");
}
function show(html, step, cls, keepScroll) {
  $("app").innerHTML = `<section class="${cls || "screen"}">${html}</section>`;
  renderChrome();
  renderSteps(step);
  if (!keepScroll) window.scrollTo({ top: 0 });
}
function rerender() {
  const y = window.scrollY;
  const v = state.view;
  if (v === "map") viewMap(true);
  else if (v === "info") viewInfo(state.place, true);
  else if (v === "loading") viewLoading(true);
  else if (v === "loaderror") viewLoadError(true);
  else if (v === "edinfo") viewEdInfo(true);
  else if (v === "start") viewStart(true);
  else if (v === "question") viewQuestion();
  else if (v === "checkpoint") viewCheckpoint();
  else if (v === "results") viewResults();
  window.scrollTo({ top: y });
}

/* ================== Carte ================== */
const INFO_MARK = (x, y, r) => `<circle class="ring" cx="${x}" cy="${y}" r="${r}"></circle><path class="stem" d="M${x} ${y - r * .1}v${r * .55}"></path><circle class="dot" cx="${x}" cy="${y - r * .5}" r="${r * .17}"></circle>`;
function mapSVG() {
  const L = t();
  const ids = Object.keys(MAP.c);
  const aria = id => {
    const k = kindLine(catFor(id), L);
    return esc(`${cname(id)} · ${statusLine(id)}${k ? " · " + k.slice(2) : ""}`);
  };
  const paths = ids.map(id => {
    const d = MAP.c[id];
    if (id === "732") return `<path class="disp" d="${d}"><title>${esc(cname("732"))} · ${esc(L.legDisputed)}</title></path>`;
    return `<path class="ctry ${isUp(id) ? "up" : "none"}" data-place="${id}" d="${d}" tabindex="0" role="button" aria-label="${aria(id)}"></path>`;
  }).join("");
  const isl = Object.entries(MAP.isl).map(([id, [x, y]]) => {
    return `<circle class="isl-hit" data-place="${id}" cx="${x}" cy="${y}" r="22" aria-hidden="true"></circle><circle class="isl ${isUp(id) ? "up" : "none"}" data-place="${id}" cx="${x}" cy="${y}" r="9" tabindex="0" role="button" aria-label="${aria(id)}"></circle>`;
  }).join("");
  const pins = Object.values(CATALOG).filter(c => c.a3 && AFRICA[c.a3] && (MAP.isl[c.a3] || MAP.cent[c.a3])).map(c => {
    const [x, y] = MAP.isl[c.a3] || MAP.cent[c.a3];
    if (c.kind === "info") return `<g class="pin-info">${INFO_MARK(x, y, 9)}</g>`;
    return `<circle class="pin" cx="${x}" cy="${y}" r="11"></circle><path class="pin-check" d="M${x - 5} ${y}l3.5 3.5L${x + 6} ${y - 5}"></path>`;
  }).join("");
  return `<svg viewBox="${MAP.vb.join(" ")}" role="group" aria-label="${esc(L.mapAria)}" dir="ltr">
    <defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="var(--none)"></rect><rect width="1.6" height="6" fill="var(--none-hatch)"></rect></pattern></defs>
    <path class="nb" d="${MAP.nb}"></path>${paths}${isl}${pins}
  </svg><div class="tip" id="tip" hidden></div>`;
}
function countryList(filter) {
  const L = t();
  const f = (filter || "").trim().toLowerCase();
  const ids = Object.keys(AFRICA).filter(id => !f || cname(id).toLowerCase().includes(f) || AFRICA[id].fr.toLowerCase().includes(f) || AFRICA[id].en.toLowerCase().includes(f));
  const sort = arr => arr.sort((a, b) => cname(a).localeCompare(cname(b), locale()));
  const up = sort(ids.filter(isUp)), no = sort(ids.filter(id => !isUp(id)));
  const mark = id => {
    const cat = catFor(id);
    if (!cat) return "";
    return cat.kind === "ed" ? ` <span aria-hidden="true">✓</span><span class="sr">${esc(L.legReady)}</span>` : ` <span aria-hidden="true">ⓘ</span><span class="sr">${esc(L.legInfo)}</span>`;
  };
  const item = id => `<li><button type="button" class="cbtn" data-place="${id}"><span class="dot ${isUp(id) ? "up" : "none"}" aria-hidden="true"></span><span><span class="cn2">${esc(cname(id))}${mark(id)}</span><span class="cs2">${esc(isUp(id) || catFor(id) ? statusLine(id) : L.legNone)}</span></span></button></li>`;
  return `${up.length ? `<div class="clist-group"><h3>${L.legUp} · ${L.nCountries(up.length)}</h3><ul class="clist2">${up.map(item).join("")}</ul></div>` : ""}
    ${no.length ? `<div class="clist-group"><h3>${L.legNone} · ${L.nCountries(no.length)}</h3><ul class="clist2">${no.map(item).join("")}</ul></div>` : ""}`;
}
function viewMap(keep) {
  state.view = "map"; state.country = null; state.place = null;
  const L = t();
  const nUp = Object.keys(AFRICA).filter(isUp).length, nNo = Object.keys(AFRICA).length - nUp;
  const inAfrica = Object.values(CATALOG).filter(c => c.a3 && AFRICA[c.a3]);
  const nReady = inAfrica.filter(c => c.kind === "ed").length, nInfo = inAfrica.filter(c => c.kind === "info").length;
  show(`
    <div class="map-intro">
      <p class="kicker">${L.heroKicker}</p>
      <h1 class="map-title">${L.mapTitle}</h1>
      <p class="lead">${L.mapLead}</p>
    </div>
    <div class="map-card">
      <div class="map-wrap" id="mapWrap">${mapSVG()}</div>
      <p class="map-hint">${L.mapHint}</p>
    </div>
    <div class="map-side">
      <ul class="legend">
        <li><span class="sw up" aria-hidden="true"></span><span>${L.legUp}</span><span class="cnt">${nUp}</span></li>
        <li><span class="sw none" aria-hidden="true"></span><span>${L.legNone}</span><span class="cnt">${nNo}</span></li>
        <li><span class="sw ready" aria-hidden="true"></span><span>${L.legReady}</span><span class="cnt">${nReady}</span></li>
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
function bindMap() {
  const wrap = $("mapWrap"), tip = $("tip");
  if (!wrap) return;
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
  wrap.addEventListener("pointermove", e => {
    const el = e.target.closest("[data-place]");
    if (!el || e.pointerType === "touch") { tip.hidden = true; return; }
    showTip(el, e.clientX, e.clientY);
  });
  wrap.addEventListener("pointerleave", () => { tip.hidden = true; });
  wrap.addEventListener("focusin", e => {
    const el = e.target.closest("[data-place]");
    if (!el) return;
    const b = el.getBoundingClientRect();
    showTip(el, b.left + b.width / 2, b.top + b.height / 2);
  });
  wrap.addEventListener("focusout", () => { tip.hidden = true; });
  wrap.addEventListener("keydown", e => {
    const el = e.target.closest("[data-place]");
    if (el && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); openLang(el.dataset.place); }
  });
  const s = $("csearch");
  if (s) s.addEventListener("input", () => { $("clist").innerHTML = countryList(s.value); });
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
    return `<button type="button" class="lang-btn${l.code === state.ui && !off ? " cur" : ""}" data-pick="${l.code}" lang="${l.code}" dir="${l.rtl ? "rtl" : "ltr"}"${off ? " disabled" : ""}><span><span>${l.name}</span>${off ? `<span class="lnote" lang="${state.ui}" dir="${uiDir}">${esc(note)}</span>` : ""}</span><span class="lc">${l.code.toUpperCase()}</span></button>`;
  };
  $("langBody").innerHTML = `
    <div><p class="eyebrow">${esc(cname(id))}</p><h2 id="langTitle">${L.chooseLang}</h2><p class="st">${esc(statusLine(id))}</p>${cat ? `<p class="st">${esc(kindLine(cat, L))}</p>` : ""}</div>
    <div class="lang-grid"><h3>${L.langCountry}</h3>${mine.map(btn).join("")}</div>
    <div class="lang-grid"><h3>${L.langOther}</h3>${other.map(btn).join("")}</div>
    <div><button class="btn btn-ghost" type="button" id="langCancel">${L.cancel}</button></div>`;
  const dlg = $("langDlg");
  if (typeof dlg.showModal === "function") { if (!dlg.open) dlg.showModal(); } else dlg.setAttribute("open", "");
  const first = $("langBody").querySelector(".lang-btn.cur") || $("langBody").querySelector(".lang-btn:not(:disabled)");
  if (first) first.focus();
}
function closeLang() { const d = $("langDlg"); if (d.open) { if (typeof d.close === "function") d.close(); else d.removeAttribute("open"); } }
function pickLang(code) {
  const id = state.pending;
  closeLang();
  state.ui = code;
  if (A3CC[id]) { openEdition(A3CC[id]); return; }
  viewInfo(id);
}

/* ================== Chargement d'une édition ================== */
let loadSeq = 0;
function openEdition(cc) {
  if (!CATALOG[cc]) return;
  closeFiche();
  const seq = ++loadSeq;
  state.loadCc = cc;
  const ready = () => {
    if (seq !== loadSeq) return;
    const D = DATA[cc];
    state.country = cc; state.place = null;
    if (!D.langs.includes(state.ui)) state.ui = D.lang;
    resetAnswers(); state.priorities = [];
    if (D.kind === "info") viewEdInfo(); else viewStart();
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
  const lines = [];
  if (up) evsFor(id).forEach(ev => lines.push(`<li><span class="dot up" aria-hidden="true"></span><span>${esc(evText(ev))}</span></li>`));
  else {
    lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.legNone)}</span></li>`);
    if (c.note) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.notes[c.note])}</span></li>`);
    if (c.recent) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.recent(fmtDate(c.recent)))}</span></li>`);
    if (c.next) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.nextKnown)}${C()} ${esc(evText(c.next))}</span></li>`);
  }
  const cat = catFor(id);
  const s = (cat && cat.evSrc) || SRC_AF[c.src];
  show(`
    <div class="strip">
      <span><b>${esc(name)}</b><br><span class="sd">${esc(up ? L.upcoming : L.legNone)}</span></span>
      <button class="link" type="button" data-go="home">${L.changeCountry}</button>
    </div>
    <div class="block">
      <h1 class="big-title">${esc(up ? L.prepTitle(name) : L.noneTitle(name))}</h1>
    </div>
    <ul class="ev-list">${lines.join("")}</ul>
    ${s ? `<p class="src muted">${L.source}${C()} ${srcA(s)}</p>` : ""}
    ${up ? `<p class="lead">${L.prepText}</p>` : ""}
    <div class="actions">
      ${CATALOG.ng ? `<button class="btn btn-primary" type="button" data-go="nigeria">${L.tryNigeria}</button>` : ""}
      <button class="btn btn-ghost" type="button" data-go="home">${L.backMap}</button>
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
      <span><b>${esc(name)} · ${esc(E.strip)}</b><br><span class="sd">${esc(E.stripDate)}</span></span>
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
      <ol class="src-list">${all.map(id => { const s = E.src[id]; return `<li><a href="${esc(s.u)}" target="_blank" rel="noopener">${esc(s.t)}</a> · ${esc(s.o)}, ${esc(s.d)}</li>`; }).join("")}</ol>
      ${E.lang !== E.baseLang ? `<p class="caveat">${L.mTransl}</p>` : ""}
    </section>
    <div class="actions">
      ${CATALOG.ng && E.cc !== "ng" ? `<button class="btn btn-primary" type="button" data-go="nigeria">${L.tryNigeria}</button>` : ""}
      <button class="btn btn-ghost" type="button" data-go="home">${L.backMap}</button>
    </div>
  `, null, "screen", keep);
}

/* ================== Départ : élection + priorités ================== */
function viewStart(keep) {
  state.view = "start";
  const E = ed(), L = t();
  const full = state.priorities.length >= 3;
  const n = state.priorities.length;
  const openDetails = [...document.querySelectorAll(".about details")].map(d => d.open);
  show(`
    <div class="strip">
      <span><b>${esc(edName(E))} · ${esc(E.strip)}</b><br><span class="sd">${esc(E.stripDate)}</span></span>
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
      <button class="btn btn-primary" type="button" data-go="startq" ${n ? "" : "disabled"}>${L.startPrio}</button>
      <span class="mono muted" style="font-size:.85rem" aria-live="polite">${L.chosen(n)}</span>
    </div>
  `, 0, "screen", keep);
  if (keep) document.querySelectorAll(".about details").forEach((d, i) => { d.open = !!openDetails[i]; });
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
let advanceTimer = null;
function viewQuestion() {
  state.view = "question";
  const E = ed(), L = t();
  const qi = state.order[state.i];
  const q = E.questions[qi];
  const th = E.themes.find(x => x.id === q.theme);
  const inPrio = state.i < state.nPrio;
  const blockN = inPrio ? state.nPrio : state.order.length - state.nPrio;
  const blockI = inPrio ? state.i + 1 : state.i - state.nPrio + 1;
  const v = state.answers[qi];
  const allPrioSeen = state.order.slice(0, state.nPrio).every(x => state.answers[x] !== undefined);
  const progress = state.order.map((x, k) => {
    const a = state.answers[x];
    const cls = [
      k > 0 && E.questions[state.order[k - 1]].theme !== E.questions[x].theme ? "theme-start" : "",
      k < state.nPrio ? "prio" : "",
      typeof a === "number" ? "done" : a === null ? "skipped" : "",
      k === state.i ? "current" : ""
    ].join(" ");
    return `<button type="button" class="${cls}" data-goto="${k}" aria-label="${L.qOf(k + 1, state.order.length)}"${k === state.i ? ' aria-current="step"' : ""}></button>`;
  }).join("");
  show(`
    <nav class="progress" aria-label="${L.steps[1]}">${progress}</nav>
    <div class="q-meta">
      <span><span class="q-theme">${esc(th.name)}</span> <span class="chip ${inPrio ? "" : "grey"}">${inPrio ? L.blockPrio : L.blockMore}</span></span>
      <span class="mono muted">${L.qOf(nn(blockI), nn(blockN))}</span>
    </div>
    <p class="q-min">${L.ministries}${C()} ${esc(th.min)}</p>
    <div class="slip">
      <h2>${esc(q.text)}</h2>
      <details><summary>${L.background}</summary><p>${esc(q.ctx)}</p></details>
    </div>
    <fieldset class="answers"><legend class="sr">${L.yourAnswer}</legend>
      ${[2, 1, 0, -1, -2].map(val => `<button type="button" class="ans" data-val="${val}" aria-pressed="${v === val}"><span class="box" aria-hidden="true">${CHECK}</span><span>${L.ans[val]}</span></button>`).join("")}
    </fieldset>
    <label class="double"><input type="checkbox" id="qDouble" ${state.double[qi] ? "checked" : ""}> ${L.double}</label>
    <div class="q-nav">
      <button class="btn btn-ghost" type="button" data-go="prev" ${state.i === 0 ? "disabled" : ""}>${L.prev}</button>
      <div class="actions">
        <button class="btn btn-ghost" type="button" data-val="skip">${v === null ? L.skipped : L.skip}</button>
        ${allPrioSeen ? `<button class="btn btn-primary" type="button" data-go="results">${L.seeResults}</button>` : ""}
      </div>
    </div>
  `, 1);
}
function answer(val) {
  const qi = state.order[state.i];
  state.answers[qi] = val;
  document.querySelectorAll(".ans").forEach(b => b.setAttribute("aria-pressed", String(+b.dataset.val === val)));
  clearTimeout(advanceTimer);
  advanceTimer = setTimeout(nextQ, 240);
}
function nextQ() {
  const last = state.order.length - 1;
  if (state.i === state.nPrio - 1 && state.nPrio < state.order.length && !state.order.slice(state.nPrio).some(x => state.answers[x] !== undefined)) {
    viewCheckpoint(); return;
  }
  if (state.i < last) { state.i++; viewQuestion(); }
  else viewResults();
}
function viewCheckpoint() {
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
  `, 1);
}

/* ================== Résultats ================== */
function viewResults() {
  state.view = "results";
  clearTimeout(advanceTimer);
  const E = ed(), L = t();
  const a = answeredCount();
  const rank = ranking();
  const eligible = rank.filter(r => r.ok);
  let title, summary;
  if (!eligible.length) {
    title = L.resNone; summary = L.resNoneText;
  } else {
    const top = Math.round(eligible[0].s * 100);
    const tied = eligible.filter(r => Math.round(r.s * 100) === top);
    title = tied.length > 1 ? L.resTie(tied.map(r => pname(r.p)).join(", ")) : L.resClosest(`${pname(eligible[0].p)} (${eligible[0].p.sigle})`);
    const pr = state.priorities.map(id => E.themes.find(x => x.id === id).name).join(", ") || L.none;
    summary = L.resSummary(a, E.questions.length, pr);
  }
  show(`
    <div class="res-head">
      <p class="eyebrow">${L.resEyebrow} · ${esc(edName(E))}</p>
      <h1 class="big-title">${esc(title)}</h1>
      <p>${esc(summary)}</p>
    </div>
    <div class="tabs" role="tablist">${L.tabs.map((x, k) => `<button class="tab" role="tab" id="tab${k}" aria-controls="pan${k}" aria-selected="${state.tab === k}" type="button" data-tab="${k}">${x}</button>`).join("")}</div>
    <div class="panel" role="tabpanel" id="pan0" aria-labelledby="tab0" ${state.tab === 0 ? "" : "hidden"}>${panelRanking(rank, a)}</div>
    <div class="panel" role="tabpanel" id="pan1" aria-labelledby="tab1" ${state.tab === 1 ? "" : "hidden"}>${panelThemes()}</div>
    <div class="panel" role="tabpanel" id="pan2" aria-labelledby="tab2" ${state.tab === 2 ? "" : "hidden"}>${panelQuestions()}</div>
    <div class="panel" role="tabpanel" id="pan3" aria-labelledby="tab3" ${state.tab === 3 ? "" : "hidden"}>${panelMethod()}</div>
    <div class="actions">
      <button class="btn btn-ghost" type="button" data-go="edit">${L.actEdit}</button>
      <button class="btn btn-ghost" type="button" data-go="restart">${L.actRestart}</button>
      <button class="btn btn-ghost" type="button" data-go="home">${L.changeCountry}</button>
    </div>
  `, 2);
}
function panelRanking(rank, a) {
  const E = ed(), L = t();
  let pos = 0;
  return `<ol class="rank">${rank.map(r => {
    const has = r.s !== null;
    if (r.ok) pos++;
    return `<li class="${r.ok ? (pos === 1 ? "top" : "") : "out"}">
      <span class="pos">${r.ok ? pos : "–"}</span>
      ${badge(r.p)}
      <div class="rank-main">
        <div class="rank-head"><b>${hname(r.p)}</b><span class="pct">${has && r.ok ? pctTxt(r.s) : "–"}</span></div>
        <div class="bar" style="--pc:var(${pvar(r.p.id)}, var(--accent))" role="img" aria-label="${has && r.ok ? Math.round(r.s * 100) + " " + L.pctWord : L.notRanked}"><span style="width:${has && r.ok ? (r.s * 100).toFixed(1) : 0}%"></span></div>
        <div class="rank-sub"><span>${candLine(r.p, E, L)}</span><span>${r.ok ? L.compared(r.k, a) : L.notRanked}</span>${r.ok && r.partial ? `<span class="chip warn">${L.partial}</span>` : ""}${r.p.chip ? `<span class="chip grey">${esc(r.p.chip)}</span>` : ""}<button class="link" type="button" data-fiche="${esc(r.p.id)}">${L.seeProfile}</button></div>
      </div>
    </li>`;
  }).join("")}</ol>
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
    const head = `<div class="tc-head"><h3>${esc(th.name)}</h3>${on ? `<span class="chip">${L.prio}</span>` : ""}</div>`;
    if (!answered) {
      const first = state.order.indexOf(qIdx[0]);
      return `<article class="theme-card${on ? " prio-on" : ""}">${head}<p class="skipped-note">${L.themeNotAnswered}</p><div><button class="link" type="button" data-goto="${first}">${L.answerTheme}</button></div></article>`;
    }
    const r = ranking(th.id);
    const ok = r.filter(x => x.ok);
    let phrase;
    if (!ok.length) phrase = L.themeNoData;
    else {
      const top = Math.round(ok[0].s * 100);
      const tied = ok.filter(x => Math.round(x.s * 100) === top);
      phrase = tied.length > 1
        ? L.themeTie(esc(th.name), tied.map(x => `<b>${hname(x.p)}</b>`).join(", "), pctTxt(ok[0].s))
        : L.themeVerdict(esc(th.name), esc(`${pname(ok[0].p)} (${ok[0].p.sigle})`), pctTxt(ok[0].s), ok[0].k);
    }
    return `<article class="theme-card${on ? " prio-on" : ""}">${head}
      <p class="verdict-line">${phrase}</p>
      <div class="mini">${r.map(x => x.ok
        ? `<div class="mini-row">${badge(x.p, "sm")}<span class="name">${hname(x.p)}</span><div class="bar" style="--pc:var(${pvar(x.p.id)}, var(--accent))"><span style="width:${(x.s * 100).toFixed(1)}%"></span></div><span class="pct">${pctTxt(x.s)}</span></div>`
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
    <h3>${L.mFormulaTitle}</h3>
    <p>${L.mFormula1}</p>
    <p class="formula" dir="ltr">${L.formula}</p>
    <p>${L.mFormula2}</p>
    <h3>${L.mCodingTitle}</h3>
    <ul>${coding.map(x => `<li>${x}</li>`).join("")}${E.lang !== E.baseLang ? `<li class="transl">${L.mTransl}</li>` : ""}</ul>
    <h3>${L.mCovTitle}</h3>
    <div class="tbl-wrap"><table class="cov"><thead><tr><th>${L.mCovParty}</th><th style="text-align:end">${L.mCovN}</th></tr></thead><tbody>
      ${E.parties.map(p => ({ p, n: documented(p.id) })).sort((x, y) => y.n - x.n).map(({ p, n }) => `<tr><td>${esc(label(p))}</td><td class="num">${n} / ${E.questions.length}</td></tr>`).join("")}
    </tbody></table></div>
    <h3>${L.mNotTitle}</h3>
    <ul>${L.mNot.map(x => `<li>${x}</li>`).join("")}</ul>
    <h3>${L.mSrcTitle}</h3>
    <ol class="src-list">${used.map(id => { const s = E.src[id]; return `<li><a href="${esc(s.u)}" target="_blank" rel="noopener">${esc(s.t)}</a> · ${esc(s.o)}, ${esc(s.d)}</li>`; }).join("")}</ol>
  </div>`;
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

/* ================== Navigation ================== */
function resetAnswers() { state.answers = {}; state.double = {}; state.i = 0; state.tab = 0; state.order = []; }
function go(where) {
  clearTimeout(advanceTimer);
  switch (where) {
    case "home": loadSeq++; closeFiche(); viewMap(); break;
    case "france": state.ui = "fr"; openEdition("fr"); break;
    case "nigeria": openEdition("ng"); break;
    case "retry": openEdition(state.loadCc); break;
    case "startq": buildOrder(); state.i = 0; viewQuestion(); break;
    case "prev": if (state.i > 0) { state.i--; viewQuestion(); } break;
    case "more": state.i = state.nPrio; viewQuestion(); break;
    case "results": state.tab = 0; viewResults(); break;
    case "edit": state.i = 0; viewQuestion(); break;
    case "restart": resetAnswers(); state.priorities = []; viewStart(); break;
  }
}
document.addEventListener("click", e => {
  if (e.target === $("langDlg")) return closeLang();
  if (e.target === $("fiche")) return closeFiche();
  const el = e.target.closest("[data-pick],[data-place],[data-lang],[data-go],[data-prio],[data-val],[data-goto],[data-tab],[data-fiche],#ficheClose,#langCancel,#brand");
  if (!el) return;
  if (el.id === "ficheClose") return closeFiche();
  if (el.id === "langCancel") return closeLang();
  if (el.id === "brand") return go("home");
  if (el.dataset.pick) return pickLang(el.dataset.pick);
  if (el.dataset.place) return openLang(el.dataset.place);
  if (el.dataset.lang) { state.ui = el.dataset.lang; return rerender(); }
  if (el.dataset.go) return go(el.dataset.go);
  if (el.dataset.fiche) return openFiche(el.dataset.fiche);
  if (el.dataset.prio) {
    const id = el.dataset.prio;
    const k = state.priorities.indexOf(id);
    if (k >= 0) state.priorities.splice(k, 1); else if (state.priorities.length < 3) state.priorities.push(id);
    const y = window.scrollY;
    viewStart(true);
    window.scrollTo({ top: y });
    const again = document.querySelector(`[data-prio="${CSS.escape(id)}"]`); if (again) again.focus({ preventScroll: true });
    return;
  }
  if (el.dataset.val) return answer(el.dataset.val === "skip" ? null : +el.dataset.val);
  if (el.dataset.goto) {
    closeFiche();
    if (!state.order.length) buildOrder();
    state.i = +el.dataset.goto; return viewQuestion();
  }
  if (el.dataset.tab) {
    state.tab = +el.dataset.tab;
    document.querySelectorAll('[role="tab"]').forEach((b, k) => b.setAttribute("aria-selected", String(k === state.tab)));
    document.querySelectorAll('[role="tabpanel"]').forEach((p, k) => { p.hidden = k !== state.tab; });
  }
});
document.addEventListener("change", e => {
  if (e.target.id === "qDouble") state.double[state.order[state.i]] = e.target.checked;
});
document.addEventListener("keydown", e => {
  if (!e.target.closest || !e.target.closest('[role="tablist"]')) return;
  if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const k = tabs.indexOf(document.activeElement);
  if (k < 0) return;
  const n = (k + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length;
  tabs[n].focus(); tabs[n].click();
});

viewMap();
</script>
