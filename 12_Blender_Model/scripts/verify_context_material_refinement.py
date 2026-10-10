from pathlib import Path
import bpy,json,hashlib,numpy as np
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R129_build_report.json').read_text())
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  if o.type=='MESH':
   geom=([list(v.co) for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons],[[list(d.uv) for d in uv.data] for uv in o.data.uv_layers])
  else:geom=[(s.type,[list(p.co) for p in s.points]) for s in o.data.splines]
  out[o.name]=hashlib.sha256(repr((geom,[list(x) for x in o.matrix_world],o.hide_render,o.hide_get())).encode()).hexdigest()
 return out
before=snap(B/'scenes'/r['base_scene']);after=snap(R/r['file']);fail=[]
if before!=after:fail.append('geometry, UV, transforms or visibility changed')
for name in r['changed_inherited_objects']:
 o=bpy.data.objects[name]
 if not any(s.material and s.material.name in r['materials'] for s in o.material_slots):fail.append(name+' missing material')
for name in r['textures']:
 im=bpy.data.images[name]
 if not im.packed_file:fail.append(name+' not packed')
 if tuple(im.size)!=(2048,1536):fail.append(name+' size')
for material in r['materials']:
 m=bpy.data.materials[material];nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
 for socket in ['Base Color','Normal','Roughness']:
  if not bs.inputs[socket].is_linked:fail.append(material+' missing '+socket)
 if not any(n.type=='UVMAP' and n.uv_map=='R55_CONTEXT_METRIC_UV' for n in nt.nodes):fail.append(material+' UV changed')
result=dict(file=r['file'],geometry_objects_checked=len(before),unchanged_geometry_uv_transforms_visibility=before==after,material_objects=len(r['changed_inherited_objects']),packed_textures=len(r['textures']),failures=fail,construction_acceptance=False)
(B/'reports/R129_verification.json').write_text(json.dumps(result,indent=2));print(result);assert not fail
