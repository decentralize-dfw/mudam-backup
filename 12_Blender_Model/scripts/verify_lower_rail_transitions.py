from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R48_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];joins=[]
def points(name):
 ob=bpy.data.objects[name];return [ob.matrix_world@v.co for v in ob.data.vertices]
for name in r['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);v=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);bm.free();row=dict(name=name,volume=v,nonmanifold=nm,zero_faces=zero);solids.append(row)
 if v<=0 or nm or zero or ob.hide_render:fail.append(row)
for j in r['joins']:
 e=points(j['continuous_rail']);cc=[Vector(p) for p in j['continuous_centers']];radial=max(abs((p-cc[i//20]).length-j['radius_m']) for i,p in enumerate(e));advance=min((e[(k+1)*20+i]-e[k*20+i]).dot((cc[k+1]-cc[k]).normalized()) for k in range(len(cc)-1) for i in range(20));original=points(j['old_rail']);n=j['retained_rail_rings']*20;unchanged=max((p-q).length for p,q in zip(e[:n],original[:n]));row=dict(side=j['side'],radius_error_m=radial,retained_rail_vertex_error_m=unchanged,minimum_longitudinal_advance_m=advance,continuous_rings=len(cc),original_centerline_gap_m=j['before_centerline_gap_m']);joins.append(row)
 if radial>2e-5 or unchanged>2e-5 or advance<=0:fail.append(row)
 for name in [j['old_rail'],j['old_ground']]:
  if not bpy.data.objects[name].hide_render:fail.append(dict(old_rail_still_visible=name))
result=dict(file=r['file'],closed_solids=solids,joins=joins,failures=fail,construction_acceptance=False);(B/'reports/R48_verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert not fail,fail
