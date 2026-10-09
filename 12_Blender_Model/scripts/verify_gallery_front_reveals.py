from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R15_build_report.json').read_text());P=json.loads((B/'config/gallery_front_reveals.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render];direction=Vector(r['inside']);axis=Vector(r['axis']);up=Vector((0,0,1));checks=[]
for op in r['openings']:
 if op['type']!='glazed':continue
 for dx in [-.6,0,.6]:
  for dz in [-.6,0,.6]:
   center=Vector(op['glass_center'])+axis*dx+up*dz;p=center-direction*1.5;hits=[]
   for ob in visible:
    iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@p,iv.to_3x3()@direction,distance=1.55)
    if ok:hits.append(ob.name)
   row=dict(bay=op['index'],dx=dx,dz=dz,hits=hits);checks.append(row)
   if hits!=[f'R15_BAY_{op["index"]}_GLASS']:fail.append(row)
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,window_clear_view_checks=checks,construction_acceptance=False);(B/'reports/R15_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),checks=len(checks),failures=fail),indent=2));assert not fail,fail
