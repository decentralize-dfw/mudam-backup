// French, German and Luxembourgish for the content modules. The packs in
// content/i18n/*.json follow the shape that scripts/i18n-source.mjs writes
// for English; each entry is attached next to `en` on its content object,
// so pick() finds it.
import fr from './i18n/fr.json';
import de from './i18n/de.json';
import lb from './i18n/lb.json';
import { BUILDING_HOTSPOTS } from './building.js';
import { SURROUNDING_HOTSPOTS } from './surroundings.js';
import { EXHIBITIONS, OTHER_ROOMS } from './exhibitions.js';

const FIELDS = ['subtitle', 'dates', 'place', 'credits', 'intro'];

for (const [lang, pack] of Object.entries({ fr, de, lb })) {
  for (const h of BUILDING_HOTSPOTS) if (pack.building?.[h.id]) h[lang] = pack.building[h.id];
  for (const h of SURROUNDING_HOTSPOTS) if (pack.surroundings?.[h.id]) h[lang] = pack.surroundings[h.id];
  for (const [id, room] of Object.entries(OTHER_ROOMS)) if (pack.other?.[id]) room[lang] = pack.other[id];
  for (const ex of EXHIBITIONS) {
    const p = pack.exhibitions?.[ex.id];
    if (!p) continue;
    for (const f of FIELDS) if (p[f] !== undefined && ex[f]) ex[f][lang] = p[f];
    for (const r of ex.rooms) if (p.rooms?.[r.id]) r[lang] = p.rooms[r.id];
  }
}
