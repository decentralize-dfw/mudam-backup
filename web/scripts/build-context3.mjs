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
import { MeshoptDecoder } from 'meshoptimizer';

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const python = process.env.PYTHON || 'python';
const cache = path.join(repo,'12_Blender_Model/.local_source_cache/context3-webp');
fs.mkdirSync(cache,{recursive:true});
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.decoder': MeshoptDecoder,
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
  const instances=r.listNodes().flatMap(n=> {const e=n.getExtension('EXT_mesh_gpu_instancing');return e?e.listSemantics().map(s=>({semantic:s,count:e.getAttribute(s).getCount(),hash:sha(new Uint8Array(e.getAttribute(s).getArray().buffer))})):[];});
  return { instances, degenerate, triangles: r.listMeshes().reduce((s,m)=>s+m.listPrimitives().reduce((n,p)=>n+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0),
    bounds: getBounds(r.getDefaultScene()??r.listScenes()[0]),
    textures: r.listTextures().map(t=>({size:t.getSize(),mime:t.getMimeType()})) };
}
const candidate = process.argv.includes('--r162-candidate');
const roadRelease = process.argv.includes('--r168-roads');
const southRelease = process.argv.includes('--r167-buildings');
const eastRelease = process.argv.includes('--r166-buildings');
const buildingRelease = roadRelease || southRelease || eastRelease || process.argv.includes('--r165-buildings');
const surfaceRelease = process.argv.includes('--r163-surface');
const outputDir=candidate?'demo/model/r162-review':'demo/model/cevre3';
const manifest = { name:'Context 3', revision:'R161-authored-draco-webp', source:'Authored environment: R159 terrain and vegetation, Philharmonie, Melia, Schuman; R161 WKI, Thomas More and road connections. Not ACT photogrammetry.', compression:'Draco 24-bit positions; WebP quality 92; original texture resolution', files:{} };
if(buildingRelease) Object.assign(manifest,{revision:'R165-seven-source-derived-buildings',source:'Authored environment with seven source-derived building envelopes: roof steps, courtyard boundaries and a measured sloping tower roof. ACT facade color projected onto authored geometry. Fine facade recesses, remaining district buildings, roads and vegetation are incomplete.'});
if(eastRelease) Object.assign(manifest,{revision:'R166-eastern-complex-and-curved-roof',source:'Authored source-derived buildings including eastern triangular complex and its tower, curved glass-roof building, seven earlier envelopes. Roof levels and facade colors follow ACT reference. Manual outer traces and fine facade relief remain approximate; roads and vegetation incomplete.'});
if(southRelease) Object.assign(manifest,{revision:'R167-southern-roof-rows',source:'Authored source-derived environment: R166 buildings plus ten southern houses with sampled pitched roofs and source facade color. OSM party-wall footprint gaps corrected. Fine facade relief, occluded source regions, roads and vegetation remain incomplete.'});
if(roadRelease) Object.assign(manifest,{revision:'R168-source-registered-boulevard',source:'R167 authored buildings plus terrain-conforming source-registered main boulevard and two northern approaches. Road markings and sidewalks are source color, not separately reconstructed kerbs. Manual outlines and source coverage limit accuracy; vegetation and remaining roads incomplete.'});
if(surfaceRelease) Object.assign(manifest,{revision:'R163-authored-source-surface',source:'Authored environment with ACT registered overhead surface colors on retained terrain; R161 buildings and R159 vegetation remain approximate.'});
if(candidate) Object.assign(manifest,{name:'R162 review candidate',revision:'R162-v002-review-only',source:'Authored roof segmentation and facade projection from ACT reference; incomplete, not accepted as full context.',accepted:false});
fs.mkdirSync(path.join(repo,outputDir),{recursive:true});
for (const [key,sourceName] of (candidate ? [['candidate','r162_measured_candidate']] : [['near','near_site'],['far','philharmonie'],['melia','melia'],['schuman','schuman'],['vegetation','vegetation'],['district','r161_additions']])) {
  const buildingFile=buildingRelease && key==='district' ? (roadRelease?'r168_district':southRelease?'r167_district':eastRelease?'r166_district':'r165_district') : null;
  const surfaceFile=surfaceRelease && (key==='near'||key==='district') ? `r163_${key}` : null;
  const source = buildingFile ? fs.readFileSync(path.join(repo,`12_Blender_Model/exports/r152_clean/${buildingFile}.glb`)) : surfaceFile ? fs.readFileSync(path.join(repo,`12_Blender_Model/exports/r152_clean/${surfaceFile}.glb`)) : candidate ? fs.readFileSync(path.join(repo,'12_Blender_Model/exports/r152_clean/r162_measured_candidate.glb')) : key==='district' ? fs.readFileSync(path.join(repo,'12_Blender_Model/exports/r152_clean/r161_additions.glb')) : zlib.gunzipSync(fs.readFileSync(path.join(repo,`12_Blender_Model/exports/r152_clean/${sourceName}_web.glb.gz`)));
  const doc = await io.readBinary(source);
  const before = stats(doc);
  doc.getRoot().listExtensionsUsed().filter(e=>e.extensionName==='EXT_meshopt_compression').forEach(e=>e.dispose());
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
  if(JSON.stringify(before.instances)!==JSON.stringify(after.instances)) throw Error('Instance transforms changed');
  console.log(key,'triangle verification',before.triangles,before.degenerate,after.triangles,after.degenerate);
  if (before.triangles-before.degenerate!==after.triangles-after.degenerate) throw Error(`${key}: nondegenerate triangle count changed`);
  if (after.textures.some(t=>t.mime!=='image/webp')) throw Error('Non-WebP texture');
  const error = Math.max(...['min','max'].flatMap(k=>before.bounds[k].map((v,i)=>Math.abs(v-after.bounds[k][i]))));
  if(error>0.02) throw Error(`${key}: bounds drift ${error}`);
  const file = candidate ? 'model/r162-review/measured-buildings.glb' : `model/cevre3/authored-${key}.glb`;
  fs.writeFileSync(path.join(repo,'demo',file),output);
  manifest.files[key]={file,bytes:output.length,sha256:sha(output),sourceSha256:sha(source),triangles:after.triangles,sourceTriangles:before.triangles,degenerateRemoved:before.triangles-after.triangles,bounds:after.bounds,boundsError:error,textures:after.textures.length,instanceTransformsPreserved:true,instances:after.instances};
  console.log(key,manifest.files[key]);
}
fs.writeFileSync(path.join(repo,candidate?'demo/data/r162-review.json':'demo/data/cevre3.json'),JSON.stringify(manifest,null,2)+'\n');
