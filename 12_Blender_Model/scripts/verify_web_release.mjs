import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {modelBytes,latestModelRelease} from '../assets/model-release.mjs';
const realFetch=globalThis.fetch;
globalThis.fetch=async url=>new Response(await readFile(new URL(url)));
const release=await latestModelRelease();
const raw=await modelBytes(release);
assert.equal(new TextDecoder().decode(raw.slice(0,4)),'glTF');
await assert.rejects(modelBytes({...release,sha256:'0'.repeat(64)}),/eşleşmiyor/);
// A host which already decodes Content-Encoding must also work.
globalThis.fetch=async()=>new Response(raw);
assert.equal((await modelBytes(release)).byteLength,release.size_bytes);
globalThis.fetch=async()=>new Response('Not found',{status:404});
await assert.rejects(modelBytes(release),/404/);
globalThis.fetch=realFetch;
console.log(`${release.revision}: gzip, decoded HTTP, SHA mismatch and missing asset checks passed`);
