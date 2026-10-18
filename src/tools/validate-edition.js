#!/usr/bin/env node
/* Validate a country edition file: node src/tools/validate-edition.js src/editions/ke.js [src/i18n/ke.js] [fr,sw] */
const fs = require("fs"), path = require("path"), vm = require("vm");
const file = process.argv[2];
if (!file) { console.error("usage: validate-edition.js <edition.js> [i18n.js]"); process.exit(2); }
const cc = path.basename(file, ".js").toLowerCase(), CC = cc.toUpperCase();
const ctx = {};
vm.createContext(ctx);
const errs = [], warns = [];
try {
  vm.runInContext(fs.readFileSync(file, "utf8") + `\n;this.__S = SRC_${CC}; this.__M = META_${CC}; this.__E = typeof ED_${CC} !== "undefined" ? ED_${CC} : null; this.__I = typeof INFO_${CC} !== "undefined" ? INFO_${CC} : null;`, ctx, { filename: file });
} catch (e) { console.error("LOAD ERROR:", e.message); process.exit(1); }
const S = ctx.__S, M = ctx.__M;
let E = ctx.__E;
const hex = c => /^#[0-9A-Fa-f]{6}$/.test(c || "");
const str = (v, where) => { if (typeof v !== "string" || !v.trim()) errs.push(`${where}: missing or empty string`); else if (/(^|[^\\])"/.test(JSON.stringify(v).slice(1, -1).replace(/\\"/g, "§"))) {} };
const srcOk = (k, where) => { if (!S[k]) errs.push(`${where}: source key “${k}” not in SRC_${CC}`); };

