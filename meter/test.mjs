/* Test du Worker du compteur (Node >= 18) : node meter/test.mjs
 *
 * Joue le même scénario sur deux bases D1 : une fausse base en mémoire (portable, elle n'accepte que les instructions SQL
 * connues, donc une instruction modifiée dans worker.js fait échouer le test) et, si Node a node:sqlite (Node >= 22.5), un
 * vrai SQLite qui exécute schema.sql : le SQL réel est alors vérifié aussi.
 */
import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { webcrypto } from "node:crypto";
import vm from "node:vm";

if (!globalThis.crypto) globalThis.crypto = webcrypto;
const HERE = dirname(fileURLToPath(import.meta.url));
let checks = 0;
const ok = (cond, msg) => { if (!cond) { console.error("FAIL  " + msg); process.exitCode = 1; throw new Error(msg); } checks++; };
const eq = (a, b, msg) => ok(JSON.stringify(a) === JSON.stringify(b), `${msg}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`);

/* ---------- Le Worker, avec la liste des pays incorporée (Node n'importe pas le JSON comme Wrangler) ---------- */
const src = readFileSync(join(HERE, "worker.js"), "utf8");
const COUNTRIES = JSON.parse(readFileSync(join(HERE, "countries.json"), "utf8"));
const IMPORT = /^import COUNTRIES from "\.\/countries\.json";$/m;
ok(IMPORT.test(src), "worker.js imports ./countries.json");
const tmp = mkdtempSync(join(tmpdir(), "vote-meter-"));
writeFileSync(join(tmp, "worker.mjs"), src.replace(IMPORT, `const COUNTRIES = ${JSON.stringify(COUNTRIES)};`));
const worker = (await import(pathToFileURL(join(tmp, "worker.mjs")).href)).default;
rmSync(tmp, { recursive: true, force: true });

/* ---------- Horloge réglable ---------- */
const RealDate = Date;
let NOW = RealDate.parse("2026-10-22T10:00:00Z");
globalThis.Date = class extends RealDate {
  constructor(...a) { if (a.length === 0) super(NOW); else super(...a); }
  static now() { return NOW; }
};
const setDay = iso => { NOW = RealDate.parse(iso); };

/* ---------- Fausse base D1 : seulement les instructions du Worker ---------- */
const KNOWN = {
  saltNew: "INSERT OR IGNORE INTO meta (k, v) VALUES (?1, ?2)",
  metaGet: "SELECT v FROM meta WHERE k = ?1",
  limit: "INSERT INTO limits (h, day, n) VALUES (?1, ?2, 1) ON CONFLICT (h, day) DO UPDATE SET n = n + 1 WHERE n < ?3 RETURNING n",
  count: "INSERT INTO counts (country, level, n) VALUES (?1, ?2, 1) ON CONFLICT (country, level) DO UPDATE SET n = n + 1",
  updated: "INSERT INTO meta (k, v) VALUES ('updated', ?1) ON CONFLICT (k) DO UPDATE SET v = excluded.v",
  purgeLimits: "DELETE FROM limits WHERE day < ?1",
  purgeSalts: "DELETE FROM meta WHERE k LIKE 'salt:%' AND k < ?1",
  all: "SELECT country, level, n FROM counts",
};
const KIND = Object.fromEntries(Object.entries(KNOWN).map(([k, v]) => [v, k]));

function fakeD1() {
  const T = { counts: new Map(), limits: new Map(), meta: new Map() };
  const exec = (sql, a) => {
    const kind = KIND[sql];
    if (!kind) throw new Error("unknown SQL in the fake D1: " + sql);
    switch (kind) {
      case "saltNew": if (T.meta.has(a[0])) return { changes: 0, rows: [] }; T.meta.set(a[0], a[1]); return { changes: 1, rows: [] };
      case "metaGet": return { changes: 0, rows: T.meta.has(a[0]) ? [{ v: T.meta.get(a[0]) }] : [] };
      case "limit": {
        const key = a[0] + "|" + a[1], cur = T.limits.get(key);
        if (cur === undefined) { T.limits.set(key, { h: a[0], day: a[1], n: 1 }); return { changes: 1, rows: [{ n: 1 }] }; }
        if (cur.n < a[2]) { cur.n++; return { changes: 1, rows: [{ n: cur.n }] }; }
        return { changes: 0, rows: [] };
      }
      case "count": { const key = a[0] + "|" + a[1]; T.counts.set(key, { country: a[0], level: a[1], n: (T.counts.get(key) || { n: 0 }).n + 1 }); return { changes: 1, rows: [] }; }
      case "updated": T.meta.set("updated", a[0]); return { changes: 1, rows: [] };
      case "purgeLimits": { let n = 0; for (const [k, r] of [...T.limits]) if (r.day < a[0]) { T.limits.delete(k); n++; } return { changes: n, rows: [] }; }
      case "purgeSalts": { let n = 0; for (const k of [...T.meta.keys()]) if (k.startsWith("salt:") && k < a[0]) { T.meta.delete(k); n++; } return { changes: n, rows: [] }; }
      case "all": return { changes: 0, rows: [...T.counts.values()].map(r => ({ ...r })) };
    }
  };
  const stmt = (sql, a = []) => ({
    sql, args: a,
    bind: (...x) => stmt(sql, x),
    run: async () => ({ success: true, meta: { changes: exec(sql, a).changes } }),
    first: async () => exec(sql, a).rows[0] || null,
    all: async () => ({ results: exec(sql, a).rows }),
  });
  return {
    prepare: sql => stmt(sql),
    batch: async list => { const out = []; for (const s of list) out.push(await s.run()); return out; },
    dump: () => JSON.stringify([[...T.counts], [...T.limits], [...T.meta]]),
    tables: T,
  };
}

