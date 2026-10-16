import fs from 'node:fs';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {NodeIO,PropertyType,getBounds} from '@gltf-transform/core';
import {ALL_EXTENSIONS,EXTTextureWebP} from '@gltf-transform/extensions';
import {draco,mergeDocuments,unpartition,dedup,prune} from '@gltf-transform/functions';import draco3d from 'draco3dgltf';
const root='12_Blender_Model/',hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const receipt=JSON.parse(fs.readFileSync(root+'reports/R185_REOPEN_v003.json'));
const build=JSON.parse(fs.readFileSync(root+'reports/R185_ROAD9_v003.json'));
if(!receipt.reopened||receipt.objects.some(o=>o.degenerate||!o.finite)||build.reconstruction.some(r=>r.ground_misses))throw Error('Validation failed');
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule(),'draco3d.encoder':await draco3d.createEncoderModule()});
const base=fs.readFileSync('demo/model/cevre3/authored-district.glb');
if(hash(base)!=='9a19c1f34fa7c204dcc9a17954af4fd5f0fd98708eab124fd1e96847e50fb46e')throw Error('Production base changed');
const doc=await io.readBinary(base),add=await io.read(root+'exports/r152_clean/r185_road9_REVIEW.glb');
const count=d=>d.getRoot().listMeshes().reduce((s,m)=>s+m.listPrimitives().reduce((a,p)=>a+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0);
const removedDegenerates=[];
for(const m of doc.getRoot().listMeshes())for(const p of m.listPrimitives()){
 const pos=p.getAttribute('POSITION'),idx=p.getIndices();if(!idx)continue;const out=[];let removed=0;
 const a=[],b=[],c=[];
 for(let i=0;i<idx.getCount();i+=3){const ids=[idx.getScalar(i),idx.getScalar(i+1),idx.getScalar(i+2)];pos.getElement(ids[0],a);pos.getElement(ids[1],b);pos.getElement(ids[2],c);const u=b.map((v,j)=>v-a[j]),v=c.map((v,j)=>v-a[j]);const cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];if(cross.every(x=>x===0)){removed++;continue;}out.push(...ids);}
 if(removed){if(m.getName()!=='R182_EXTENSION_GROUND'||removed!==4)throw Error('Unexpected degenerate geometry '+m.getName()+' '+removed);p.setIndices(idx.clone().setArray(new Uint32Array(out)));removedDegenerates.push({mesh:m.getName(),zeroAreaTriangles:removed});}
}
const replaced=[];
for(const name of ['R161_ROAD_CONNECTIONS','R168_SOURCE_JUNCTION']){
 const nodes=doc.getRoot().listNodes().filter(n=>n.getName()===name);if(nodes.length!==1)throw Error('Expected one '+name);
 const n=nodes[0],m=n.getMesh();n.dispose();if(!doc.getRoot().listNodes().some(n=>n.getMesh()===m)){for(const p of m.listPrimitives())p.dispose();m.dispose();}replaced.push(name);
}
for(const texture of add.getRoot().listTextures()){
 const p=spawnSync('C:/Users/yigit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['-c','import sys,io;from PIL import Image;im=Image.open(io.BytesIO(sys.stdin.buffer.read()));im.save(sys.stdout.buffer,format="WEBP",quality=92,method=6)'],{input:Buffer.from(texture.getImage()),maxBuffer:64*1024*1024});if(p.status)throw Error(p.stderr.toString());texture.setImage(p.stdout).setMimeType('image/webp');
}
add.createExtension(EXTTextureWebP).setRequired(true);let expected=count(doc)+count(add);const scene=doc.getRoot().listScenes()[0],map=mergeDocuments(doc,add);
for(const s of add.getRoot().listScenes()){const m=map.get(s);for(const n of [...m.listChildren()])scene.addChild(n);m.dispose();}
const backgroundReceipt=JSON.parse(fs.readFileSync(root+'reports/R188_EXPORT_REOPEN.json'));
if(!backgroundReceipt.reopened||backgroundReceipt.degenerate||backgroundReceipt.buildings.length!==7)throw Error('Background verification failed');
const bg=await io.read(root+'exports/r152_clean/r188_background_REVIEW.glb');expected+=count(bg);const bgmap=mergeDocuments(doc,bg);
for(const s of bg.getRoot().listScenes()){const mapped=bgmap.get(s);for(const n of [...mapped.listChildren()])scene.addChild(n);mapped.dispose();}
await doc.transform(prune({propertyTypes:[PropertyType.MATERIAL,PropertyType.TEXTURE,PropertyType.ACCESSOR,PropertyType.BUFFER],keepAttributes:true,keepLeaves:true,keepSolidTextures:true}),dedup({propertyTypes:[PropertyType.TEXTURE]}),unpartition(),draco({method:'edgebreaker',quantizePosition:24,quantizeNormal:14,quantizeTexcoord:18}));
const bytes=await io.writeBinary(doc),check=await io.readBinary(bytes);if(count(check)!==expected){const stats=d=>d.getRoot().listMeshes().map(m=>({name:m.getName(),triangles:m.listPrimitives().reduce((a,p)=>a+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0)}));fs.writeFileSync(root+'reports/R185_DRACO_COUNT_DIAGNOSTIC.json',JSON.stringify({before:stats(doc),after:stats(check)},null,2));throw Error('Triangle count drift '+expected+' -> '+count(check));}
for(const name of replaced)if(check.getRoot().listNodes().filter(n=>n.getName()===name).length!==1)throw Error('Duplicated road');
const out=root+'exports/r152_clean/r185_r188_district_draco_webp_REVIEW.glb';fs.writeFileSync(out,bytes);
const report={acceptedForPublication:false,scope:'Region9 overhang replacement and7 source-footprint simple outside-scan masses; full11regions not complete',baseSha256:hash(base),sha256:hash(bytes),bytes:bytes.length,triangles:expected,replaced,removedDegenerates,bounds:getBounds(check.getRoot().listScenes()[0]),compressedDecodePassed:true,limitations:build.limits};fs.writeFileSync(root+'reports/R185_R188_COMPRESSED_CANDIDATE.json',JSON.stringify(report,null,2));console.log(report);
