import fs from 'node:fs';
import crypto from 'node:crypto';
import {NodeIO,getBounds} from '@gltf-transform/core';
import {ALL_EXTENSIONS,EXTTextureWebP} from '@gltf-transform/extensions';
import {draco,mergeDocuments,unpartition} from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import {spawnSync} from 'node:child_process';
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule(),'draco3d.encoder':await draco3d.createEncoderModule()});
const target='demo/model/cevre3/authored-district.glb',base='12_Blender_Model/.local_source_cache/r182/published_district_base.glb';
fs.mkdirSync('12_Blender_Model/.local_source_cache/r182',{recursive:true});
if(!fs.existsSync(base)) {
 if(hash(fs.readFileSync(target))!=='f296ed5cc4f918669d1ece3f213eaf20108e634136b81b2b253764b764e384d5')throw Error('Unexpected production base; refusing duplicate append');
 fs.copyFileSync(target,base);
}
const receipt=JSON.parse(fs.readFileSync('12_Blender_Model/reports/R182_REOPEN_v003.json','utf8'));
if(!receipt.glb_reopened||receipt.degenerate||receipt.buildings.length!==134||receipt.maximum_footprint_error>.001)throw Error('Missing source/geometry validation');
const doc=await io.read(base),addition=await io.read('12_Blender_Model/exports/r152_clean/r182_district_terrain_REVIEW.glb');
const count=d=>d.getRoot().listMeshes().reduce((s,m)=>s+m.listPrimitives().reduce((n,p)=>n+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0);
const expected=count(doc)+count(addition),sourceBounds=getBounds(addition.getRoot().listScenes()[0]);
for(const texture of addition.getRoot().listTextures()){
 const result=spawnSync('C:/Users/yigit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['-c','import sys,io;from PIL import Image;im=Image.open(io.BytesIO(sys.stdin.buffer.read()));im.save(sys.stdout.buffer,format="WEBP",quality=92,method=6)'],{input:Buffer.from(texture.getImage()),maxBuffer:64*1024*1024});
 if(result.status!==0)throw Error(result.stderr.toString());texture.setImage(result.stdout).setMimeType('image/webp');
}
addition.createExtension(EXTTextureWebP).setRequired(true);
const scene=doc.getRoot().listScenes()[0],map=mergeDocuments(doc,addition);
for(const s of addition.getRoot().listScenes()){const merged=map.get(s);for(const n of [...merged.listChildren()])scene.addChild(n);merged.dispose();}
await doc.transform(unpartition(),draco({method:'edgebreaker',quantizePosition:24,quantizeNormal:14,quantizeTexcoord:18}));
const bytes=await io.writeBinary(doc),check=await io.readBinary(bytes);
if(count(check)!==expected||check.getRoot().listScenes().length!==1)throw Error('Compressed decode failed');
const manifest=JSON.parse(fs.readFileSync('demo/data/cevre3.json','utf8'));
manifest.revision='R182-lower-district-footprints-review';
manifest.source='Existing Context3 including R169 v088 preserved. Added134 independently modeled abstract lower-district masses on OSM footprints,10 mapped hardscape polygons and ACT LiDAR terrain extension. Untagged heights are explicit8m abstract assumptions. Fort, northern facade fidelity and remaining11-region work are not accepted as complete.';
Object.assign(manifest.files.district,{bytes:bytes.length,sha256:hash(bytes),triangles:expected,sourceTriangles:expected,bounds:getBounds(check.getRoot().listScenes()[0]),sourceSha256:hash(fs.readFileSync('12_Blender_Model/exports/r152_clean/r182_district_terrain_REVIEW.glb'))});
fs.writeFileSync(target,bytes);fs.writeFileSync('demo/data/cevre3.json',JSON.stringify(manifest,null,2)+'\n');
const report={revision:manifest.revision,dateUTC:new Date().toISOString(),bytes:bytes.length,triangles:expected,addedTriangles:receipt.triangles,buildings:134,maximumFootprintError:receipt.maximum_footprint_error,sha256:hash(bytes),sourceBounds,textures:check.getRoot().listTextures().map(t=>t.getMimeType()),scopeAcceptance:'User-authorized abstract footprint massing and terrain extension only; not full11-region completion',excludedCandidates:['R172/R181 fort','R175 viaduct','R176 northern architecture','R177 road replacement','R178/R180 station','R179 background masses']};
fs.writeFileSync('12_Blender_Model/reports/R182_PUBLICATION.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
