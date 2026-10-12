#!/usr/bin/env node
/* Éclaire ton vote : construit le site à partir de src/.
 *
 *   node tools/build.js [--extra <dir>]... [--out <dir>] [--strict]
 *
 * - Lit chaque src/editions/<cc>.js (et src/i18n/<cc>.js s'il existe), le valide avec
 *   src/tools/validate-edition.js et écrit data/<cc>.json. Une édition qui ne passe pas est ignorée
 *   (avertissement), une langue dont la traduction est incomplète aussi. La France (fr) est dispensée
 *   de validation (elle dépasse volontairement les limites du validateur).
 * - Écrit index.html (page complète) et artifact.html (même page sans doctype/html/head/body, pour
 *   l'hébergeur d'artefacts Claude qui ajoute son propre squelette ; elle commence par <title>).
 * - --extra <dir> ajoute des éditions de <dir>/editions/<cc>.js (+ <dir>/i18n/<cc>.js), par ex. pour les tests ;
 *   elles remplacent une édition de même code. --out <dir> écrit ailleurs qu'à la racine du dépôt.
 *   --strict : code de sortie 1 s'il y a eu le moindre avertissement.
 * Aucune dépendance : Node ≥ 18.
 */
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm"), { spawnSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "src");
const VALIDATOR = path.join(SRC, "tools", "validate-edition.js");
const EXEMPT = new Set(["fr"]);
const UI_FILES = ["ui/t-fr-en.js", "ui/t-pt-sw-ar.js", "ui/t-party.js", "ui/t-party-pt-sw-ar.js", "ui/t-multi.js"];
const DESCRIPTION = "Réponds à des questions précises par ministère et découvre quels partis pensent comme toi. Carte des élections dans les 54 pays d’Afrique, questionnaires par pays, en 5 langues.";
const FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%235A2DB8'/%3E%3Cpath d='M8 17l6 6L27 7' fill='none' stroke='%23F2B42C' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E";
const RESET = "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>";

/* ---------- Arguments ---------- */
const extras = [];
let OUT = ROOT, strict = false;
const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--extra" && argv[i + 1]) extras.push(path.resolve(argv[++i]));
  else if (a === "--out" && argv[i + 1]) OUT = path.resolve(argv[++i]);
  else if (a === "--strict") strict = true;
  else if (a === "-h" || a === "--help") { console.log("usage: node tools/build.js [--extra <dir>]... [--out <dir>] [--strict]"); process.exit(0); }
  else { console.error(`unknown argument: ${a}`); process.exit(2); }
}

const warnings = [];
const warn = msg => { warnings.push(msg); console.log("WARN  " + msg); };
const read = f => fs.readFileSync(f, "utf8");

/* Exécute un fichier source dans un bac à sable et renvoie les globales demandées. */
function runFile(file, names) {
  const ctx = {};
  vm.createContext(ctx);
  const grab = names.map(n => `${JSON.stringify(n)}: typeof ${n} !== "undefined" ? ${n} : undefined`).join(", ");
  vm.runInContext(read(file) + `\n;this.__x = { ${grab} };`, ctx, { filename: file, timeout: 5000 });
  // JSON aller-retour : objets « normaux » (le contexte vm a ses propres prototypes)
  return JSON.parse(JSON.stringify(ctx.__x));
}
function validate(args) {
  const r = spawnSync(process.execPath, [VALIDATOR, ...args], { cwd: ROOT, encoding: "utf8", timeout: 30000 });
  const out = (r.stdout || "") + (r.stderr || "");
  return { ok: r.status === 0, out, errors: out.split("\n").filter(l => /^(ERROR|LOAD ERROR|I18N LOAD ERROR)|Neither/.test(l)) };
}
const isStr = v => typeof v === "string" && v.trim() !== "";
const pairs = (a, n) => Array.isArray(a) && a.length === n && a.every(r => Array.isArray(r) && isStr(r[0]) && isStr(r[1]));

