"""Check ACT conversion preserves every triangle, UV and JPEG byte stream."""
import json,struct,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'.local_source_cache/act_context';OUT=SRC/'local_glb'
m=json.loads((OUT/'manifest.json').read_text());fail=[];triangles=0;images=0
for row in m['tiles']:
 tile,leaf=row['file'].rsplit('_',1);original=SRC/tile/leaf.replace('.glb','.b3dm')
 b=original.read_bytes();h=struct.unpack_from('<4s6I',b);g=b[28+sum(h[3:]):];n=struct.unpack_from('<I',g,12)[0];j=json.loads(g[20:20+n]);data=g[20+n:]
 converted=(OUT/row['file']).read_bytes();cn=struct.unpack_from('<I',converted,12)[0];c=json.loads(converted[20:20+cn]);cd=converted[28+cn:]
 def view(doc,buf,key):
  v=doc['bufferViews'][key];o=v.get('byteOffset',0);return buf[o:o+v['byteLength']]
 source_prims=[p for mesh in j['meshes'].values() for p in mesh['primitives']]
 dest_prims=c['meshes'][0]['primitives']
 assert len(source_prims)==len(dest_prims)
 for p,q in zip(source_prims,dest_prims):
  a=j['accessors'][p['indices']];av=view(j,data,a['bufferView']);count=a['count'];size={5123:2,5125:4}[a['componentType']]
  old=[struct.unpack_from('<H' if size==2 else '<I',av,a.get('byteOffset',0)+k*a.get('byteStride',size))[0] for k in range(count)]
  ca=c['accessors'][q['indices']];new=list(struct.unpack('<'+'I'*ca['count'],view(c,cd,ca['bufferView'])))
  if old!=new:fail.append([row['file'],'triangle_indices'])
  uv=j['accessors'][p['attributes']['TEXCOORD_0']];cuv=c['accessors'][q['attributes']['TEXCOORD_0']]
  uvbuf=view(j,data,uv['bufferView']);start=uv.get('byteOffset',0);stride=uv.get('byteStride',8)
  uvbytes=b''.join(uvbuf[start+k*stride:start+k*stride+8] for k in range(uv['count']))
  if uvbytes!=view(c,cd,cuv['bufferView']):fail.append([row['file'],'uv_bytes'])
  mat=j['materials'][p['material']];im=j['images'][j['textures'][mat['values']['diffuse']]['source']]['extensions']['KHR_binary_glTF']
  ci=c['images'][c['textures'][c['materials'][q['material']]['pbrMetallicRoughness']['baseColorTexture']['index']]['source']]
  if view(j,data,im['bufferView'])!=view(c,cd,ci['bufferView']):fail.append([row['file'],'jpeg_bytes'])
  triangles+=count//3;images+=1
result={'passed':not fail,'checked_tiles':len(m['tiles']),'triangles':triangles,'unchanged_images':images,'failures':fail,'scope':'Source triangle indices, UV bytes and embedded image bytes only; does not prove complete download, positioning, visual parity or production integration'}
(ROOT/'reports/ACT2020_conversion_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert not fail
