from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R114_build_report.json').read_text());poly=[Vector(v) for v in r['polygon_world']];up=Vector((0,0,1));axis=(poly[1]-poly[0]).normalized();n=up.cross(axis);fail=[];results={}
for phase,path in [('before',B/'scenes'/r['base_scene']),('after',B.parent/r['file'])]:
 bpy.ops.wm.open_mainfile(filepath=str(path));deps=bpy.context.evaluated_depsgraph_get();obs=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o.visible_get()]
 def ray(p,d,dist,exclude=None):
  hits=[]
  for o in obs:
   if o.name==exclude:continue
   iv=o.matrix_world.inverted();ok,loc,_,_=o.ray_cast(iv@p,iv.to_3x3()@d,distance=dist)
   if ok:hits.append((o.name,(o.matrix_world@loc-p).length))
  return sorted(hits,key=lambda q:q[1])
 rows=[]
 for f in [.1,.3,.5,.7,.9]:
  for z in [-5.1,-4,-3,-2,-1]:
   p=poly[0].lerp(poly[1],f)+up*z-n*.05;hits=ray(p,n,.1);ok=bool(hits) and hits[0][0]==r['closed_objects'][0];rows.append(dict(f=f,z=z,hits=hits,blade_present=ok))
   if phase=='after' and not ok:fail.append(rows[-1])
 results[phase]=rows
 if phase=='after':
  contacts=[]
  for f in [.1,.5,.9]:
   p=poly[0].lerp(poly[1],f)+n*.14;floor=ray(p+up*(r['z_range'][0]+.01),-up,.03,r['closed_objects'][0]);ceiling=ray(p+up*(-.4),up,.3,r['closed_objects'][0]);ok=bool(floor) and bool(ceiling);contacts.append(dict(f=f,floor=floor,ceiling=ceiling,passed=ok))
   if not ok:fail.append(contacts[-1])
q=dict(file=r['file'],failures=fail,surface_checks=results,contacts=contacts,source_presence='051,052',dimensions='D representative landing-aligned footprint; not measured',construction_acceptance=False);(B/'reports/R114_verification.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('FAILURES',fail);assert not fail
