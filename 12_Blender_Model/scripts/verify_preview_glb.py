"""Independent binary/glTF graph and world-bounds check, outside Blender."""
from pathlib import Path
import json,struct,numpy as np
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/P21_export_report.json').read_text());data=(R/r['file']).read_bytes();magic,version,length=struct.unpack_from('<4sII',data);assert magic==b'glTF' and version==2 and length==len(data)
size,kind=struct.unpack_from('<I4s',data,12);assert kind==b'JSON';g=json.loads(data[20:20+size]);assert g['asset']['version']=='2.0';assert not g.get('buffers',[{}])[0].get('uri')
def transform(node):
 if 'matrix' in node:return np.array(node['matrix']).reshape(4,4).T
 x,y,z,w=node.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 m=np.eye(4);m[:3,:3]=rot@np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0]);return m
points=[];names=[];triangles=0
def walk(i,parent):
 global triangles
 n=g['nodes'][i];m=parent@transform(n)
 if 'mesh' in n:
  names.append(n.get('name',''))
  for p in g['meshes'][n['mesh']]['primitives']:
   a=g['accessors'][p['attributes']['POSITION']];lo=a['min'];hi=a['max'];assert all(np.isfinite(lo+hi));assert p.get('mode',4)==4
   for mask in range(8):points.append((m@np.array([hi[j] if mask&(1<<j) else lo[j] for j in range(3)]+[1]))[:3])
   triangles+=g['accessors'][p['indices']]['count']//3 if 'indices' in p else a['count']//3
 for child in n.get('children',[]):walk(child,m)
for node in g['scenes'][g.get('scene',0)]['nodes']:walk(node,np.eye(4))
assert set(names)==set(r['selected_names']),(len(names),len(r['selected_names']),list(set(r['selected_names'])-set(names))[:10])
actual=np.array([np.min(points,axis=0),np.max(points,axis=0)]);lo=r['blender_world_bounds']['min'];hi=r['blender_world_bounds']['max'];expected=np.array([[lo[0],lo[2],-hi[1]],[hi[0],hi[2],-lo[1]]]);error=float(np.max(np.abs(actual-expected)));assert error<.005,error
# Image payloads and texture-coordinate bindings must survive Blender -> GLB.
image_checks=[];texture_checks=[];bin_start=20+size+8
for im in g.get('images',[]):
 assert not im.get('uri') and im.get('mimeType')=='image/png' and 'bufferView' in im,im
 view=g['bufferViews'][im['bufferView']];offset=bin_start+view.get('byteOffset',0);payload=data[offset:offset+view['byteLength']];assert payload[:8]==b'\x89PNG\r\n\x1a\n'
 image_checks.append(dict(name=im.get('name'),embedded_bytes=len(payload),mime=im['mimeType']))
for mi,m in enumerate(g.get('materials',[])):
 if not m.get('name','').startswith('R32_'):continue
 for usage,link in [('basecolor',m['pbrMetallicRoughness'].get('baseColorTexture')),('normal',m.get('normalTexture'))]:
  assert link,m['name'];tex=g['textures'][link['index']];im=g['images'][tex['source']];assert usage in im['name']
  uv='TEXCOORD_'+str(link.get('texCoord',0));count=0
  for mesh in g['meshes']:
   for primitive in mesh['primitives']:
    if primitive.get('material')==mi:assert uv in primitive['attributes'];count+=1
  assert count>0;texture_checks.append(dict(material=m['name'],usage=usage,image=im['name'],uv_attribute=uv,primitive_count=count))
result=dict(file=r['file'],size_bytes=len(data),mesh_nodes=len(names),triangles=triangles,world_bounds_glTF=actual.tolist(),bounds_max_error_m=error,external_binary_dependency=False,embedded_images=image_checks,texture_bindings=texture_checks,failures=[],construction_acceptance=False)
(B/'reports/P21_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