/* ---------- Vrai SQLite (node:sqlite), avec schema.sql ---------- */
async function sqliteD1() {
  let DatabaseSync;
  process.removeAllListeners("warning");   // « SQLite is an experimental feature » : inutile ici
  try { ({ DatabaseSync } = await import("node:sqlite")); } catch (e) { return null; }
  const db = new DatabaseSync(":memory:");
  db.exec(readFileSync(join(HERE, "schema.sql"), "utf8"));
  const stmt = (sql, a = []) => ({
    bind: (...x) => stmt(sql, x),
    run: async () => { const r = db.prepare(sql).run(...a); return { success: true, meta: { changes: Number(r.changes) } }; },
    first: async () => db.prepare(sql).get(...a) || null,
    all: async () => ({ results: db.prepare(sql).all(...a) }),
  });
  return {
    prepare: sql => stmt(sql),
    batch: async list => { const out = []; db.exec("BEGIN"); try { for (const s of list) out.push(await s.run()); db.exec("COMMIT"); } catch (e) { db.exec("ROLLBACK"); throw e; } return out; },
    dump: () => JSON.stringify({ counts: db.prepare("SELECT * FROM counts").all(), limits: db.prepare("SELECT * FROM limits").all(), meta: db.prepare("SELECT * FROM meta").all() }),
    rows: t => db.prepare("SELECT * FROM " + t).all(),
  };
}

/* ---------- Scénario ---------- */
const BASE = "https://meter.example.test";
const post = (env, body, ip = "203.0.113.7", extra = {}) => worker.fetch(new Request(BASE + "/v", { method: "POST", headers: { "Content-Type": "text/plain", "CF-Connecting-IP": ip, ...extra }, body: typeof body === "string" ? body : JSON.stringify(body) }), env);
const get = (env, path = "/counts") => worker.fetch(new Request(BASE + path), env);

