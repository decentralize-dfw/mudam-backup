import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { NodeIO, getBounds } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTTextureWebP } from '@gltf-transform/extensions';
import { draco } from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import { spawnSync } from 'node:child_process';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const python = process.env.PYTHON || 'python';
const cache = path.join(repo,'12_Blender_Model/.local_source_cache/context3-webp');
fs.mkdirSync(cache,{recursive:true});
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(),
  'draco3d.encoder': await draco3d.createEncoderModule(),
});
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
function stats(doc) {
  const r = doc.getRoot();
  let degenerate=0;
  for(const m of r.listMeshes()) for(const p of m.listPrimitives()) {
    const pos=p.getAttribute('POSITION'), idx=p.getIndices();
    const count=idx?.getCount()??pos.getCount();
    for(let i=0;i<count;i+=3) {
      const a=pos.getElement(idx?idx.getScalar(i):i,[]),b=pos.getElement(idx?idx.getScalar(i+1):i+1,[]),c=pos.getElement(idx?idx.getScalar(i+2):i+2,[]);
      const u=b.map((x,j)=>x-a[j]),v=c.map((x,j)=>x-a[j]);
      if(Math.hypot(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])<1e-12) degenerate++;
    }
  }
  return { degenerate, triangles: r.listMeshes().reduce((s,m)=>s+m.listPrimitives().reduce((n,p)=>n+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0),
    bounds: getBounds(r.getDefaultScene()??r.listScenes()[0]),
    textures: r.listTextures().map(t=>({size:t.getSize(),mime:t.getMimeType()})) };
}
const manifest = { name:'Context 3', revision:'R160-draco-webp', source:'ACT 2020, CC0; museum footprint removed in R151. Source geometry retained without simplification.', compression:'Draco 24-bit positions; WebP quality 92; original texture resolution', files:{} };
fs.mkdirSync(path.join(repo,'demo/model/cevre3'),{recursive:true});
for (const key of ['near','far']) {
  const source = zlib.gunzipSync(fs.readFileSync(path.join(repo,`12_Blender_Model/exports/web_current/${key}_context.glb.gz`)));
  const doc = await io.readBinary(source);
  const before = stats(doc);
  // Preserve mesh instances, topology and material assignments.
  const missing=[];
  for(const texture of doc.getRoot().listTextures()) {
    const base=path.join(cache,sha(texture.getImage()));
    if(!fs.existsSync(base+'-q92.webp')) { fs.writeFileSync(base+'.source',texture.getImage()); missing.push(base); }
  }
  if(missing.length) {
    const result=spawnSync(python,['-c','import sys,json; from PIL import Image; from concurrent.futures import ThreadPoolExecutor\ndef convert(base):\n im=Image.open(base+".source"); im.save(base+"-q92.webp",format="WEBP",quality=92,method=4)\nwith ThreadPoolExecutor(max_workers=8) as pool: list(pool.map(convert,json.load(sys.stdin)))'],{input:JSON.stringify(missing),maxBuffer:1024*1024});
    if(result.status!==0) throw Error(result.stderr?.toString()||'Texture conversion failed');
  }
  for (const texture of doc.getRoot().listTextures()) {
    const cached = path.join(cache,sha(texture.getImage())+'-q92.webp');
    const result = fs.existsSync(cached) ? {status:0,stdout:fs.readFileSync(cached)} : spawnSync(python, ['-c', 'import sys,io; from PIL import Image; im=Image.open(io.BytesIO(sys.stdin.buffer.read())); im.save(sys.stdout.buffer,format="WEBP",quality=92,method=4)'], {input:Buffer.from(texture.getImage()),maxBuffer:64*1024*1024});
    if(result.status!==0) throw Error(result.stderr.toString());
    const bytes = result.stdout;
    fs.writeFileSync(cached,bytes);
    texture.setImage(bytes).setMimeType('image/webp');
  }
  doc.createExtension(EXTTextureWebP).setRequired(true);
  await doc.transform(draco({method:'edgebreaker',quantizePosition:24,quantizeNormal:14,quantizeTexcoord:18}));
  const output = await io.writeBinary(doc);
  const reopened = await io.readBinary(output);
  const after = stats(reopened);
  console.log(key,'triangle verification',before.triangles,before.degenerate,after.triangles,after.degenerate);
  if (before.triangles-before.degenerate!==after.triangles-after.degenerate) throw Error(`${key}: nondegenerate triangle count changed`);
  if (after.textures.some(t=>t.mime!=='image/webp')) throw Error('Non-WebP texture');
  const error = Math.max(...['min','max'].flatMap(k=>before.bounds[k].map((v,i)=>Math.abs(v-after.bounds[k][i]))));
  if(error>0.02) throw Error(`${key}: bounds drift ${error}`);
  const file = `model/cevre3/${key}.glb`;
  fs.writeFileSync(path.join(repo,'demo',file),output);
  manifest.files[key]={file,bytes:output.length,sha256:sha(output),sourceSha256:sha(source),triangles:after.triangles,sourceTriangles:before.triangles,degenerateRemoved:before.triangles-after.triangles,bounds:after.bounds,boundsError:error,textures:after.textures.length};
  console.log(key,manifest.files[key]);
}
fs.writeFileSync(path.join(repo,'demo/data/cevre3.json'),JSON.stringify(manifest,null,2)+'\n');
