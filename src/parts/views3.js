
NG.i18n = NG_I18N;
NG.langs = LANGS.map(l => ({ code: l.code, label: l.code.toUpperCase(), name: l.name, ready: true }));
FR.langs = LANGS.map(l => ({ code: l.code, label: l.code.toUpperCase(), name: l.name, ready: l.code === "fr" }));
const EDITIONS = { fr: FR, ng: NG };
const SRC = Object.assign({}, SRC_NG, SRC_FR, SRC_AF);

/* ================== État ================== */
const state = { ui: "fr", country: null, place: null, view: "map", priorities: [], order: [], nPrio: 0, i: 0, answers: {}, double: {}, tab: 0, pending: null };
const PRIOR_ALL = 3, PRIOR_THEME = 1;
const $ = id => document.getElementById(id);
const t = () => T[state.ui] || T.fr;
const edCache = {};
const ed = () => {
  const key = state.country + ":" + state.ui;
  if (!edCache[key]) edCache[key] = localizeEdition(EDITIONS[state.country], state.ui);
  return edCache[key];
};
const nn = n => String(n).padStart(2, "0");
const C = () => state.ui === "fr" ? "\u202f:" : ":";
const pctTxt = s => Math.round(s * 100) + '<span class="pu"> %</span>';
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const label = p => `${p.sigle} · ${p.nom}`;
const ISO = [String.fromCharCode(0x2068), String.fromCharCode(0x2069)];
const pname = p => ISO[0] + p.nom + ISO[1];
const candLine = (p, L) => `${L.presCand}${C()} ${p.cand}`;
const locale = () => (LANGS.find(l => l.code === state.ui) || LANGS[1]).locale;

function badge(p, size) {
  return `<span class="badge ${size || ""}" style="--pc:var(--c-${p.id})" aria-hidden="true">${p.sigle}</span>`;
}
function srcLink(id) {
  const s = SRC[id];
  if (!s) return "";
  return `<a href="${s.u}" target="_blank" rel="noopener">${esc(s.o)}, ${esc(s.d)}</a>`;
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
    try { n = new Intl.DisplayNames([(LANGS.find(l => l.code === lang) || {}).locale || lang], { type: "region" }).of(c.a2); } catch (e) { n = null; }
    if (!n || n === c.a2) n = c.en;
  }
  return (namesCache[key] = n);
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
  const w = ev.q === "range" ? L.when.range(fmtDate(ev.d), fmtDate(ev.d2)) : L.when[ev.q](fmtDate(ev.d));
  return `${ty} · ${w}`;
}
function statusLine(id) {
  const c = AFRICA[id];
  if (!c) return t().legDisputed;
  if (c.up) return c.ev.map(evText).join(" ; ");
  return t().legNone;
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
  document.documentElement.dir = (LANGS.find(l => l.code === state.ui) || {}).rtl ? "rtl" : "ltr";
  $("protoTag").textContent = L.proto;
  const list = state.country ? ed().langs : LANGS.map(l => ({ code: l.code, label: l.code.toUpperCase(), name: l.name, ready: true }));
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
  else if (v === "start") viewStart(true);
  else if (v === "question") viewQuestion();
  else if (v === "checkpoint") viewCheckpoint();
  else if (v === "results") viewResults();
  window.scrollTo({ top: y });
}