/* Parité d'une traduction de page d'information (le validateur ne la vérifie pas). */
function infoParity(I, L) {
  const e = [];
  if (!L || typeof L !== "object") return ["missing"];
  ["strip", "stripDate", "why"].forEach(k => { if (!isStr(L[k])) e.push(k); });
  if (!pairs(L.facts, (I.facts || []).length)) e.push("facts");
  if (!pairs(L.system, (I.system || []).length)) e.push("system");
  if (!pairs(L.actors, (I.actors || []).length)) e.push("actors");
  return e;
}
/* Parité d'une traduction de questionnaire, pour les éditions dispensées du validateur. */
function edParity(E, L) {
  const e = [];
  if (!L || typeof L !== "object") return ["missing"];
  ["strip", "stripDate", "status"].forEach(k => { if (!isStr(L[k])) e.push(k); });
  ["facts", "system", "others"].forEach(k => { if (!Array.isArray(L[k]) || L[k].length !== (E[k] || []).length) e.push(k); });
  E.parties.forEach(p => {
    if (!isStr((L.tags || {})[p.id])) e.push(`tags.${p.id}`);
    const cm = (L.commits || {})[p.id];
    if (!Array.isArray(cm) || cm.length !== p.commit.length) e.push(`commits.${p.id}`);
    if (p.candNote && !isStr((L.candNotes || {})[p.id])) e.push(`candNotes.${p.id}`);
  });
  E.themes.forEach(t => { const x = (L.themes || {})[t.id]; if (!Array.isArray(x) || x.length !== 2) e.push(`themes.${t.id}`); });
  if (!Array.isArray(L.q) || L.q.length !== E.questions.length) e.push("q length");
  else E.questions.forEach((q, i) => {
    const tq = L.q[i] || {};
    ["short", "text", "ctx"].forEach(k => { if (!isStr(tq[k])) e.push(`q[${i}].${k}`); });
    Object.keys(q.cells || {}).forEach(pid => { if (!isStr((tq.n || {})[pid])) e.push(`q[${i}].n.${pid}`); });
    Object.keys(q.nd || {}).forEach(pid => { if (!isStr((tq.nd || {})[pid])) e.push(`q[${i}].nd.${pid}`); });
  });
  return e;
}
/* Contrôle minimal d'une édition dispensée du validateur : de quoi ne pas casser l'application. */
function basicCheck(cc, E) {
  const e = [];
  if (!E || E.id !== cc) e.push("id");
  if (!isStr(E && E.lang)) e.push("lang");
  if (!Array.isArray(E.parties) || !E.parties.length) e.push("parties");
  if (!Array.isArray(E.themes) || !E.themes.length) e.push("themes");
  if (!Array.isArray(E.questions) || !E.questions.length) e.push("questions");
  if (!e.length) {
    const pids = new Set(E.parties.map(p => p.id)), tids = new Set(E.themes.map(t => t.id));
    E.questions.forEach((q, i) => {
      if (!tids.has(q.theme)) e.push(`questions[${i}].theme`);
      Object.keys(q.cells || {}).forEach(pid => { if (!pids.has(pid)) e.push(`questions[${i}].cells.${pid}`); });
    });
    E.parties.forEach((p, i) => { if (!Array.isArray(p.commit)) e.push(`parties[${i}].commit`); });
  }
  return e;
}

/* ---------- Référentiels : langues de l'interface, pays africains ---------- */
const UI_LANGS = runFile(path.join(SRC, "ui/t-fr-en.js"), ["LANGS"]).LANGS.map(l => l.code);
const AFRICA = runFile(path.join(SRC, "africa.js"), ["AFRICA"]).AFRICA;
const A2_TO_NUM = {};
Object.entries(AFRICA).forEach(([num, c]) => { A2_TO_NUM[c.a2.toLowerCase()] = num; });

