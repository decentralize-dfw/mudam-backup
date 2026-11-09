import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {NodeIO,getBounds} from '@gltf-transform/core';
import {ALL_EXTENSIONS,EXTMeshoptCompression} from '@gltf-transform/extensions';
import {dedup,flatten,join,prune,instance} from '@gltf-transform/functions';
import {MeshoptEncoder,MeshoptDecoder} from 'meshoptimizer';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../12_Blender_Model');
await Promise.all([MeshoptEncoder.ready,MeshoptDecoder.ready]);
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.encoder':MeshoptEncoder,'meshopt.decoder':MeshoptDecoder});
const count=d=>d.getRoot().listNodes().reduce((n,node)=>n+(node.getExtension('EXT_mesh_gpu_instancing')?.getAttribute('TRANSLATION')?.getCount()??1)*(node.getMesh()?.listPrimitives()??[]).reduce((v,p)=>v+(p.getIndices()?.getCount()??p.getAttribute('POSITION').getCount())/3,0),0);
const layers=[];
for(const [key,file] of [['building','building'],['near_context','near_site'],['far_context','philharmonie'],['melia','melia'],['schuman','schuman'],['vegetation','vegetation']]){
 const source=path.join(root,'exports/r152_clean',file+'.glb');const doc=await io.read(source);const before=count(doc);const bounds=getBounds(doc.getRoot().listScenes()[0]);
 if(key==='vegetation')for(const mat of doc.getRoot().listMaterials())if(mat.getName()==='R158_LEAFY_BRANCH_CUTOUT')mat.setAlphaMode('MASK').setAlphaCutoff(0.45).setDoubleSided(true);
 if(key==='vegetation')await doc.transform(dedup(),instance({min:2}),prune());else await doc.transform(dedup(),flatten(),join(),prune());
 // Compression only: no simplification, texture resampling or quantize transform.
 doc.createExtension(EXTMeshoptCompression).setRequired(true).setEncoderOptions({method:EXTMeshoptCompression.EncoderMethod.QUANTIZE});
 const out=path.join(root,'exports/r152_clean',file+'_web.glb');await io.write(out,doc);const check=await io.read(out);const after=count(check);const b=getBounds(check.getRoot().listScenes()[0]);
 const error=Math.max(...bounds.min.map((v,i)=>Math.abs(v-b.min[i])),...bounds.max.map((v,i)=>Math.abs(v-b.max[i])));if((key!=='vegetation'&&error>.001)||before!==after)throw Error('Geometry changed: '+error+' triangles '+before+' / '+after);
 const bytes=fs.readFileSync(out),gz=zlib.gzipSync(bytes,{level:9});fs.writeFileSync(out+'.gz',gz);
 layers.push({key,url:'../exports/r152_clean/'+file+'_web.glb.gz',bytes:bytes.length,gzip_bytes:gz.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),triangles:after,source_instanced_triangles:before,bounds_error_m:key==='vegetation'?null:error,gpu_instances:check.getRoot().listNodes().reduce((n,o)=>n+(o.getExtension('EXT_mesh_gpu_instancing')?.getAttribute('TRANSLATION')?.getCount()??0),0),draw_primitives_after:check.getRoot().listMeshes().reduce((n,m)=>n+m.listPrimitives().length,0)});
 console.log(key,JSON.stringify(layers.at(-1)));
}
fs.writeFileSync(path.join(root,'config/r152_clean_site_preview.json'),JSON.stringify({scene:'MUDAM_R159_KAYNAK_ORTU_OLCEGI_v001.blend',status:'review_candidate',layers},null,2));
