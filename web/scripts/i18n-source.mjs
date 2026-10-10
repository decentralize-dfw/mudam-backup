// English source for the translations: writes src/content/i18n/en.source.json
// (interface strings and every text of the content modules, keyed by id) and
// lists what each language pack still lacks.
//   node scripts/i18n-source.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { STRINGS } from '../src/strings.js';
import { BUILDING_HOTSPOTS } from '../src/content/building.js';
import { SURROUNDING_HOTSPOTS } from '../src/content/surroundings.js';
import { EXHIBITIONS, OTHER_ROOMS } from '../src/content/exhibitions.js';

const dir = path.join(path.dirname(fileURLToPath(import.meta.url)), '../src/content/i18n');
const byId = (list) => Object.fromEntries(list.map((h) => [h.id, h.en]));
const source = {
  strings: STRINGS.en,
  building: byId(BUILDING_HOTSPOTS),
  surroundings: byId(SURROUNDING_HOTSPOTS),
  exhibitions: Object.fromEntries(EXHIBITIONS.map((ex) => [ex.id, {
    subtitle: ex.subtitle.en, dates: ex.dates.en, place: ex.place.en, credits: ex.credits.en, intro: ex.intro.en,
    ...(ex.next ? { next: ex.next.en } : {}),
    rooms: Object.fromEntries(ex.rooms.map((r) => [r.id, r.en])),
  }])),
  other: Object.fromEntries(Object.entries(OTHER_ROOMS).map(([id, r]) => [id, r.en])),
};
fs.writeFileSync(path.join(dir, 'en.source.json'), JSON.stringify(source, null, 1) + '\n');

// every leaf path of the source must exist in each pack, with the same shape
const leaves = (o, p = []) => (typeof o === 'object' && o !== null ? Object.entries(o).flatMap(([k, v]) => leaves(v, [...p, k])) : [p.join('.')]);
const want = leaves(source);
for (const lang of ['fr', 'de', 'lb']) {
  const file = path.join(dir, `${lang}.json`);
  const pack = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
  const have = new Set(leaves(pack));
  const missing = want.filter((k) => !have.has(k));
  const extra = [...have].filter((k) => !want.includes(k));
  console.log(`${lang}: ${want.length - missing.length}/${want.length}${missing.length ? `, missing ${missing.slice(0, 8).join(', ')}${missing.length > 8 ? ' …' : ''}` : ''}${extra.length ? `, extra ${extra.slice(0, 5).join(', ')}` : ''}`);
}
