"""P20 non-destructive horizontal mesh sections in the calibrated plan frame."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(B/'scripts'));from release_utils import verified_current_scene
release=verified_current_scene();C=json.loads((B/'config/foundation.json').read_text())['calibration'];Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']}
bpy.ops.wm.open_mainfile(filepath=str(R/release['file']));deps=bpy.context.evaluated_depsgraph_get();M=C['pdf_to_utm_matrix'];inv=Matrix([row[:2] for row in M]).inverted();k=C['canonical_to_pdf_scale'];off=C['canonical_to_pdf_offset']
# Python double precision inverse avoids float32 cancellation on the UTM northing.
det=M[0][0]*M[1][1]-M[0][1]*M[1][0]
def canonical(p):
 a=p.x+293425-M[0][2];b=p.y+5499960-M[1][2];u=(M[1][1]*a-M[0][1]*b)/det;v=(-M[1][0]*a+M[0][0]*b)/det
 return [(u-off[0])/k,(v-off[1])/k]
levels=[dict(id='L00',source='102',z=1.2,above_floor=1.2),dict(id='LP1',source='103',z=Z['Z_LP1_FINISH']+.9,above_floor=.9)];counts={};objects=[];excluded_vegetation=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 if ob.name.startswith(('R38_TREE_','R56_TREE_')):excluded_vegetation.append(ob.name);continue
 eo=ob.evaluated_get(deps);bounds=[eo.matrix_world@Vector(p) for p in eo.bound_box];lo=min(p.z for p in bounds);hi=max(p.z for p in bounds)
 active=[level for level in levels if lo-1e-6<=level['z']<=hi+1e-6]
 if not active:continue
 me=eo.to_mesh();me.calc_loop_triangles();points=[eo.matrix_world@v.co for v in me.vertices];is_glass=any(m and m.use_nodes and (n:=m.node_tree.nodes.get('Principled BSDF')) and n.inputs['Transmission Weight'].default_value>.5 for m in me.materials)
 for level in active:
  segments=[];seen=set();z=level['z']
  for tri in me.loop_triangles:
   vs=[points[i] for i in tri.vertices];hits=[]
   for a,b in zip(vs,vs[1:]+vs[:1]):
    if (a.z<z<=b.z) or (b.z<z<=a.z):hits.append(a.lerp(b,(z-a.z)/(b.z-a.z)))
   if len(hits)!=2 or (hits[0]-hits[1]).length<1e-6:continue
   endpoints=[canonical(p) for p in hits];key=tuple(sorted(tuple(round(v,5) for v in p) for p in endpoints))
   if key in seen:continue
   seen.add(key);segments.append(endpoints)
  if segments:objects.append(dict(level=level['id'],name=ob.name,glass=is_glass,status=ob.get('status','unclassified'),segments=segments))
 eo.to_mesh_clear()
for l in levels:counts[l['id']]=dict(objects=sum(o['level']==l['id'] for o in objects),segments=sum(len(o['segments']) for o in objects if o['level']==l['id']))
assert all(v['segments']>0 for v in counts.values())
report=dict(scene=release['file'],method='Evaluated visible architectural mesh / horizontal-plane triangle intersections. Tree foliage, branches and trunks excluded explicitly; no building geometry or plan warping.',excluded_vegetation=excluded_vegetation,levels=levels,counts=counts,objects=objects,construction_acceptance=False)
(B/'reports/P20_sections.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(counts,indent=2))
