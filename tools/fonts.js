#!/usr/bin/env node
/* Installe les polices dans fonts/ (outil de construction, à lancer à la main).
 *
 *   node tools/fonts.js [--keep]
 *
 * - Installe les paquets npm « @fontsource-variable/bricolage-grotesque » et « @fontsource-variable/readex-pro »
 *   (polices variables sous licence SIL OFL 1.1) dans un dossier temporaire (npm requis, accès au registre).
 * - Copie, sous des noms stables, les fichiers WOFF2 dont la page a besoin :
 *     bricolage-grotesque-latin(.ext).woff2   titres ; axes graisse (200–800) et chasse (75–100 %)
 *     readex-pro-latin(.ext).woff2            texte courant ; axe graisse (160–700)
 *     readex-pro-arabic.woff2                 texte courant en arabe
 *   Le vietnamien, l'axe « corps optique » de Bricolage et l'axe « HEXP » de Readex sont laissés de côté (aucune des 5 langues
 *   de l'interface n'en a besoin, et l'axe de corps optique pèserait 50 Ko de plus).
 * - Copie les licences dans fonts/LICENSE-*.txt, affiche chaque fichier de plus de 15 Ko et le total, puis le poids d'un visiteur qui
 *   lit en alphabet latin (le seul poids chargé d'emblée) : il doit rester sous 120 Ko.
 * Les @font-face (avec unicode-range et font-display: swap) sont écrits à la main dans src/shell.html, avec les mêmes plages
 * que les paquets ; ce script ne fait que fournir les fichiers. Ils sont versionnés ; tools/build.js les recopie dans le
 * dossier de sortie quand --out en change. La page ne contacte aucun serveur de polices.
 */
"use strict";
const fs = require("fs"), os = require("os"), path = require("path"), { spawnSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "fonts");
const PKGS = { bricolage: "@fontsource-variable/bricolage-grotesque@5.3.0", readex: "@fontsource-variable/readex-pro@5.3.0" };
// [paquet, fichier du paquet, nom publié]
const FILES = [
  ["bricolage", "bricolage-grotesque-latin-wdth-normal.woff2", "bricolage-grotesque-latin.woff2"],
  ["bricolage", "bricolage-grotesque-latin-ext-wdth-normal.woff2", "bricolage-grotesque-latin-ext.woff2"],
  ["readex", "readex-pro-latin-wght-normal.woff2", "readex-pro-latin.woff2"],
  ["readex", "readex-pro-latin-ext-wght-normal.woff2", "readex-pro-latin-ext.woff2"],
  ["readex", "readex-pro-arabic-wght-normal.woff2", "readex-pro-arabic.woff2"]
];
const LATIN_ONLY = ["bricolage-grotesque-latin.woff2", "readex-pro-latin.woff2"];
const BUDGET = 120 * 1024;

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "etv-fonts-"));
console.log(`npm install ${Object.values(PKGS).join(" ")} in ${tmp}`);
fs.writeFileSync(path.join(tmp, "package.json"), JSON.stringify({ name: "etv-fonts-tmp", private: true }));
const r = spawnSync("npm", ["install", "--no-audit", "--no-fund", "--loglevel=error", ...Object.values(PKGS)], { cwd: tmp, encoding: "utf8", timeout: 240000 });
if (r.status !== 0) { console.error((r.stdout || "") + (r.stderr || "")); console.error("npm install failed"); process.exit(1); }

const pkgDir = k => path.join(tmp, "node_modules", "@fontsource-variable", k === "bricolage" ? "bricolage-grotesque" : "readex-pro");
fs.mkdirSync(OUT, { recursive: true });
let total = 0;
const sizes = {}, big = [];
for (const [k, from, to] of FILES) {
  const src = path.join(pkgDir(k), "files", from);
  if (!fs.existsSync(src)) { console.error(`missing ${from} in the ${k} package`); process.exit(1); }
  fs.copyFileSync(src, path.join(OUT, to));
  const n = fs.statSync(src).size;
  sizes[to] = n; total += n;
  if (n > 15 * 1024) big.push([to, n]);
}
const versions = {};
for (const k of Object.keys(PKGS)) {
  versions[k] = JSON.parse(fs.readFileSync(path.join(pkgDir(k), "package.json"), "utf8")).version;
  fs.copyFileSync(path.join(pkgDir(k), "LICENSE"), path.join(OUT, `LICENSE-${k === "bricolage" ? "bricolage-grotesque" : "readex-pro"}.txt`));
}
fs.writeFileSync(path.join(OUT, "README.txt"),
  `Polices : Bricolage Grotesque ${versions.bricolage} (titres) et Readex Pro ${versions.readex} (texte), paquets npm « @fontsource-variable/* »,\n` +
  `SIL Open Font License 1.1 (voir LICENSE-*.txt). WOFF2 variables ; Bricolage : axes graisse + chasse, Readex Pro : axe graisse.\n` +
  `Les @font-face sont dans src/shell.html. Refaire : node tools/fonts.js\n`);

console.log(`\nfonts/ : ${FILES.length} fichiers, ${(total / 1024).toFixed(1)} Ko en tout`);
for (const [to, n] of Object.entries(sizes)) console.log(`  ${to.padEnd(36)} ${(n / 1024).toFixed(1).padStart(6)} Ko`);
if (big.length) console.log(`plus de 15 Ko : ${big.map(([f, n]) => `${f} ${(n / 1024).toFixed(1)} Ko`).join(", ")}`);
const latin = LATIN_ONLY.reduce((s, f) => s + sizes[f], 0);
console.log(`visiteur en alphabet latin : ${(latin / 1024).toFixed(1)} Ko (objectif : moins de ${BUDGET / 1024} Ko)`);
if (latin > BUDGET) { console.error("over the budget"); process.exit(1); }
if (!process.argv.includes("--keep")) fs.rmSync(tmp, { recursive: true, force: true });
