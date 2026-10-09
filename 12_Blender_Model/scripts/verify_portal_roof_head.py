from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R37_build_report.json').read_text());P=json.loads((B/'config/gallery_reveals_revised.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()

visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
a,b=map(Vector,r['portal_endpoints']);normal=Vector(r['normal']);checks=[]
for t in [.1,.2,.3,.4,.5,.6,.7,.8,.9]:
 for label,z,want in [('clear',r['upper_head']-.05,False),('head',r['upper_head']+.05,True),('old_probe',r['roof_reference_z']-.2,True)]:
  p=a.lerp(b,t);p.z=z;p-=normal*.5;hits=[]
  for ob in visible:
   iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@p,iv.to_3x3()@normal,distance=1)
   if ok:hits.append(ob.name)
  row=dict(t=t,z=z,label=label,hits=hits);checks.append(row)
  if (want and 'R37_GH_EAST_PORTAL_METAL_HEAD' not in hits) or (not want and hits):fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,portal_checks=checks,upper_head=r['upper_head'],construction_acceptance=False)
(B/'reports/R37_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),checks=len(checks),failures=fail),indent=2));assert not fail,fail
