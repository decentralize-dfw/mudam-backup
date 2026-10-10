"""R146 stone finish continuity on existing curved west stone base walls."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base=json.loads((B/'reports/R145_build_report.json').read_text())['file'];out=B/'scenes/MUDAM_R146_BATI_KAVIS_TAS_KAPLAMA_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/base));UV='R146_STONE_METRIC_UV';mats={}
for kind,old in [('grain','R46_STONE_GRAIN_APPEARANCE_CANDIDATE'),('joint','R32_LIMESTONE_APPEARANCE_CANDIDATE')]:
 m=bpy.data.materials[old].copy();m.name='R146_'+kind.upper()+'_STONE_CANDIDATE'
 for node in m.node_tree.nodes:
  if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=UV
 m['source_ids']='093,102';m['limits']='Existing stone visual family, no surveyed slab dimensions or physical colour';mats[kind]=m
ceilings=[];stairs=[];walls=['P11_WEST_STONE_BASE_'+str(i) for i in range(18)];rows=[]
# Follow the original P11 registered polyline; lengths are model values, not a survey.
import math
F=json.loads((B/'config/foundation.json').read_text());C=F['calibration'];M=C['pdf_to_utm_matrix'];curve=F['polygons']['WEST_CAFE'][:-2];lengths=[0.]
for a,b in zip(curve,curve[1:]):lengths.append(lengths[-1]+math.dist(a,b))
def point(p):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];a=k*p[0]+ox;b=k*p[1]+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
def sample(t):
 d=t*lengths[-1]
 for j in range(len(lengths)-1):
  if d<=lengths[j+1]+1e-8:
   u=(d-lengths[j])/(lengths[j+1]-lengths[j]);return point([curve[j][n]*(1-u)+curve[j+1][n]*u for n in range(2)])
 return point(curve[-1])
ends=[sample(i/18) for i in range(19)];arc=[0.]
for a,b in zip(ends,ends[1:]):arc.append(arc[-1]+(b-a).length)

for name in ceilings+stairs+walls:
 o=bpy.data.objects[name];assert not o.hide_render and o.visible_get();o.data=o.data.copy();me=o.data;nm=o.matrix_world.to_3x3().inverted().transposed();uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;slots={}
 for kind,m in mats.items():slots[kind]=len(me.materials);me.materials.append(m)
 faces=[];idx=int(name.rsplit('_',1)[1]);tangent=(ends[idx+1]-ends[idx]).normalized()
 for f in me.polygons:
  old=me.materials[f.material_index].name
  if old!='P05_NEUTRAL_ENVELOPE':continue
  n=(nm@f.normal).normalized()
  if name in ceilings and n.z>=-.05:continue
  main_side=abs(n.z)<.05 and abs(n.dot(tangent))<.01
  kind='joint' if main_side else 'grain';repeat=(3.2,2.4) if main_side else (2.,2.)
  u=tangent if main_side else (Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.95 else Vector((1,0,0)))
  v=Vector((0,0,1)) if main_side else n.cross(u).normalized()
  offset=(arc[idx]-ends[idx].dot(tangent))/repeat[0] if main_side else 0.
  f.material_index=slots[kind]
  for li in f.loop_indices:
   p=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/repeat[0]+offset,p.dot(v)/repeat[1])
  faces.append(dict(face=f.index,material=mats[kind].name,u=list(u),v=list(v),repeat_m=repeat,uv_offset=[offset,0.]))
 assert faces,name
 o['surface_appearance_revision']='R146';o['surface_source_ids']='093,102';o['surface_limits']='Photographed stone family. Inherited procedural grain and joints are not a surveyed panel schedule.';rows.append(dict(name=name,faces=faces))
sources=[q for q in json.loads((B/'references/source_manifest.json').read_text()) if q['id'] in ['093','102']]
for q in sources:assert hashlib.sha256((R/q['path']).read_bytes()).hexdigest()==q['sha256']
bpy.context.scene['stage']='R146 curved west stone base stone wall material continuity';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R146_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[q['name'] for q in rows],closed_objects=[],surface_objects=rows,uv_map=UV,materials=[m.name for m in mats.values()],sources=sources,geometry_changed=False,construction_acceptance=False),indent=2)+'\n');print('R146',len(rows),'objects',sum(len(q['faces']) for q in rows),'faces')
