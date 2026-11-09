import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {NodeIO,getBounds} from '@gltf-transform/core';
import {ALL_EXTENSIONS,EXTTextureWebP} from '@gltf-transform/extensions';
import {draco} from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
import {spawnSync} from 'node:child_process';
const root=path.resolve(import.meta.dirname,'../..');
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule(),'draco3d.encoder':await draco3d.createEncoderModule()});
const source=path.join(root,'12_Blender_Model/exports/r152_clean/r169_geometry_review_v073.glb');const doc=await io.read(source);
const stats=d=>({triangles:d.getRoot().listMeshes().reduce((a,m)=>a+m.listPrimitives().reduce((a,p)=>a+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0),bounds:getBounds(d.getRoot().listScenes()[0]),textures:d.getRoot().listTextures().map(t=>({size:t.getSize(),mime:t.getMimeType()}))});
const before=stats(doc);const python='C:/Users/yigit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
for(const t of doc.getRoot().listTextures()){
 const r=spawnSync(python,['-c','import sys,io;from PIL import Image; im=Image.open(io.BytesIO(sys.stdin.buffer.read()));im.save(sys.stdout.buffer,format="WEBP",quality=92,method=6)'],{input:Buffer.from(t.getImage()),maxBuffer:32*1024*1024});if(r.status!==0)throw Error(r.stderr.toString());t.setImage(r.stdout).setMimeType('image/webp');
}
doc.createExtension(EXTTextureWebP).setRequired(true);await doc.transform(draco({method:'edgebreaker',quantizePosition:24,quantizeNormal:14,quantizeTexcoord:18}));const bytes=await io.writeBinary(doc);const reopened=await io.readBinary(bytes);const after=stats(reopened);if(before.triangles!==after.triangles)throw Error('Triangle count changed');const drift=Math.max(...['min','max'].flatMap(k=>before.bounds[k].map((v,i)=>Math.abs(v-after.bounds[k][i]))));if(drift>.001)throw Error('Bounds drift');if(after.textures.some(t=>t.mime!=='image/webp'))throw Error('Non-WebP');
const output=path.join(root,'12_Blender_Model/exports/r152_clean/r169_whole_row_v073_draco_webp_REVIEW.glb');fs.writeFileSync(output,bytes);const report={source,output,rawBytes:fs.statSync(source).size,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),before,after,boundsDrift:drift,accepted:false,published:false,scope:'Local review only. Compression pass does not certify visual/source similarity.'};fs.writeFileSync(path.join(root,'12_Blender_Model/reports/R169_WEB_REVIEW_v073.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));