/* ---------- Éditions ---------- */
const sources = new Map(); // cc → { file, i18n }
function collect(dir, label) {
  const edDir = path.join(dir, "editions");
  if (!fs.existsSync(edDir)) { if (label !== "src") warn(`${label}: no editions/ folder in ${dir}`); return; }
  fs.readdirSync(edDir).filter(f => f.endsWith(".js")).sort().forEach(f => {
    const cc = f.slice(0, -3);
    if (!/^[a-z]{2}$/.test(cc)) { warn(`${label}/editions/${f}: file name must be a lower-case ISO alpha-2 code, skipped`); return; }
    if (sources.has(cc)) warn(`${cc}: edition from ${dir} replaces the one in ${sources.get(cc).dir}`);
    const i18n = path.join(dir, "i18n", cc + ".js");
    sources.set(cc, { dir, file: path.join(edDir, f), i18n: fs.existsSync(i18n) ? i18n : null });
  });
}
collect(SRC, "src");
extras.forEach(d => collect(d, d));

const built = [];
for (const [cc, { file, i18n }] of [...sources.entries()].sort((a, b) => a[0].localeCompare(b[0]))) {
  const CC = cc.toUpperCase();
  let mod;
  try { mod = runFile(file, [`SRC_${CC}`, `META_${CC}`, `ED_${CC}`, `INFO_${CC}`]); }
  catch (e) { warn(`${cc}: cannot load ${path.relative(ROOT, file)} (${e.message.split("\n")[0]}), skipped`); continue; }
  const S = mod[`SRC_${CC}`], M = mod[`META_${CC}`], E = mod[`ED_${CC}`], I = mod[`INFO_${CC}`];
  const kind = E ? "ed" : I ? "info" : null;
  const base = E || I;
  if (!kind || !S || !M) { warn(`${cc}: needs SRC_${CC}, META_${CC} and ED_${CC} or INFO_${CC}, skipped`); continue; }

  if (EXEMPT.has(cc)) {
    const errs = kind === "ed" ? basicCheck(cc, E) : infoParity(I, I);
    if (errs.length) { warn(`${cc}: invalid (${errs.slice(0, 5).join(", ")}), skipped`); continue; }
  } else {
    const v = validate([file]);
    if (!v.ok) { warn(`${cc}: validation failed, skipped\n        ${v.errors.slice(0, 6).join("\n        ") || v.out.trim().split("\n").slice(-3).join("\n        ")}`); continue; }
  }
  if (!UI_LANGS.includes(base.lang)) { warn(`${cc}: base language “${base.lang}” is not an interface language (${UI_LANGS.join(", ")}), skipped`); continue; }

  // Langues : la langue de base + chaque traduction complète
  const langs = [base.lang], tr = {};
  if (i18n) {
    let all = null;
    try { all = runFile(i18n, [`I18N_${CC}`])[`I18N_${CC}`]; }
    catch (e) { warn(`${cc}: cannot load ${path.relative(ROOT, i18n)} (${e.message.split("\n")[0]}), translations ignored`); }
    if (all && typeof all === "object") {
      for (const lang of Object.keys(all)) {
        if (lang === base.lang) { warn(`${cc}: i18n.${lang} is the base language, ignored`); continue; }
        if (!UI_LANGS.includes(lang)) { warn(`${cc}: i18n.${lang} is not an interface language, dropped`); continue; }
        let errs;
        if (kind === "info") errs = infoParity(I, all[lang]);
        else if (EXEMPT.has(cc)) errs = edParity(E, all[lang]);
        else { const v = validate([file, i18n, lang]); errs = v.ok ? [] : v.errors.map(l => l.replace(/^ERROR\s+/, "")); }
        if (errs.length) { warn(`${cc}: translation “${lang}” incomplete, dropped (${errs.slice(0, 4).join("; ")}${errs.length > 4 ? ` … ${errs.length} problems` : ""})`); continue; }
        langs.push(lang); tr[lang] = all[lang];
      }
    } else if (all !== null) warn(`${cc}: I18N_${CC} missing in ${path.relative(ROOT, i18n)}`);
  }

  const a3 = A2_TO_NUM[cc] || null;
  if (!a3 && !EXEMPT.has(cc)) warn(`${cc}: not one of the 54 countries on the map; reachable only by a direct link`);
  const data = { kind, id: cc, a3, lang: base.lang, langs, meta: M, src: S, [kind]: base, i18n: tr };
  const evSrc = M.src && S[M.src] ? S[M.src] : null;
  const cat = { kind, a3, langs, ev: M.ev || [], evSrc };
  if (M.note) cat.note = M.note;
  built.push({ cc, data, cat });
  const what = kind === "ed" ? `${E.parties.length} parties, ${E.questions.length} questions` : `${I.actors.length} actors`;
  console.log(`ok    ${cc}: ${kind === "ed" ? "questionnaire" : "information page"}, ${what}, langs ${langs.join(",")}${EXEMPT.has(cc) ? " (validation exempt)" : ""}`);
}