/* ================== Carte ================== */
function mapSVG() {
  const L = t();
  const ids = Object.keys(MAP.c);
  const paths = ids.map(id => {
    const d = MAP.c[id];
    if (id === "732") return `<path class="disp" d="${d}"><title>${esc(cname("732"))} · ${esc(L.legDisputed)}</title></path>`;
    const c = AFRICA[id];
    return `<path class="ctry ${c.up ? "up" : "none"}" data-place="${id}" d="${d}" tabindex="0" role="button" aria-label="${esc(cname(id))} · ${esc(statusLine(id))}"></path>`;
  }).join("");
  const isl = Object.entries(MAP.isl).map(([id, [x, y]]) => {
    const c = AFRICA[id];
    return `<circle class="isl-hit" data-place="${id}" cx="${x}" cy="${y}" r="22" aria-hidden="true"></circle><circle class="isl ${c.up ? "up" : "none"}" data-place="${id}" cx="${x}" cy="${y}" r="9" tabindex="0" role="button" aria-label="${esc(cname(id))} · ${esc(statusLine(id))}"></circle>`;
  }).join("");
  const pins = Object.entries(AFRICA).filter(([, c]) => c.ed).map(([id]) => {
    const [x, y] = MAP.cent[id];
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
  const up = sort(ids.filter(id => AFRICA[id].up)), no = sort(ids.filter(id => !AFRICA[id].up));
  const item = id => `<li><button type="button" class="cbtn" data-place="${id}"><span class="dot ${AFRICA[id].up ? "up" : "none"}" aria-hidden="true"></span><span><span class="cn2">${esc(cname(id))}${AFRICA[id].ed ? " ✓" : ""}</span><span class="cs2">${esc(AFRICA[id].up ? statusLine(id) : L.legNone)}</span></span></button></li>`;
  return `${up.length ? `<div class="clist-group"><h3>${L.legUp} · ${L.nCountries(up.length)}</h3><ul class="clist2">${up.map(item).join("")}</ul></div>` : ""}
    ${no.length ? `<div class="clist-group"><h3>${L.legNone} · ${L.nCountries(no.length)}</h3><ul class="clist2">${no.map(item).join("")}</ul></div>` : ""}`;
}
function viewMap(keep) {
  state.view = "map"; state.country = null; state.place = null;
  const L = t();
  const nUp = Object.values(AFRICA).filter(c => c.up).length, nNo = Object.values(AFRICA).length - nUp;
  const nReady = Object.values(AFRICA).filter(c => c.ed).length;
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
        <li><span class="sw disp" aria-hidden="true"></span><span>${L.legDisputed}</span><span class="cnt">1</span></li>
      </ul>
      <details class="clist-wrap" id="listBox">
        <summary>${L.listToggle}</summary>
        <label class="sr" for="csearch">${L.searchLabel}</label>
        <input id="csearch" type="search" placeholder="${esc(L.searchLabel)}" autocomplete="off">
        <div id="clist">${countryList("")}</div>
      </details>
      <div class="outside"><p class="eyebrow">${L.outsideAfrica}</p><button class="link" type="button" data-go="france">${L.protoFrance}</button></div>
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
    tip.innerHTML = `<b>${esc(cname(id))}</b>${esc(statusLine(id))}`;
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
  const mine = LANGS.filter(l => c.langs.includes(l.code)).sort((a, b) => c.langs.indexOf(a.code) - c.langs.indexOf(b.code));
  const other = LANGS.filter(l => !c.langs.includes(l.code));
  const btn = l => `<button type="button" class="lang-btn${l.code === state.ui ? " cur" : ""}" data-pick="${l.code}" lang="${l.code}" dir="${l.rtl ? "rtl" : "ltr"}"><span>${l.name}</span><span class="lc">${l.code.toUpperCase()}</span></button>`;
  $("langBody").innerHTML = `
    <div><p class="eyebrow">${esc(cname(id))}</p><h2 id="langTitle">${L.chooseLang}</h2><p class="st">${esc(statusLine(id))}</p></div>
    <div class="lang-grid"><h3>${L.langCountry}</h3>${mine.map(btn).join("")}</div>
    <div class="lang-grid"><h3>${L.langOther}</h3>${other.map(btn).join("")}</div>
    <div><button class="btn btn-ghost" type="button" id="langCancel">${L.cancel}</button></div>`;
  const dlg = $("langDlg");
  if (typeof dlg.showModal === "function") { if (!dlg.open) dlg.showModal(); } else dlg.setAttribute("open", "");
  const first = $("langBody").querySelector(".lang-btn");
  if (first) first.focus();
}
function closeLang() { const d = $("langDlg"); if (d.open) { if (typeof d.close === "function") d.close(); else d.removeAttribute("open"); } }
function pickLang(code) {
  const id = state.pending;
  closeLang();
  state.ui = code;
  const c = AFRICA[id];
  if (c && c.ed) { startEdition(c.ed); return; }
  viewInfo(id);
}
function startEdition(edId) {
  state.country = edId;
  if (!ed().langs.find(l => l.code === state.ui && l.ready)) state.ui = EDITIONS[edId].lang;
  resetAnswers(); state.priorities = [];
  viewStart();
}

/* ================== Pays sans questionnaire ================== */
function viewInfo(id, keep) {
  state.view = "info"; state.place = id; state.country = null;
  const L = t(), c = AFRICA[id];
  const name = cname(id);
  const lines = [];
  if (c.up) c.ev.forEach(ev => lines.push(`<li><span class="dot up" aria-hidden="true"></span><span>${esc(evText(ev))}</span></li>`));
  else {
    lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.legNone)}</span></li>`);
    if (c.note) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.notes[c.note])}</span></li>`);
    if (c.recent) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.recent(fmtDate(c.recent)))}</span></li>`);
    if (c.next) lines.push(`<li><span class="dot none" aria-hidden="true"></span><span>${esc(L.nextKnown)}${C()} ${esc(evText(c.next))}</span></li>`);
  }
  show(`
    <div class="strip">
      <span><b>${esc(name)}</b><br><span class="sd">${esc(c.up ? L.upcoming : L.legNone)}</span></span>
      <button class="link" type="button" data-go="home">${L.changeCountry}</button>
    </div>
    <div class="block">
      <h1 class="big-title">${esc(c.up ? L.prepTitle(name) : L.noneTitle(name))}</h1>
    </div>
    <ul class="ev-list">${lines.join("")}</ul>
    ${c.src ? `<p class="src muted">${L.source}${C()} ${srcLink(c.src)}</p>` : ""}
    ${c.up ? `<p class="lead">${L.prepText}</p>` : ""}
    <div class="actions">
      <button class="btn btn-primary" type="button" data-go="nigeria">${L.tryNigeria}</button>
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
      <span><b>${esc(state.country === "fr" ? E.name : cname("566"))} · ${E.strip}</b><br><span class="sd">${E.stripDate}</span></span>
      <button class="link" type="button" data-go="home">${L.changeCountry}</button>
    </div>
    <div class="about">
      <details>
        <summary>${L.aboutElection}</summary>
        <dl class="facts">${E.facts.map(([a, b]) => `<div><dt>${a}</dt><dd>${b}</dd></div>`).join("")}</dl>
        <ul class="sys">${E.system.map(([a, b]) => `<li><b>${a}</b><span>${b}</span></li>`).join("")}</ul>
        <p class="src muted" style="margin-top:8px">${L.source}${C()} ${[...E.factsSrc, ...(E.systemSrc || [])].filter((v, i, a) => a.indexOf(v) === i).map(srcLink).join(" · ")}</p>
      </details>
      <details>
        <summary>${L.whoCompared(E.parties.length)}</summary>
        <p class="basis">${L.partyBasis}</p>
        <ul class="party-list">${E.parties.map(p => `
          <li><button class="party-btn" type="button" data-fiche="${p.id}">
            ${badge(p)}
            <span class="pb-text"><span class="pb-name">${pname(p)} ${p.chip ? `<span class="chip warn">${p.chip}</span>` : ""}</span><span class="pb-sub">${candLine(p, L)}</span></span>
          </button></li>`).join("")}
        </ul>
        <p class="caveat" style="margin-top:10px">${E.status}</p>
        <details style="margin-top:10px"><summary>${L.alsoRunning}</summary><ul class="others">${E.others.map(o => `<li>${o}</li>`).join("")}</ul><p class="src muted" style="margin-top:6px">${L.source}${C()} ${srcLink(E.othersSrc)}</p></details>
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
      return `<button type="button" class="theme-opt" data-prio="${th.id}" aria-pressed="${on}" ${!on && full ? "disabled" : ""}>
        <span class="box" aria-hidden="true">${CHECK}</span>
        <span class="tn">${th.name} ${on ? `<span class="rank-badge">· ${L.prioN(rank)}</span>` : ""}</span>
        <span class="tm">${th.min}</span>
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
      <span><span class="q-theme">${th.name}</span> <span class="chip ${inPrio ? "" : "grey"}">${inPrio ? L.blockPrio : L.blockMore}</span></span>
      <span class="mono muted">${L.qOf(nn(blockI), nn(blockN))}</span>
    </div>
    <p class="q-min">${L.ministries}${C()} ${th.min}</p>
    <div class="slip">
      <h2>${q.text}</h2>
      <details><summary>${L.background}</summary><p>${q.ctx}</p></details>
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
  const country = state.country === "fr" ? E.name : cname("566");
  show(`
    <div class="res-head">
      <p class="eyebrow">${L.resEyebrow} · ${esc(country)}</p>
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
  const L = t();
  let pos = 0;
  return `<ol class="rank">${rank.map(r => {
    const has = r.s !== null;
    if (r.ok) pos++;
    return `<li class="${r.ok ? (pos === 1 ? "top" : "") : "out"}">
      <span class="pos">${r.ok ? pos : "–"}</span>
      ${badge(r.p)}
      <div class="rank-main">
        <div class="rank-head"><b>${pname(r.p)}</b><span class="pct">${has && r.ok ? pctTxt(r.s) : "–"}</span></div>
        <div class="bar" style="--pc:var(--c-${r.p.id})" role="img" aria-label="${has && r.ok ? Math.round(r.s * 100) + " " + L.pctWord : L.notRanked}"><span style="width:${has && r.ok ? (r.s * 100).toFixed(1) : 0}%"></span></div>
        <div class="rank-sub"><span>${candLine(r.p, L)}</span><span>${r.ok ? L.compared(r.k, a) : L.notRanked}</span>${r.ok && r.partial ? `<span class="chip warn">${L.partial}</span>` : ""}${r.p.chip ? `<span class="chip grey">${r.p.chip}</span>` : ""}<button class="link" type="button" data-fiche="${r.p.id}">${L.seeProfile}</button></div>
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
    const head = `<div class="tc-head"><h3>${th.name}</h3>${on ? `<span class="chip">${L.prio}</span>` : ""}</div>`;
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
        ? L.themeTie(th.name, tied.map(x => `<b>${pname(x.p)}</b>`).join(", "), pctTxt(ok[0].s))
        : L.themeVerdict(th.name, `${pname(ok[0].p)} (${ok[0].p.sigle})`, pctTxt(ok[0].s), ok[0].k);
    }
    return `<article class="theme-card${on ? " prio-on" : ""}">${head}
      <p class="verdict-line">${phrase}</p>
      <div class="mini">${r.map(x => x.ok
        ? `<div class="mini-row">${badge(x.p, "sm")}<span class="name">${pname(x.p)}</span><div class="bar" style="--pc:var(--c-${x.p.id})"><span style="width:${(x.s * 100).toFixed(1)}%"></span></div><span class="pct">${pctTxt(x.s)}</span></div>`
        : `<div class="mini-row nd">${badge(x.p, "sm")}<span class="name">${pname(x.p)}</span><span class="ndt" style="font-size:.82rem;font-style:italic">${L.notDoc}</span><span></span></div>`).join("")}
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
      <div class="qa-meta"><span class="mono">${nn(k + 1)}</span><span>${th.name}</span>${state.priorities.includes(q.theme) ? `<span class="chip">${L.prio}</span>` : ""}${state.double[qi] ? `<span class="chip grey">×2</span>` : ""}</div>
      <p class="qa-text">${q.text}</p>
      ${yours}
      <div class="scale-wrap"><div class="scale">${cols}</div></div>
      ${nd.length ? `<p class="nd-line">${L.noDocLine} ${nd.map(p => `<span class="chip grey">${p.sigle}</span>`).join("")}</p>` : ""}
      <details><summary>${L.whatTheySay}</summary>
        <ul class="why-list">${E.parties.map(p => {
          const c = q.cells[p.id];
          if (c) return `<li>${badge(p, "sm")}<div><span class="pos-label">${pname(p)} · ${L.ans[c.p]}</span> <span class="kind">· ${L.kinds[c.k]}</span><p>${c.n}</p><p class="src">${L.source}${C()} ${srcLink(c.s)}</p></div></li>`;
          const note = q.nd && q.nd[p.id];
          return `<li>${badge(p, "sm")}<div><span class="pos-label" style="font-weight:400;font-style:italic">${pname(p)} · ${L.notDoc}</span>${note ? `<p>${note}</p>` : ""}</div></li>`;
        }).join("")}</ul>
      </details>
      <div><button class="link" type="button" data-goto="${k}">${typeof v === "number" ? L.edit : L.answerIt}</button></div>
    </article>`;
  }).join("");
}
function panelMethod() {
  const E = ed(), L = t();
  const used = [...new Set([...E.factsSrc, ...(E.systemSrc || []), E.othersSrc, ...E.parties.map(p => p.tagSrc).filter(Boolean), ...E.questions.flatMap(q => Object.values(q.cells).map(c => c.s)), ...E.parties.flatMap(p => p.commit.map(c => c[1]))])].filter(id => SRC[id]);
  return `<div class="method">
    <h3>${L.mFormulaTitle}</h3>
    <p>${L.mFormula1}</p>
    <p class="formula" dir="ltr">${L.formula}</p>
    <p>${L.mFormula2}</p>
    <h3>${L.mCodingTitle}</h3>
    <ul>${L.mCoding.map(x => `<li>${x}</li>`).join("")}${state.country === "ng" ? `<li>${L.mTransl}</li>` : ""}</ul>
    <h3>${L.mCovTitle}</h3>
    <div class="tbl-wrap"><table class="cov"><thead><tr><th>${L.mCovParty}</th><th style="text-align:end">${L.mCovN}</th></tr></thead><tbody>
      ${E.parties.map(p => ({ p, n: documented(p.id) })).sort((x, y) => y.n - x.n).map(({ p, n }) => `<tr><td>${label(p)}</td><td class="num">${n} / ${E.questions.length}</td></tr>`).join("")}
    </tbody></table></div>
    <h3>${L.mNotTitle}</h3>
    <ul>${L.mNot.map(x => `<li>${x}</li>`).join("")}</ul>
    <h3>${L.mSrcTitle}</h3>
    <ol class="src-list">${used.map(id => `<li><a href="${SRC[id].u}" target="_blank" rel="noopener">${esc(SRC[id].t)}</a> · ${esc(SRC[id].o)}, ${esc(SRC[id].d)}</li>`).join("")}</ol>
  </div>`;
}

