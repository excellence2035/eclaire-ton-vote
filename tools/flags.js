#!/usr/bin/env node
/* Installe les drapeaux dans flags/<cc>.svg (outil de construction, à lancer à la main).
 *
 *   node tools/flags.js [--keep] [--no-svgo]
 *
 * - Installe le paquet « flag-icons » (licence MIT) et « svgo » dans un dossier temporaire (npm requis, accès au registre).
 * - Copie le drapeau 4×3 de chaque pays de la carte (src/africa.js) et de la France dans flags/<cc>.svg (code ISO alpha-2
 *   en minuscules), optimisé avec svgo, plus la licence dans flags/LICENSE.
 * - Affiche chaque fichier de plus de 15 Ko et le total. Les drapeaux ne sont jamais incorporés à index.html :
 *   ce sont des fichiers à côté de la page (tools/build.js les recopie dans le dossier de sortie quand --out en change).
 * Les fichiers de flags/ sont versionnés : ce script ne sert qu'à les refaire (nouveau pays, nouvelle version du paquet).
 */
"use strict";
const fs = require("fs"), os = require("os"), path = require("path"), vm = require("vm"), { spawnSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "flags");
const PKG = "flag-icons@7.6.0", SVGO = "svgo@4.1.0";
const args = process.argv.slice(2);
const noSvgo = args.includes("--no-svgo");

function africaCodes() {
  const ctx = {};
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, "src", "africa.js"), "utf8") + "\n;this.__a = AFRICA;", ctx, { timeout: 5000 });
  return Object.values(JSON.parse(JSON.stringify(ctx.__a))).map(c => c.a2.toLowerCase());
}

const codes = [...new Set([...africaCodes(), "fr"])].sort();
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "etv-flags-"));
console.log(`npm install ${PKG}${noSvgo ? "" : " " + SVGO} in ${tmp}`);
fs.writeFileSync(path.join(tmp, "package.json"), JSON.stringify({ name: "etv-flags-tmp", private: true }));
const r = spawnSync("npm", ["install", "--no-audit", "--no-fund", "--loglevel=error", PKG, ...(noSvgo ? [] : [SVGO])], { cwd: tmp, encoding: "utf8", timeout: 240000 });
if (r.status !== 0) { console.error((r.stdout || "") + (r.stderr || "")); console.error("npm install failed"); process.exit(1); }

const pkgDir = path.join(tmp, "node_modules", "flag-icons");
const version = JSON.parse(fs.readFileSync(path.join(pkgDir, "package.json"), "utf8")).version;
let svgo = null;
if (!noSvgo) { try { svgo = require(path.join(tmp, "node_modules", "svgo", "dist", "svgo-node.cjs")); } catch (e) { console.warn("svgo unavailable, files are copied as they are"); } }

fs.mkdirSync(OUT, { recursive: true });
let total = 0, big = [];
const missing = [];
for (const cc of codes) {
  const src = path.join(pkgDir, "flags", "4x3", cc + ".svg");
  if (!fs.existsSync(src)) { missing.push(cc); continue; }
  let svg = fs.readFileSync(src, "utf8");
  if (svgo) {
    // svgo ≥ 4 garde le viewBox (la taille d'affichage est fixée par width/height de la balise <img>)
    svg = svgo.optimize(svg, { multipass: true, plugins: ["preset-default"] }).data;
  }
  const f = path.join(OUT, cc + ".svg");
  fs.writeFileSync(f, svg);
  const n = Buffer.byteLength(svg);
  total += n;
  if (n > 15 * 1024) big.push([cc, n]);
}
fs.copyFileSync(path.join(pkgDir, "LICENSE"), path.join(OUT, "LICENSE"));
fs.writeFileSync(path.join(OUT, "README.txt"), `Drapeaux : paquet npm « flag-icons » ${version} (licence MIT, voir LICENSE), format 4×3, optimisés avec svgo.\nRefaire : node tools/flags.js\n`);

console.log(`flag-icons ${version}: ${codes.length - missing.length} flag(s) written to flags/, total ${(total / 1024).toFixed(1)} KB`);
if (missing.length) console.warn(`missing in the package: ${missing.join(", ")}`);
if (big.length) console.warn(`over 15 KB: ${big.map(([c, n]) => `${c} ${(n / 1024).toFixed(1)} KB`).join(", ")}`);
else console.log("no file over 15 KB");
try { fs.rmSync(tmp, { recursive: true, force: true }); } catch (e) { /* ignore */ }
if (missing.length) process.exit(1);