/* ---------- Écriture : data/<cc>.json ---------- */
const dataDir = path.join(OUT, "data");
fs.mkdirSync(dataDir, { recursive: true });
const sizes = [];
const keep = new Set();
for (const { cc, data } of built) {
  const f = path.join(dataDir, cc + ".json");
  const json = JSON.stringify(data);
  fs.writeFileSync(f, json);
  keep.add(cc + ".json");
  sizes.push([path.relative(OUT, f), Buffer.byteLength(json)]);
}
for (const f of fs.readdirSync(dataDir)) {
  if (f.endsWith(".json") && !keep.has(f)) { fs.unlinkSync(path.join(dataDir, f)); console.log(`rm    data/${f} (no valid edition)`); }
}

/* ---------- Écriture : index.html et artifact.html ---------- */
const shell = read(path.join(SRC, "shell.html"));
const cut = shell.indexOf("</style>");
if (!shell.startsWith("<title>") || cut < 0) throw new Error("src/shell.html must start with <title> and contain the main <style> block");
const shellHead = shell.slice(0, cut + "</style>".length);
const shellBody = shell.slice(cut + "</style>".length).replace(/^\n+/, "");
const app = read(path.join(SRC, "app.js"));
if (!app.trimEnd().endsWith("</script>")) throw new Error("src/app.js must end with </script> (it closes the script tag opened in shell.html)");

const catalog = {};
built.forEach(({ cc, cat }) => { catalog[cc] = cat; });
const scripts = [...UI_FILES, "africa.js", "mapdata.js"].map(f => read(path.join(SRC, f)).replace(/\s+$/, "") + "\n").join("")
  + "\n/* ================== Catalogue des éditions (généré par tools/build.js) ================== */\n"
  + `const CATALOG = ${JSON.stringify(catalog)};\n`
  + app.replace(/\s+$/, "") + "\n";

const index = `<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="${DESCRIPTION}">
<meta property="og:title" content="Éclaire ton vote">
<meta property="og:description" content="${DESCRIPTION}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#5A2DB8">
<link rel="icon" href="${FAVICON}">
${RESET}
${shellHead}
</head>
<body>
${shellBody}${scripts}
</body>
</html>
`;
const nl = shell.indexOf("\n");
const artifact = shell.slice(0, nl + 1) + RESET + "\n" + shell.slice(nl + 1).replace(/\s+$/, "\n") + scripts;

fs.writeFileSync(path.join(OUT, "index.html"), index);
fs.writeFileSync(path.join(OUT, "artifact.html"), artifact);
sizes.unshift(["index.html", Buffer.byteLength(index)], ["artifact.html", Buffer.byteLength(artifact)]);

console.log(`\n${built.length} edition(s): ${built.map(b => `${b.cc} (${b.cat.kind})`).join(", ") || "none"}`);
sizes.forEach(([f, n]) => console.log(`  ${f.padEnd(18)} ${(n / 1024).toFixed(1).padStart(7)} KB`));
if (warnings.length) console.log(`${warnings.length} warning(s)`);
if (strict && warnings.length) process.exit(1);
