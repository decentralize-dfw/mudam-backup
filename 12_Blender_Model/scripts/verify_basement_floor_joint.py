from pathlib import Path
import bpy,json,math,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R89_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];rows=[]
for item in r['walls']:
 ob=bpy.data.objects[item['name']];ps=[ob.matrix_world@v.co for v in ob.data.vertices];before=[Vector(p) for p in item['before_vertices']];assert len(ps)==len(before);faces=[list(f.vertices) for f in ob.data.polygons];old=BVHTree.FromPolygons(before,faces);new=BVHTree.FromPolygons(ps,faces);center=sum(ps,Vector())/len(ps);center.z=(item['old_top']+item['new_top'])/2;tests=[]
 for angle in range(0,360,45):
  a=math.radians(angle);d=Vector((math.cos(a),math.sin(a),0));was=old.ray_cast(center,d,200)[0] is not None;now=new.ray_cast(center,d,200)[0] is not None;tests.append(dict(angle=angle,before_closed=was,after_closed=now))
  if was or not now:fail.append(dict(name=ob.name,test=tests[-1]))
 for a,b in zip(before,ps):
  if (a.xy-b.xy).length>1e-5 or (abs(a.z-item['old_top'])>1e-5 and abs(a.z-b.z)>1e-5):fail.append(dict(name=ob.name,unexpected_vertex_change=True))
 rows.append(dict(name=ob.name,checks=tests))
q=dict(file=r['file'],wall_checks=rows,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R89_verification.json').write_text(json.dumps(q,indent=2));print('R89',len(rows)*8,'before/after boundary rays',len(fail),'failures');assert not fail
