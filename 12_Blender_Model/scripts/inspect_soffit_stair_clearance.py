"""Full-scene 2.1m review headroom across tread interiors; not statutory acceptance."""
from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R112_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs);up=Vector((0,0,1));rows=[];counts={}
for rev in ['R04','R05','R10','R14','R25','R97']:
 report=json.loads((B/'reports'/f'{rev}_build_report.json').read_text());counts[rev]=0
 for step in report['steps']:
  ob=bpy.data.objects[step['name']];points=[ob.matrix_world@v.co for v in ob.data.vertices];z=max(p.z for p in points);top=[p for p in points if abs(p.z-z)<1e-4];center=sum(top,Vector())/len(top);candidates=[center]+[center.lerp(p,.5) for p in top];unique=[]
  for p in candidates:
   if any((p-q).length<.01 for q in unique):continue
   unique.append(p)
  for i,p in enumerate(unique):
   support=tree.ray_cast(p+up*.025,-up,.05)
   if support[0] is None or owners[support[2]]!=ob.name:continue
   counts[rev]+=1;hit=tree.ray_cast(p+up*.025,up,2.075)
   if hit[0] is not None:rows.append(dict(stair=rev,step=ob.name,sample=i,point=list(p),obstruction=owners[hit[2]],clear_height=hit[0].z-p.z))
q=dict(file=r['file'],sample_counts=counts,findings=rows,construction_acceptance=False,limits=['2.1m is a review probe, not measured statutory compliance.','Confirmed tread interior samples only; boundary/rail areas and source geometry require separate checks.']);(B/'reports/R112_stair_width_clearance.json').write_text(json.dumps(q,indent=2));print('SAMPLES',counts,'FINDINGS',len(rows));print(sorted(set((x['stair'],x['obstruction']) for x in rows)))
