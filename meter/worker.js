/* Compteur collectif : Cloudflare Worker + base D1.
 *
 *   POST /v       corps {"c":"ng","l":1}  (c = code pays, l = niveau -2..2)  ->  204, ou 400 / 405 / 413 / 429
 *   GET  /counts  {updated, total:{"-2":n,...}, byCountry:{ng:{...}}}        ->  200, Cache-Control: public, max-age=60
 *
 * Ce qui est enregistré : un compteur par (pays, niveau) et, pour limiter les abus, un compteur par (empreinte, jour) où
 * l'empreinte est SHA-256(sel du jour + adresse IP), tronquée. L'adresse IP n'est jamais écrite en clair, ni en base ni dans
 * un journal ; le sel du jour est tiré au hasard et gardé en base ; empreintes et sels de plus de 48 h sont supprimés.
 * Aucun cookie, aucun outil de mesure d'audience, aucun journal du contenu des requêtes (voir meter/README.md).
 */
import COUNTRIES from "./countries.json";

const LEVELS = [-2, -1, 0, 1, 2];
const MAX_BODY = 200;      // octets
const MAX_PER_DAY = 10;    // contributions par empreinte et par jour (UTC)
const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "86400" };
const COUNTRY_SET = new Set(COUNTRIES);

const reply = (status, body, extra) => new Response(body === undefined ? null : body, { status, headers: { ...CORS, ...(extra || {}) } });
const hex = bytes => [...new Uint8Array(bytes)].map(b => b.toString(16).padStart(2, "0")).join("");
const today = () => new Date().toISOString().slice(0, 10);
const dayBefore = day => new Date(Date.parse(day + "T00:00:00Z") - 86400000).toISOString().slice(0, 10);

/* Lit le corps de la requête en s'arrêtant dès qu'il dépasse la limite (null = trop long). */
async function readCapped(request, max) {
  const declared = Number(request.headers.get("content-length"));
  if (declared > max) return null;
  if (!request.body) return "";
  const reader = request.body.getReader();
  const chunks = [];
  let n = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    n += value.byteLength;
    if (n > max) { try { await reader.cancel(); } catch (e) { /* ignoré */ } return null; }
    chunks.push(value);
  }
  const all = new Uint8Array(n);
  let off = 0;
  for (const c of chunks) { all.set(c, off); off += c.byteLength; }
  return new TextDecoder().decode(all);
}

/* {"c": pays connu, "l": entier de -2 à 2} et rien d'autre, sinon null. */
function parse(text) {
  let j;
  try { j = JSON.parse(text); } catch (e) { return null; }
  if (!j || typeof j !== "object" || Array.isArray(j)) return null;
  const keys = Object.keys(j);
  if (keys.length !== 2 || !keys.includes("c") || !keys.includes("l")) return null;
  if (typeof j.c !== "string" || !COUNTRY_SET.has(j.c)) return null;
  if (typeof j.l !== "number" || !Number.isInteger(j.l) || j.l < -2 || j.l > 2) return null;
  return { c: j.c, l: j.l + 0 };
}

/* Sel du jour : tiré au hasard à la première contribution du jour, gardé en base ; les données de plus de 48 h sont supprimées. */
async function daySalt(db, day) {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  const fresh = await db.prepare("INSERT OR IGNORE INTO meta (k, v) VALUES (?1, ?2)").bind("salt:" + day, hex(bytes)).run();
  if (fresh && fresh.meta && fresh.meta.changes) {
    const keep = dayBefore(day);
    await db.prepare("DELETE FROM limits WHERE day < ?1").bind(keep).run();
    await db.prepare("DELETE FROM meta WHERE k LIKE 'salt:%' AND k < ?1").bind("salt:" + keep).run();
  }
  const row = await db.prepare("SELECT v FROM meta WHERE k = ?1").bind("salt:" + day).first();
  return row.v;
}

async function contribute(request, db) {
  const text = await readCapped(request, MAX_BODY);
  if (text === null) return reply(413, undefined, { "Cache-Control": "no-store" });
  const v = parse(text);
  if (!v) return reply(400, undefined, { "Cache-Control": "no-store" });
  const day = today();
  const ip = request.headers.get("CF-Connecting-IP") || "local";
  const salt = await daySalt(db, day);
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(salt + "|" + ip));
  const h = hex(digest).slice(0, 32);
  // Une seule instruction, atomique : la ligne n'est créée ou augmentée que si le plafond n'est pas atteint
  const slot = await db.prepare("INSERT INTO limits (h, day, n) VALUES (?1, ?2, 1) ON CONFLICT (h, day) DO UPDATE SET n = n + 1 WHERE n < ?3 RETURNING n")
    .bind(h, day, MAX_PER_DAY).first();
  if (!slot) return reply(429, undefined, { "Cache-Control": "no-store", "Retry-After": "86400" });
  await db.batch([
    db.prepare("INSERT INTO counts (country, level, n) VALUES (?1, ?2, 1) ON CONFLICT (country, level) DO UPDATE SET n = n + 1").bind(v.c, v.l),
    db.prepare("INSERT INTO meta (k, v) VALUES ('updated', ?1) ON CONFLICT (k) DO UPDATE SET v = excluded.v").bind(new Date().toISOString().slice(0, 19) + "Z"),
  ]);
  return reply(204, undefined, { "Cache-Control": "no-store" });
}

async function counts(db) {
  const zero = () => ({ "-2": 0, "-1": 0, "0": 0, "1": 0, "2": 0 });
  const total = zero(), by = {};
  const rows = ((await db.prepare("SELECT country, level, n FROM counts").all()).results) || [];
  for (const r of rows) {
    if (!LEVELS.includes(r.level) || !COUNTRY_SET.has(r.country) || !(r.n > 0)) continue;
    total[r.level] += r.n;
    if (!by[r.country]) by[r.country] = zero();
    by[r.country][r.level] = r.n;
  }
  const up = await db.prepare("SELECT v FROM meta WHERE k = ?1").bind("updated").first();
  return reply(200, JSON.stringify({ updated: up ? up.v : "", total, byCountry: by }), { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "public, max-age=60" });
}

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    try {
      if (request.method === "OPTIONS") return reply(204);
      if (path === "/v") return request.method === "POST" ? await contribute(request, env.DB) : reply(405, undefined, { Allow: "POST, OPTIONS" });
      if (path === "/counts") return request.method === "GET" ? await counts(env.DB) : reply(405, undefined, { Allow: "GET, OPTIONS" });
      return reply(404);
    } catch (e) {
      return reply(500, undefined, { "Cache-Control": "no-store" });   // rien n'est journalisé : ni le contenu, ni l'adresse
    }
  },
};