async function scenario(name, db, rows) {
  const env = { DB: db };
  const logged = [];
  const spies = ["log", "info", "warn", "error", "debug"].map(k => { const o = console[k]; console[k] = (...a) => logged.push(a); return [k, o]; });
  try {
    setDay("2026-10-22T10:00:00Z");
    // vide
    let r = await get(env);
    ok(r.status === 200, `${name}: GET /counts on an empty base`);
    eq(await r.json(), { updated: "", total: { "-2": 0, "-1": 0, "0": 0, "1": 0, "2": 0 }, byCountry: {} }, `${name}: empty counts`);
    ok(r.headers.get("access-control-allow-origin") === "*", `${name}: CORS * on GET`);
    ok(r.headers.get("cache-control") === "public, max-age=60", `${name}: Cache-Control public, max-age=60`);
    ok(/^application\/json/.test(r.headers.get("content-type")), `${name}: JSON content type`);
    ok(!r.headers.get("set-cookie"), `${name}: no cookie`);
    // une contribution
    r = await post(env, { c: "ng", l: 1 });
    ok(r.status === 204 && (await r.text()) === "", `${name}: POST /v → 204, empty body`);
    ok(r.headers.get("access-control-allow-origin") === "*" && !r.headers.get("set-cookie"), `${name}: CORS * on POST, no cookie`);
    r = await get(env);
    let j = await r.json();
    eq(j.total, { "-2": 0, "-1": 0, "0": 0, "1": 1, "2": 0 }, `${name}: total after one answer`);
    eq(j.byCountry, { ng: { "-2": 0, "-1": 0, "0": 0, "1": 1, "2": 0 } }, `${name}: by country`);
    ok(j.updated === "2026-10-22T10:00:00Z", `${name}: updated is an ISO date (${j.updated})`);
    // tous les niveaux et plusieurs pays, text/plain comme application/json, 0 négatif accepté
    for (const [c, l, ip] of [["ke", -2, "198.51.100.1"], ["ke", 0, "198.51.100.2"], ["fr", 2, "198.51.100.3"], ["ng", -1, "198.51.100.4"]]) ok((await post(env, { c, l }, ip)).status === 204, `${name}: ${c} ${l}`);
    ok((await post(env, '{"c":"ng","l":-0}', "198.51.100.5", { "Content-Type": "application/json" })).status === 204, `${name}: l = -0 is level 0`);
    j = await (await get(env)).json();
    eq(j.byCountry.ng, { "-2": 0, "-1": 1, "0": 1, "1": 1, "2": 0 }, `${name}: Nigeria distribution`);
    eq(j.byCountry.ke, { "-2": 1, "-1": 0, "0": 1, "1": 0, "2": 0 }, `${name}: Kenya distribution`);
    eq(j.total, { "-2": 1, "-1": 1, "0": 2, "1": 1, "2": 1 }, `${name}: total is the sum`);
    // incréments atomiques : 40 contributions simultanées, 40 adresses
    await Promise.all(Array.from({ length: 40 }, (_, i) => post(env, { c: "za", l: 2 }, "192.0.2." + i)));
    j = await (await get(env)).json();
    ok(j.byCountry.za["2"] === 40 && j.total["2"] === 41, `${name}: 40 simultaneous answers are all counted exactly once`);
    // validation : rien ne doit être compté
    const before = db.dump();
    const bad = ['{"c":"zz","l":1}', '{"c":"NG","l":1}', '{"c":"ng","l":3}', '{"c":"ng","l":-3}', '{"c":"ng","l":1.5}', '{"c":"ng","l":"1"}', '{"c":"ng"}', '{"l":1}',
      '{"c":"ng","l":1,"x":1}', '{"c":["ng"],"l":1}', '{"c":"__proto__","l":1}', "[]", "null", "42", '"ng"', "{", "", "c=ng&l=1", '{"c":"ng","l":null}', '{"c":"ng","l":true}'];
    for (const b of bad) { r = await post(env, b, "198.51.100.99"); ok(r.status === 400, `${name}: ${JSON.stringify(b)} → 400 (got ${r.status})`); }
    ok(db.dump() === before, `${name}: rejected requests change nothing (not even the rate limit)`);
    // taille : 200 octets au plus (en-tête et flux)
    const pad = '{"c":"ng","l":1,"p":"' + "x".repeat(300) + '"}';
    r = await post(env, pad, "198.51.100.98");
    ok(r.status === 413, `${name}: a body over 200 bytes → 413 (declared length)`);
    r = await worker.fetch(new Request(BASE + "/v", { method: "POST", headers: { "CF-Connecting-IP": "198.51.100.98" }, body: new ReadableStream({ start(ctl) { ctl.enqueue(new TextEncoder().encode(pad)); ctl.close(); } }), duplex: "half" }), env);
    ok(r.status === 413, `${name}: a body over 200 bytes → 413 (stream, no declared length)`);
    const exact = '{"c":"ng","l":1}' + " ".repeat(184);
    ok(new TextEncoder().encode(exact).length === 200 && (await post(env, exact, "198.51.100.97")).status === 204, `${name}: 200 bytes exactly is accepted`);
    ok(db.dump() !== before && (await (await get(env)).json()).byCountry.ng["1"] === 2, `${name}: …and counted`);
    // méthodes et chemins
    r = await get(env, "/v"); ok(r.status === 405 && r.headers.get("allow") === "POST, OPTIONS", `${name}: GET /v → 405`);
    r = await worker.fetch(new Request(BASE + "/counts", { method: "POST", body: "{}" }), env); ok(r.status === 405, `${name}: POST /counts → 405`);
    r = await get(env, "/"); ok(r.status === 404, `${name}: / → 404`);
    r = await get(env, "/admin"); ok(r.status === 404, `${name}: unknown path → 404`);
    r = await worker.fetch(new Request(BASE + "/v", { method: "OPTIONS" }), env);
    ok(r.status === 204 && r.headers.get("access-control-allow-origin") === "*" && /POST/.test(r.headers.get("access-control-allow-methods")), `${name}: OPTIONS preflight`);
    // plafond de 10 par jour et par adresse
    const IP = "203.0.113.200";
    for (let i = 0; i < 10; i++) ok((await post(env, { c: "gh", l: 1 }, IP)).status === 204, `${name}: contribution ${i + 1}/10 from one address`);
    r = await post(env, { c: "gh", l: 1 }, IP);
    ok(r.status === 429 && r.headers.get("retry-after"), `${name}: the 11th from the same address → 429`);
    j = await (await get(env)).json();
    ok(j.byCountry.gh["1"] === 10, `${name}: …and it is not counted`);
    ok((await post(env, { c: "gh", l: 1 }, "203.0.113.201")).status === 204, `${name}: another address is not affected`);
    // l'adresse n'est jamais écrite en clair, ni dans une réponse
    ok(!db.dump().includes(IP) && !db.dump().includes("203.0.113") && !db.dump().includes("198.51.100") && !db.dump().includes("192.0.2."), `${name}: no raw IP address in the base`);
    ok(!(await (await get(env)).text()).includes(IP), `${name}: no address in the response`);
    // le lendemain : nouveau sel, plafond remis à zéro, anciennes empreintes supprimées après 48 h
    const hashes = rows("limits").filter(x => x.day === "2026-10-22").length;
    setDay("2026-10-23T09:00:00Z");
    ok((await post(env, { c: "gh", l: 1 }, IP)).status === 204, `${name}: next day the same address can contribute again`);
    const day2 = rows("limits").filter(x => x.day === "2026-10-23");
    ok(day2.length === 1 && !rows("limits").some(x => x.day === "2026-10-22" && x.h === day2[0].h), `${name}: the fingerprint changes every day (new salt)`);
    ok(rows("limits").filter(x => x.day === "2026-10-22").length === hashes, `${name}: yesterday's fingerprints are still there (48 h window)`);
    setDay("2026-10-24T09:00:00Z");
    ok((await post(env, { c: "gh", l: 1 }, "203.0.113.202")).status === 204, `${name}: day 3`);
    ok(!rows("limits").some(x => x.day === "2026-10-22"), `${name}: fingerprints older than 48 h are deleted`);
    ok(!rows("meta").some(x => x.k === "salt:2026-10-22") && rows("meta").some(x => x.k === "salt:2026-10-23") && rows("meta").some(x => x.k === "salt:2026-10-24"), `${name}: salts older than 48 h are deleted`);
    ok(rows("counts").length > 5, `${name}: the counters themselves are kept`);
    // rien n'est journalisé
    ok(logged.length === 0, `${name}: nothing is written to the console (${JSON.stringify(logged).slice(0, 80)})`);
    // panne de la base : 500, sans exception ni journal
    const broken = { DB: { prepare() { throw new Error("D1 is down: 203.0.113.7"); }, batch() { throw new Error("down"); } } };
    r = await post(broken, { c: "ng", l: 1 });
    ok(r.status === 500 && (await r.text()) === "", `${name}: database failure → 500 with an empty body`);
    r = await get(broken); ok(r.status === 500, `${name}: GET with the database down → 500`);
    ok(logged.length === 0, `${name}: …and still nothing logged`);
  } finally {
    for (const [k, o] of spies) console[k] = o;
  }
}

