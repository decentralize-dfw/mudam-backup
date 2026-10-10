import fr from './content/i18n/fr.json';
import de from './content/i18n/de.json';
import lb from './content/i18n/lb.json';
import { STRINGS } from './strings.js';

// Offered languages; Turkish (tr) stays in strings.js but is not offered for now.
// French, German and Luxembourgish come from content/i18n/*.json.
export const LANGS = ['en', 'fr', 'de', 'lb'];
export const LANG_NAMES = { en: 'English', fr: 'Français', de: 'Deutsch', lb: 'Lëtzebuergesch' };
STRINGS.fr = fr.strings;
STRINGS.de = de.strings;
STRINGS.lb = lb.strings;

// The site opens in English unless a language was chosen.
let lang = 'en';
try {
  const asked = [new URLSearchParams(location.search).get('lang'), localStorage.getItem('mudam-lang')];
  lang = asked.find((l) => LANGS.includes(l)) ?? 'en';
} catch { /* storage off */ }

export const i18n = {
  get lang() { return lang; },
  set(next) {
    lang = LANGS.includes(next) ? next : 'en';
    try { localStorage.setItem('mudam-lang', lang); } catch { /* storage off */ }
    document.documentElement.lang = lang;
  },
};
export const t = (key) => STRINGS[lang]?.[key] ?? STRINGS.en[key] ?? key;
export const pick = (obj) => (obj ? obj[lang] ?? obj.en : '');
