from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R95_build_report.json').read_text());results={};fail=[]
for phase,file in [('before','12_Blender_Model/scenes/'+r['base_scene']),('after',r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(B.parent/file));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or not o.visible_get():continue
  eo=o.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
  for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(o.name)
  eo.to_mesh_clear()
 t=BVHTree.FromPolygons(vs,fs,epsilon=.00001);rows=[]
 for p in r['probes']:
  a=Vector(p['point']);n=Vector(p['normal']);hit=t.ray_cast(a+n*.7,-n,1.4);ok=(hit[0] is not None)==(p['expected']=='closed');rows.append(dict(issue=p['issue'],expected=p['expected'],point=p['point'],hit=None if hit[0] is None else owners[hit[2]],passed=ok))
 for f in r['glazed_surfaces']:
  ps=[Vector(p) for p in f['vertices']];a=sum(ps,Vector())/len(ps);n=Vector(f['normal']);hit=t.ray_cast(a+n*.15,-n,.3);rows.append(dict(issue='SS1_SS2',point=list(a),expected='closed',hit=None if hit[0] is None else owners[hit[2]],passed=hit[0] is not None))
 results[phase]=rows
 if phase=='after':fail.extend([p for p in rows if not p['passed']])
summary={i:dict(before_failed=sum(not p['passed'] for p in results['before'] if p['issue']==i),after_failed=sum(not p['passed'] for p in results['after'] if p['issue']==i)) for i in ['SS1_SS2','SS3','SS4','SS5']}
q=dict(file=r['file'],results=results,summary=summary,failures=fail,construction_acceptance=False);(B/'reports/R95_targeted_before_after.json').write_text(json.dumps(q,indent=2));print(summary);assert not fail,fail