/* ---------- Liste des pays ---------- */
{
  const ctx = vm.createContext({});
  vm.runInContext(readFileSync(join(HERE, "..", "src", "africa.js"), "utf8") + "\n;this.__a = AFRICA;", ctx);
  const a2 = [...new Set([...Object.values(ctx.__a).map(c => c.a2.toLowerCase()), "fr"])].sort();
  eq(COUNTRIES, a2, "meter/countries.json is the list of src/africa.js plus France (run node tools/build.js to refresh)");
  ok(COUNTRIES.length >= 55 && COUNTRIES.every(c => /^[a-z]{2}$/.test(c)), "55 two-letter codes");
}
/* Toutes les instructions SQL du Worker sont connues de la fausse base */
{
  const found = [...src.matchAll(/prepare\(\s*"([^"]+)"\s*\)/g)].map(m => m[1]);
  const uniq = [...new Set(found)];
  ok(uniq.every(s => KIND[s]) && uniq.length === Object.keys(KNOWN).length, `every SQL statement of worker.js (${uniq.length}) is covered by the fake D1, and the fake has no unused one`);
  ok(!/console\.|await fetch\(|set-cookie|waitUntil|analytics/i.test(src.replace(/\/\*[\s\S]*?\*\//g, "")), "worker.js: no console, no outgoing call, no cookie, no analytics");
}

const fake = fakeD1();
await scenario("fake D1", fake, t => (t === "meta" ? [...fake.tables.meta].map(([k, v]) => ({ k, v })) : [...fake.tables[t].values()]));
const real = await sqliteD1();
if (real) { await scenario("SQLite", real, t => real.rows(t)); console.log("  (real SQLite with schema.sql: ok)"); }
else console.log("  (node:sqlite not available: real SQL not checked, only the fake D1)");

console.log(`meter worker: ${checks} checks passed`);
