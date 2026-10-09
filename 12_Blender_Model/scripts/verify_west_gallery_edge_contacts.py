from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R105_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];results={};fail=[]
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
  eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
  eo.to_mesh_clear()
 t=BVHTree.FromPolygons(vs,fs);rows=[]
 for f in [.1,.3,.5,.7,.9]:
  x=r['wall_x']+(r['old_edge_x']-r['wall_x'])*f
  for i in range(103):
   y=r['y_range'][0]+(r['y_range'][1]-r['y_range'][0])*(i+.5)/103
   for label,z,d in [('floor',.03,-1),('ceiling',4.32,1)]:
    hit=t.ray_cast(pt(x,y,z),Vector((0,0,d)),.1);rows.append(dict(kind=label,x=x,y=y,hit=None if hit[0] is None else owners[hit[2]],passed=hit[0] is not None))
 results[phase]=rows
 if phase=='after':fail.extend(x for x in rows if not x['passed'])
solids=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=True));bm.free();solids.append(q)
 if q['nonmanifold'] or q['zero_faces'] or q['volume']<=0:fail.append(q)
q=dict(file=r['file'],results=results,solids=solids,before_missing=sum(not x['passed'] for x in results['before']),after_missing=sum(not x['passed'] for x in results['after']),failures=fail,construction_acceptance=False)
(B/'reports/R105_verification.json').write_text(json.dumps(q,indent=2));print('R105',q['before_missing'],'old misses',q['after_missing'],'remaining',len(fail),'failures');assert not fail
