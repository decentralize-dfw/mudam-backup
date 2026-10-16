import fs from 'node:fs';
import crypto from 'node:crypto';
import {NodeIO,getBounds} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {draco,mergeDocuments,unpartition} from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
const root=process.cwd();
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule(),'draco3d.encoder':await draco3d.createEncoderModule()});
const src='12_Blender_Model/exports/r152_clean/r169_architectural_v088_REVIEW.glb';
const target='demo/model/cevre3/authored-district.glb';
const doc=await io.read(target), row=await io.read(src);
const tris=d=>d.getRoot().listMeshes().reduce((s,m)=>s+m.listPrimitives().reduce((n,p)=>n+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0);
const expected=tris(doc)+tris(row);
const originalScene=doc.getRoot().listScenes()[0];
const map=mergeDocuments(doc,row);
for(const s of row.getRoot().listScenes()) {const added=map.get(s);for(const child of [...added.listChildren()]) originalScene.addChild(child);added.dispose();}
await doc.transform(unpartition(),draco({method:'edgebreaker',quantizePosition:24,quantizeNormal:14,quantizeTexcoord:18}));
const bytes=await io.writeBinary(doc), check=await io.readBinary(bytes);
if(tris(check)!==expected||check.getRoot().listScenes().length!==1)throw Error('Merged model validation failed');
const hash=crypto.createHash('sha256').update(bytes).digest('hex');
const manifest=JSON.parse(fs.readFileSync('demo/data/cevre3.json','utf8'));
manifest.revision='R170-plus-R169-v088-user-review';
manifest.source='Authored R170 context plus independently modeled R169 v088 four-house row, published for user review. Shell sampling passed; rear dormers, balcony, chimneys and material detailing remain incomplete. No full source-fidelity acceptance.';
Object.assign(manifest.files.district,{bytes:bytes.length,sha256:hash,triangles:expected,sourceTriangles:expected,bounds:getBounds(check.getRoot().listScenes()[0]),sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(src)).digest('hex')});
fs.writeFileSync(target,bytes);
fs.writeFileSync('demo/data/cevre3.json',JSON.stringify(manifest,null,2)+'\n');
const report={revision:manifest.revision,dateUTC:new Date().toISOString(),rowSource:src,rowTriangles:tris(row),districtTriangles:expected,districtBytes:bytes.length,sha256:hash,status:'User-requested review publication; incomplete architecture, not final acceptance',validation:'Merged GLB decoded successfully; one scene; triangle count preserved',textures:check.getRoot().listTextures().map(t=>t.getMimeType())};
fs.writeFileSync('12_Blender_Model/reports/R169_v088_PUBLICATION.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

