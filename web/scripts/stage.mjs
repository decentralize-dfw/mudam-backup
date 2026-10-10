// Copy the Vite build into the repository root: index.html + demo/app/.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const web = path.resolve(here, '..');
const repo = path.resolve(web, '..');
const dist = path.join(web, 'dist');
const app = path.join(repo, 'demo/app');
fs.rmSync(app, { recursive: true, force: true });
fs.cpSync(path.join(dist, 'demo/app'), app, { recursive: true });
fs.copyFileSync(path.join(dist, 'index.html'), path.join(repo, 'index.html'));
console.log('staged index.html and demo/app/', fs.readdirSync(app).length, 'files');
