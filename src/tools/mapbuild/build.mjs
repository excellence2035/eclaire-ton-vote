import fs from 'fs';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const topo0 = require('world-atlas/countries-50m.json');
import * as tc from 'topojson-client';
import * as ts from 'topojson-simplify';
import * as d3 from 'd3-geo';

const AFR = ['012','024','204','072','854','108','132','120','140','148','174','178','180','384','262','818','226','232','748','231','266','270','288','324','624','404','426','430','434','450','454','466','478','480','504','508','516','562','566','646','678','686','690','694','706','710','728','729','834','768','788','800','894','716','732'];
const NEIGH = ['724','620','380','300','792','196','760','422','376','275','400','682','887','512','784','634','048','414','368','364','250','470'];
const q = parseFloat(process.argv[2] || '0.35');
let topo = ts.presimplify(JSON.parse(JSON.stringify(topo0)), ts.sphericalTriangleArea);
topo = ts.simplify(topo, ts.quantile(topo, q));
const geoms = topo.objects.countries.geometries;
const byId = id => geoms.find(g => g.id === id);
const feats = {};
for (const id of AFR) {
  let geom = byId(id);
  if (id === '706') {
    const sl = geoms.find(g => g.properties.name === 'Somaliland');
    feats[id] = { type: 'Feature', id, geometry: tc.merge(topo, [geom, sl]) };
  } else feats[id] = tc.feature(topo, geom);
}
function trim(f) {
  const g = f.geometry;
  if (!g || g.type !== 'MultiPolygon') return f;
  const keep = g.coordinates.filter(poly => {
    const ring = poly[0];
    const maxLat = Math.max(...ring.map(c => c[1])), minLon = Math.min(...ring.map(c => c[0]));
    return !(maxLat < -36 || minLon > 60);
  });
  return { ...f, geometry: { type: 'MultiPolygon', coordinates: keep } };
}
for (const id of Object.keys(feats)) feats[id] = trim(feats[id]);
const islands = { '132': [-23.6, 15.1], '678': [6.6, 0.25], '174': [43.35, -11.7], '480': [57.55, -20.25], '690': [55.45, -4.62] };
const W = 800, H = 770;
const fitColl = { type: 'FeatureCollection', features: [...Object.values(feats), ...Object.entries(islands).map(([id, c]) => ({ type: 'Feature', geometry: { type: 'Point', coordinates: c } }))] };
const proj = d3.geoAzimuthalEqualArea().rotate([-17, -2]).fitExtent([[14, 14], [W - 14, H - 14]], fitColl);
proj.clipExtent([[0, 0], [W, H]]);
const path = d3.geoPath(proj).digits(1);
const bb = path.bounds(fitColl);
const pad = 16;
const out = { w: W, h: H, vb: [Math.floor(bb[0][0]-pad), Math.floor(bb[0][1]-pad), Math.ceil(bb[1][0]-bb[0][0]+2*pad), Math.ceil(bb[1][1]-bb[0][1]+2*pad)], c: {}, cent: {}, isl: {}, nb: '' };
for (const [id, f] of Object.entries(feats)) {
  out.c[id] = path(f) || '';
  const ct = path.centroid(f); out.cent[id] = [Math.round(ct[0]), Math.round(ct[1])];
}
for (const [id, c] of Object.entries(islands)) { const p = proj(c); out.isl[id] = [Math.round(p[0]), Math.round(p[1])]; }
const nb = NEIGH.map(byId).filter(Boolean);
out.nb = path(tc.merge(topo, nb)) || '';
const s = JSON.stringify(out);
fs.writeFileSync('../africa-map.json', s);
console.log('q', q, 'bytes', s.length, 'nb', out.nb.length);
const small = Object.entries(out.c).filter(([id, d]) => d.length < 120).map(([id]) => id);
console.log('tiny paths', small.join(','));