// Sources
for (const [k, s] of Object.entries(S)) {
  ["o", "t", "d", "u"].forEach(f => str(s[f], `SRC.${k}.${f}`));
  if (s.u && !/^https?:\/\/[^\s]+$/.test(s.u)) errs.push(`SRC.${k}.u: not a URL`);
}
// Meta
if (!M || !Array.isArray(M.ev) || !M.ev.length) errs.push("META.ev missing");
else M.ev.forEach((ev, i) => {
  if (!["general", "presidential", "legislative", "pres_leg", "referendum", "national"].includes(ev.t)) errs.push(`META.ev[${i}].t invalid`);
  if (!/^\d{4}-\d{2}(-\d{2})?$/.test(ev.d || "")) errs.push(`META.ev[${i}].d invalid`);
  if (!["exact", "month", "by", "before", "range"].includes(ev.q)) errs.push(`META.ev[${i}].q invalid`);
  if (ev.q === "range" && !/^\d{4}-\d{2}(-\d{2})?$/.test(ev.d2 || "")) errs.push(`META.ev[${i}].d2 needed for range`);
});
if (M) srcOk(M.src, "META.src");
if (!E && ctx.__I) {
  const I = ctx.__I;
  ["id", "name", "lang", "strip", "stripDate", "why"].forEach(f => str(I[f], `INFO.${f}`));
  if (I.id !== cc) errs.push(`INFO.id should be “${cc}”`);
  if (!Array.isArray(I.facts) || I.facts.length !== 3) errs.push("INFO.facts must have 3 rows");
  if (!Array.isArray(I.system) || I.system.length < 4 || I.system.length > 6) errs.push("INFO.system must have 4–6 rows");
  if (!Array.isArray(I.actors) || I.actors.length < 3 || I.actors.length > 8) errs.push("INFO.actors must have 3–8 rows");
  (I.actors || []).forEach((a, i) => { str(a[0], `actors[${i}][0]`); str(a[1], `actors[${i}][1]`); srcOk(a[2], `actors[${i}][2]`); });
  [...(I.factsSrc || []), ...(I.systemSrc || [])].forEach(k => srcOk(k, "INFO src"));
  errs.forEach(e => console.log("ERROR " + e));
  if (errs.length) { console.log(`${errs.length} error(s)`); process.exit(1); }
  console.log(`${cc}: INFO page, ${I.actors.length} actors, ${Object.keys(S).length} sources`); console.log("OK"); process.exit(0);
}
if (!E) { console.error("Neither ED_ nor INFO_ defined"); process.exit(1); }
// Edition
["id", "name", "lang", "strip", "stripDate", "status"].forEach(f => str(E[f], `ED.${f}`));
if (E.id !== cc) errs.push(`ED.id should be “${cc}”`);
if (!["pres", "leader"].includes(E.role)) errs.push("ED.role must be pres or leader");
if (!Array.isArray(E.facts) || E.facts.length !== 3) errs.push("ED.facts must have 3 rows");
(E.facts || []).forEach((r, i) => { str(r[0], `facts[${i}][0]`); str(r[1], `facts[${i}][1]`); });
(E.factsSrc || []).forEach(k => srcOk(k, "factsSrc"));
if (!Array.isArray(E.system) || E.system.length < 4 || E.system.length > 6) errs.push("ED.system must have 4–6 rows");
(E.system || []).forEach((r, i) => { str(r[0], `system[${i}][0]`); str(r[1], `system[${i}][1]`); });
(E.systemSrc || []).forEach(k => srcOk(k, "systemSrc"));
if (!Array.isArray(E.others)) errs.push("ED.others must be an array");
if (E.othersSrc) srcOk(E.othersSrc, "othersSrc");
// Parties
const P = E.parties || [];
if (P.length < 3 || P.length > 6) errs.push(`ED.parties: ${P.length} (need 3–6)`);
const pids = new Set();
P.forEach((p, i) => {
  if (!/^[a-z0-9_]+$/.test(p.id || "")) errs.push(`parties[${i}].id must be lower-case letters, digits, _`);
  else if (!p.id.startsWith(cc + "_") && cc !== "ng") warns.push(`parties[${i}].id should look like ${cc}_abc`);
  if (pids.has(p.id)) errs.push(`duplicate party id ${p.id}`); pids.add(p.id);
  ["sigle", "nom", "cand", "tag"].forEach(f => str(p[f], `parties[${i}].${f}`));
  if (!Array.isArray(p.col) || !hex(p.col[0]) || !hex(p.col[1])) errs.push(`parties[${i}].col must be ["#RRGGBB", "#RRGGBB"]`);
  if ((p.sigle || "").length > 8) warns.push(`parties[${i}].sigle longer than 8 chars (badge)`);
  if (!Array.isArray(p.commit) || p.commit.length < 3) errs.push(`parties[${i}].commit needs 3–6 items`);
  (p.commit || []).forEach((c, j) => { str(c[0], `parties[${i}].commit[${j}]`); srcOk(c[1], `parties[${i}].commit[${j}]`); });
  if (p.tagSrc) srcOk(p.tagSrc, `parties[${i}].tagSrc`);
});
// Themes
const T = E.themes || [];
if (T.length < 8 || T.length > 10) errs.push(`ED.themes: ${T.length} (need 8–10)`);
const tids = new Set();
T.forEach((t, i) => { str(t.id, `themes[${i}].id`); str(t.name, `themes[${i}].name`); str(t.min, `themes[${i}].min`); if (tids.has(t.id)) errs.push(`duplicate theme ${t.id}`); tids.add(t.id); });
// Questions
const Q = E.questions || [];
if (Q.length < 25 || Q.length > 40) errs.push(`ED.questions: ${Q.length} (need 25–40)`);
const perTheme = {}, cover = {};
P.forEach(p => cover[p.id] = 0);
Q.forEach((q, i) => {
  const w = `questions[${i}]`;
  if (!tids.has(q.theme)) errs.push(`${w}.theme “${q.theme}” not in themes`);
  perTheme[q.theme] = (perTheme[q.theme] || 0) + 1;
  ["short", "text", "ctx"].forEach(f => str(q[f], `${w}.${f}`));
  const cells = q.cells || {};
  const n = Object.keys(cells).length;
  if (n < 2) warns.push(`${w} (“${q.short}”): only ${n} party coded`);
  for (const [pid, c] of Object.entries(cells)) {
    if (!pids.has(pid)) errs.push(`${w}.cells: unknown party ${pid}`);
    if (![2, 1, 0, -1, -2].includes(c.p)) errs.push(`${w}.cells.${pid}.p invalid`);
    if (!["stated", "record", "older", "party"].includes(c.k)) errs.push(`${w}.cells.${pid}.k invalid`);
    srcOk(c.s, `${w}.cells.${pid}.s`); str(c.n, `${w}.cells.${pid}.n`);
    cover[pid] = (cover[pid] || 0) + 1;
  }
  for (const [pid, note] of Object.entries(q.nd || {})) {
    if (!pids.has(pid)) errs.push(`${w}.nd: unknown party ${pid}`);
    if (cells[pid]) errs.push(`${w}.nd.${pid}: party is also coded in cells`);
    str(note, `${w}.nd.${pid}`);
  }
});
for (const [t, n] of Object.entries(perTheme)) if (n < 3 || n > 6) warns.push(`theme ${t}: ${n} questions (aim 3–6)`);
T.forEach(t => { if (!perTheme[t.id]) errs.push(`theme ${t.id} has no question`); });
for (const [pid, n] of Object.entries(cover)) if (Q.length && n / Q.length < 0.35) warns.push(`party ${pid}: coded on ${n}/${Q.length} questions`);
// Unused sources
const used = new Set([M && M.src, ...(E.factsSrc || []), ...(E.systemSrc || []), E.othersSrc, ...P.flatMap(p => (p.commit || []).map(c => c[1])), ...P.map(p => p.tagSrc), ...Q.flatMap(q => Object.values(q.cells || {}).map(c => c.s))]);
Object.keys(S).forEach(k => { if (!used.has(k)) warns.push(`source ${k} is never used`); });

