import fs from 'node:fs';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS,EXTTextureWebP} from '@gltf-transform/extensions';
import {draco,unpartition} from '@gltf-transform/functions';
import draco3d from 'draco3dgltf';
const root='12_Blender_Model/',io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule(),'draco3d.encoder':await draco3d.createEncoderModule()});
const d=await io.read(root+'exports/r152_clean/r297_south_roof_REVIEW.glb');
function audit(doc){let triangles=0,zero=0;for(const m of doc.getRoot().listMeshes())for(const p of m.listPrimitives()){const pos=p.getAttribute('POSITION'),idx=p.getIndices();for(const v of pos.getArray())if(!Number.isFinite(v))throw Error('Nonfinite');const a=[],b=[],c=[];for(let i=0;i<(idx?.getCount()??pos.getCount());i+=3){pos.getElement(idx?idx.getScalar(i):i,a);pos.getElement(idx?idx.getScalar(i+1):i+1,b);pos.getElement(idx?idx.getScalar(i+2):i+2,c);const u=b.map((v,j)=>v-a[j]),v=c.map((v,j)=>v-a[j]);if([u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]].every(x=>Math.abs(x)<1e-12))zero++;triangles++;}}return{triangles,zero};}
const before=audit(d);if(before.zero)throw Error('Input degenerate geometry');
for(const t of d.getRoot().listTextures()){
 const p=spawnSync('C:/Users/yigit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['-c','import sys,io;from PIL import Image;im=Image.open(io.BytesIO(sys.stdin.buffer.read()));im.save(sys.stdout.buffer,format="WEBP",lossless=True,method=6)'],{input:Buffer.from(t.getImage()),maxBuffer:64*1024*1024});if(p.status)throw Error(p.stderr.toString());t.setImage(p.stdout).setMimeType('image/webp');
}
d.createExtension(EXTTextureWebP).setRequired(true);await d.transform(unpartition(),draco({method:'edgebreaker',quantizePosition:24,quantizeNormal:14,quantizeTexcoord:18}));
const data=await io.writeBinary(d),reopened=await io.readBinary(data),after=audit(reopened);if(after.zero||after.triangles!==before.triangles)throw Error('Geometry changed');
const file=root+'exports/r152_clean/r297_south_roof_draco_webp_REVIEW.glb';fs.writeFileSync(file,data);
const report={accepted:false,published:false,file,bytes:data.length,sha256:crypto.createHash('sha256').update(data).digest('hex'),before,after,textures:reopened.getRoot().listTextures().length,losslessWebP:true,decoded:true};fs.writeFileSync(root+'reports/R297_GLB_VALIDATION.json',JSON.stringify(report,null,2));console.log(report);
