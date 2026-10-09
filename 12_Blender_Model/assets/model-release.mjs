// Shared release resolver for every 3D viewer. No scene/version filename is baked in.
const manifestURL = new URL('../config/model_release.json', import.meta.url);
export async function latestModelRelease() {
  const response = await fetch(manifestURL, {cache:'no-store'});
  if (!response.ok) throw Error(`Güncel model kaydı: ${response.status}`);
  const release = await response.json();
  if (release.schema !== 1 || !/^[a-f0-9]{64}$/.test(release.sha256)) throw Error('Model kaydı geçersiz.');
  release.assetURL = new URL(release.url, manifestURL);
  release.assetURL.searchParams.set('v', release.sha256);
  return release;
}
export async function modelBytes(release, progress = () => {}) {
  const response = await fetch(release.assetURL, {cache:'no-store'});
  if (!response.ok) throw Error(`Model aktarımı: ${response.status}`);
  const reader = response.body.getReader(), chunks = [];
  let received = 0;
  for (;;) {
    const {value,done} = await reader.read();
    if (done) break;
    chunks.push(value); received += value.byteLength; progress(received);
  }
  let data = await new Blob(chunks).arrayBuffer();
  // Some hosts set Content-Encoding themselves; do not decompress twice.
  if (new Uint8Array(data)[0] === 0x1f && new Uint8Array(data)[1] === 0x8b) {
    data = await new Response(new Blob([data]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();
  }
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',data)), b=>b.toString(16).padStart(2,'0')).join('');
  if (data.byteLength !== release.size_bytes || hash !== release.sha256) throw Error('Yayın henüz eşleşmiyor; yeniden denenecek.');
  return data;
}