// Optional i18n parity
const i18nFile = process.argv[3];
if (i18nFile) {
  const c2 = {}; vm.createContext(c2);
  try { vm.runInContext(fs.readFileSync(i18nFile, "utf8") + `\n;this.__I = I18N_${CC};`, c2, { filename: i18nFile }); }
  catch (e) { console.error("I18N LOAD ERROR:", e.message); process.exit(1); }
  const I = c2.__I;
  const langs = (process.argv[4] || Object.keys(c2.__I).join(",")).split(",").filter(Boolean);
  for (const l of langs) {
    const L = I[l];
    if (!L) { errs.push(`i18n.${l} missing`); continue; }
    ["strip", "stripDate", "status"].forEach(f => str(L[f], `i18n.${l}.${f}`));
    if (!Array.isArray(L.facts) || L.facts.length !== E.facts.length) errs.push(`i18n.${l}.facts length`);
    if (!Array.isArray(L.system) || L.system.length !== E.system.length) errs.push(`i18n.${l}.system length`);
    if (!Array.isArray(L.others) || L.others.length !== E.others.length) errs.push(`i18n.${l}.others length`);
    P.forEach(p => {
      str((L.tags || {})[p.id], `i18n.${l}.tags.${p.id}`);
      const cm = (L.commits || {})[p.id];
      if (!Array.isArray(cm) || cm.length !== p.commit.length) errs.push(`i18n.${l}.commits.${p.id} length`);
      if (p.candNote) str((L.candNotes || {})[p.id], `i18n.${l}.candNotes.${p.id}`);
    });
    T.forEach(t => { const x = (L.themes || {})[t.id]; if (!Array.isArray(x) || x.length !== 2) errs.push(`i18n.${l}.themes.${t.id}`); });
    if (!Array.isArray(L.q) || L.q.length !== Q.length) { errs.push(`i18n.${l}.q length ${L.q && L.q.length} ≠ ${Q.length}`); continue; }
    Q.forEach((q, i) => {
      const tq = L.q[i] || {};
      ["short", "text", "ctx"].forEach(f => str(tq[f], `i18n.${l}.q[${i}].${f}`));
      Object.keys(q.cells || {}).forEach(pid => str((tq.n || {})[pid], `i18n.${l}.q[${i}].n.${pid}`));
      Object.keys(q.nd || {}).forEach(pid => str((tq.nd || {})[pid], `i18n.${l}.q[${i}].nd.${pid}`));
    });
  }
}

console.log(`${cc}: ${P.length} parties, ${T.length} themes, ${Q.length} questions, ${Object.keys(S).length} sources`);
console.log("coverage: " + P.map(p => `${p.sigle} ${cover[p.id]}/${Q.length}`).join(" · "));
warns.forEach(w => console.log("WARN  " + w));
errs.forEach(e => console.log("ERROR " + e));
if (errs.length) { console.log(`${errs.length} error(s)`); process.exit(1); }
console.log("OK");
