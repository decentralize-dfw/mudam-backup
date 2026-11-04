// Prepared for local R588 review only. Do not run before parent geometry/AO QA authorization.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
const require = createRequire('C:/Users/yigit/Desktop/WORK/MUDAM/web/package.json');
const {NodeIO,PropertyType,getBounds} = require('@gltf-transform/core');
const {ALL_EXTENSIONS,EXTTextureWebP} = require('@gltf-transform/extensions');
const {draco,mergeDocuments,unpartition,dedup,prune,instance} = require('@gltf-transform/functions');
const draco3d = require('draco3dgltf');
const aoReport=JSON.parse(fs.readFileSync('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model/reports/R588_AO_BUILD.json','utf8'));
if(!aoReport.reopened || aoReport.geometryChanged !== false) throw Error('R588 AO preservation/reopen gate not passed');
const requiredAO=['R588_WEST_APRON_AND_RETAINING_BODY','R588_WEST_CLASS2_GROUND_RESTORATION','R523_WEST_MOAT_LOWER_GROUND_0','R552_WEST_SLOPING_MASONRY_PLINTH','R549_WEST_GLASS_EXTERNAL_GROUND_0','R549_WEST_GLASS_EXTERNAL_GROUND_1','R588_WEST_GLASS_CORNER_GROUND','R546_WEST_MOAT_EDGE_1'];
const handoff=JSON.parse(fs.readFileSync('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model/reports/R588_GEOMETRY_HANDOFF.json','utf8'));
if(!handoff.geometryChecksPassed || !handoff.localVisualReviewPassed || aoReport.sourceScene!==handoff.scene || !requiredAO.every(name=>aoReport.targets.some(t=>t.name===name))) throw Error('Expected reviewed R588 whole western junction and source-graded ground AO');
if(!aoReport.targets.every(t=>t.retainedUVsPreserved && t.connectedMaterialUsedUVsPreserved && t.uvCount<=8)) throw Error('R588 UV preservation/limit gate not passed');
const R='C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model/',sha=b=>crypto.createHash('sha256').update(b).digest('hex');const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule(),'draco3d.encoder':await draco3d.createEncoderModule()});const result={reviewOnly:true,fullScopeAccepted:false,sourceScene:aoReport.outputScene,files:{}};
const sanitationPolicy = {
  areaBelowSquareMetres: 1e-10, altitudeBelowMetres: 1e-5,
  rule: 'Exact collapse OR (area64 < 1e-10 m2 AND altitude64 < 1e-5 m)',
  operation: 'Web-export index removal only; no scene edit, rebake, position, UV or normal change',
};
result.sanitation = {policy:sanitationPolicy, stages:[], decodedAudits:[]};
function triangleMetrics(a,b,c) {
  const u=b.map((x,i)=>x-a[i]),v=c.map((x,i)=>x-a[i]);
  const cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
  const area64=Math.hypot(...cross)/2;
  const maxEdge=Math.max(Math.hypot(...u),Math.hypot(...v),Math.hypot(...b.map((x,i)=>x-c[i])));
  const altitude64=maxEdge ? 2*area64/maxEdge : 0;
  const exactCollapsed=cross.every(x=>x===0);
  return {area64,maxEdge,altitude64,exactCollapsed,
    removable:exactCollapsed || (area64<sanitationPolicy.areaBelowSquareMetres && altitude64<sanitationPolicy.altitudeBelowMetres)};
}
function audit(d) {
  let triangles=0,zero=0,exactCollapsed=0,numericalSlivers=0,totalRejectedArea=0;
  for(const m of d.getRoot().listMeshes())for(const p of m.listPrimitives()) {
    if(p.getMode()!==4)continue;
    const pos=p.getAttribute('POSITION'),idx=p.getIndices();
    for(const v of pos.getArray())if(!Number.isFinite(v))throw Error('Nonfinite position');
    const count=idx?.getCount()??pos.getCount();if(count%3)throw Error('Incomplete triangle index triplet');
    const a=[],b=[],c=[];
    for(let i=0;i<count;i+=3) {
      pos.getElement(idx?idx.getScalar(i):i,a);pos.getElement(idx?idx.getScalar(i+1):i+1,b);pos.getElement(idx?idx.getScalar(i+2):i+2,c);
      const q=triangleMetrics(a,b,c);triangles++;
      if(q.removable){zero++;totalRejectedArea+=q.area64;if(q.exactCollapsed)exactCollapsed++;else numericalSlivers++;}
    }
  }
  return {triangles,zero,exactCollapsed,numericalSlivers,totalRejectedArea};
}
function cleanCollapsed(d,stage) {
  const entry={stage,triangles:[],removedAreaSquareMetres:0,removedCount:0};
  let meshIndex=0;
  for(const m of d.getRoot().listMeshes()) {
    let primitiveIndex=0;
    for(const p of m.listPrimitives()) {
      if(p.getMode()!==4){primitiveIndex++;continue;}
      const idx=p.getIndices(),pos=p.getAttribute('POSITION'),count=idx?.getCount()??pos.getCount();
      const keep=[],a=[],b=[],c=[];
      for(let i=0;i<count;i+=3) {
        const ids=idx?[idx.getScalar(i),idx.getScalar(i+1),idx.getScalar(i+2)]:[i,i+1,i+2];
        pos.getElement(ids[0],a);pos.getElement(ids[1],b);pos.getElement(ids[2],c);
        const q=triangleMetrics(a,b,c);
        if(q.removable) {
          entry.triangles.push({meshIndex,mesh:m.getName(),primitiveIndex,triangle:i/3,
            indices:ids,positions:[a.slice(),b.slice(),c.slice()],...q});
          entry.removedAreaSquareMetres+=q.area64;entry.removedCount++;
        } else keep.push(...ids);
      }
      if(keep.length!==count) {
        const replacement=idx?idx.clone():d.createAccessor().setType('SCALAR').setBuffer(pos.getBuffer());
        replacement.setArray(new Uint32Array(keep));p.setIndices(replacement);
      }
      primitiveIndex++;
    }
    meshIndex++;
  }
  result.sanitation.stages.push(entry);
  return entry.removedCount;
}
function exactTextureDedup(d) {
  const root=d.getRoot(),textures=root.listTextures(),buckets=new Map(),merges=[];
  const beforeBytes=textures.reduce((sum,t)=>sum+(t.getImage()?.byteLength??0),0);
  for(const t of textures) {
    const bytes=t.getImage();if(!bytes)continue;
    const mime=t.getMimeType(),size=t.getSize(),hash=sha(bytes);
    // Metadata/texture extensions are kept unless identical and extension-free.
    const key=JSON.stringify([mime,size,hash,t.getExtras()]);
    const candidates=buckets.get(key)??[];
    const existing=candidates.find(q=>q.listExtensions().length===0 && t.listExtensions().length===0 && Buffer.from(q.getImage()).equals(Buffer.from(bytes)));
    if(existing) {
      merges.push({removed:t.getName(),retained:existing.getName(),sha256:hash,bytes:bytes.byteLength,mime,size,byteIdentical:true});
      for(const parent of t.listParents())if(parent!==root)parent.swap(t,existing);
      t.dispose();
    } else {candidates.push(t);buckets.set(key,candidates);}
  }
  const after=root.listTextures(),afterBytes=after.reduce((sum,t)=>sum+(t.getImage()?.byteLength??0),0);
  return {inputTextures:textures.length,outputTextures:after.length,beforeBytes,afterBytes,
    savedBytes:beforeBytes-afterBytes,merges,byteIdenticalOnly:true,noResize:true,losslessDeduplication:true};
}
for(const key of ['near']){
 const rawFile=R+`exports/r152_clean/r588_${key}_REVIEW.glb`;
 const rawBytes=fs.readFileSync(rawFile);const d=await io.readBinary(rawBytes);let preserved=0;
 result.rawSource={file:rawFile,bytes:rawBytes.length,sha256:sha(rawBytes),audit:audit(d)};
 if(key==='district'){preserved=d.getRoot().listNodes().filter(n=>n.getName().startsWith('ARCH_')).length;if(preserved!==322)throw Error('Expected322existingrow nodes,got '+preserved);}
 const maps=new Map();
 function infos(obj){const out=[];for(let proto=obj;proto;proto=Object.getPrototypeOf(proto)){for(const k of Object.getOwnPropertyNames(proto)){if(/^get.*TextureInfo$/.test(k)&&typeof obj[k]==='function'){const v=obj[k]();if(v&&!out.includes(v))out.push(v);}}}return out;}
 for(const m of d.getRoot().listMaterials()){const ii=[...infos(m),...m.listExtensions().flatMap(infos)];const channels=[...new Set(ii.map(t=>t.getTexCoord()))].sort((a,b)=>a-b);if(channels.length>4)throw Error('More than4 usedUV sets '+m.getName());maps.set(m,{ii,channels});}
 let stripped=0,verified=0;
 for(const mesh of d.getRoot().listMeshes())for(const p of mesh.listPrimitives()){const map=maps.get(p.getMaterial());const channels=map?.channels??[];const attributes=channels.map(c=>{const a=p.getAttribute('TEXCOORD_'+c);if(!a)throw Error('MissingUV '+c);return a;});for(const semantic of p.listSemantics())if(semantic.startsWith('TEXCOORD_')){p.setAttribute(semantic,null);stripped++;}for(let i=0;i<attributes.length;i++){p.setAttribute('TEXCOORD_'+i,attributes[i]);if(p.getAttribute('TEXCOORD_'+i)!==attributes[i])throw Error('UV changed');verified++;}}
 for(const {ii,channels}of maps.values())for(const t of ii)t.setTexCoord(channels.indexOf(t.getTexCoord()));
 result.uvCompaction={stripped,reboundAttributes:verified,maxChannel:Math.max(...[...maps.values()].map(v=>v.channels.length-1)),losslessCoordinateArrays:true};
 for(const t of d.getRoot().listTextures()){if(t.getMimeType()==='image/webp')continue;const p=spawnSync('C:/Users/yigit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',['-c','import sys,io;from PIL import Image;im=Image.open(io.BytesIO(sys.stdin.buffer.read()));im.save(sys.stdout.buffer,format="WEBP",quality=92,method=6)'],{input:Buffer.from(t.getImage()),maxBuffer:64*1024*1024});if(p.status)throw Error(p.stderr.toString());t.setImage(p.stdout).setMimeType('image/webp');}d.createExtension(EXTTextureWebP).setRequired(true);
 result.textureDedup=exactTextureDedup(d);
 let removed=cleanCollapsed(d,`${key}:raw`);
 if(key==='vegetation')await d.transform(dedup(),instance({min:2}));
 const dracoOptions={method:'edgebreaker',quantizePosition:24,quantizeNormal:14,quantizeTexcoord:18};
 await d.transform(prune({keepAttributes:true,keepLeaves:true,keepSolidTextures:true}),unpartition(),draco(dracoOptions));
 let data=await io.writeBinary(d),check=await io.readBinary(data),a;
 for(let pass=0;pass<5;pass++) {
   a=audit(check);result.sanitation.decodedAudits.push({key,pass,...a});
   const count=cleanCollapsed(check,`${key}:decoded:${pass}`);removed+=count;
   if(!count)break;
   await check.transform(draco(dracoOptions));data=await io.writeBinary(check);check=await io.readBinary(data);
 }
 a=audit(check);if(a.zero)throw Error(key+' final decoded numerical slivers '+a.zero);
 const bounds=getBounds(check.getRoot().listScenes()[0]);
 if([...bounds.min,...bounds.max].some(v=>!Number.isFinite(v)||Math.abs(v)>1500))throw Error('Invalid bounds');
 const file=R+`exports/r152_clean/r588_${key}_draco_webp_REVIEW.glb`;fs.writeFileSync(file,data);
 result.files[key]={file,bytes:data.length,sha256:sha(data),...a,removedDegenerates:removed,
   preservedRowNodes:preserved,bounds,decoded:true,
   occlusionMaterials:check.getRoot().listMaterials().filter(m=>m.getOcclusionTexture()).map(m=>({name:m.getName(),uv:m.getOcclusionTextureInfo().getTexCoord()})),
   textures:check.getRoot().listTextures().length};
 result.sanitation.totalRemovedTriangles=result.sanitation.stages.reduce((n,s)=>n+s.removedCount,0);
 result.sanitation.totalRemovedAreaSquareMetres=result.sanitation.stages.reduce((n,s)=>n+s.removedAreaSquareMetres,0);
 result.sanitation.finalDecodedAudit=a;
 fs.writeFileSync(R+'reports/R588_WEB_SANITATION_LEDGER.json',JSON.stringify({rawSource:result.rawSource,...result.sanitation,output:result.files[key]},null,2));
 fs.writeFileSync(R+'reports/R588_RELEASE_VALIDATION.json',JSON.stringify(result,null,2));
 console.log(key,result.files[key]);console.log('TEXTURE_DEDUP',result.textureDedup);

}