/* ================== Fiche candidat ================== */
function openFiche(pid) {
  const E = ed(), L = t();
  const p = E.parties.find(x => x.id === pid);
  const sc = answeredCount() ? score(pid) : { s: null, k: 0 };
  $("ficheBody").innerHTML = `
    <div class="fiche-head">
      ${badge(p, "lg")}
      <div><h2 id="ficheTitle">${pname(p)}</h2><p>${candLine(p, L)}${p.vp ? ` · ${L.runningMate}${C()} ${p.vp}` : ""}</p></div>
      <button class="close" type="button" id="ficheClose" aria-label="${L.ficheClose}">×</button>
    </div>
    ${p.chip ? `<p><span class="chip warn">${p.chip}</span></p>` : ""}
    <p style="font-size:.95rem">${p.tag}${p.tagSrc ? ` <span class="src muted">(${srcLink(p.tagSrc)})</span>` : ""}</p>
    ${sc.k >= 2 ? `<div class="fiche-score"><span class="pct">${pctTxt(sc.s)}</span><span>${L.ficheScore}</span></div>` : ""}
    <p class="mono muted" style="font-size:.85rem">${L.ficheDoc(documented(pid), E.questions.length)}</p>
    <section><h3>${L.ficheCommit}</h3><ul class="commit">${p.commit.map(([c, s]) => `<li><span>${c}</span><span class="src muted">${L.source}${C()} ${srcLink(s)}</span></li>`).join("")}</ul></section>
    <section><h3>${L.fichePos}</h3><ul class="pos-table">${E.questions.map(q => {
      const c = q.cells[pid];
      return `<li><span>${q.short}</span><span class="pv${c ? "" : " nd"}">${c ? L.ans[c.p] : L.notDoc}</span></li>`;
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
    case "home": closeFiche(); viewMap(); break;
    case "france": state.ui = "fr"; startEdition("fr"); break;
    case "nigeria": startEdition("ng"); break;
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
    const again = document.querySelector(`[data-prio="${id}"]`); if (again) again.focus({ preventScroll: true });
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
