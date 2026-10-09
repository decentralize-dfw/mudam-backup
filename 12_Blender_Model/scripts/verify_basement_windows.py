"""Independent evaluated solids and all-active exterior aperture rays."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R40_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render];inside=Vector(r['inside']);axis=Vector(r['axis']);up=Vector((0,0,1));rays=[]
for win in r['windows']:
 center=Vector(win['center'])
 for dx in [-.38,0,.38]:
  for dz in [-.5,0,.5]:
   target=center+axis*dx+up*dz;start=target-inside*6;hits=[]
   for ob in visible:
    iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@start,iv.to_3x3()@inside,distance=6.05)
    if ok:hits.append(((ob.matrix_world@loc-start).length,ob.name))
   hits.sort();row=dict(window=win['id'],offset=[dx,dz],first_hit=hits[0] if hits else None,hits=hits);rays.append(row)
   if not hits or hits[0][1]!=win['glass']:fail.append(row)
# Retained upper facade apertures must stay reachable.
old=json.loads((B/'reports/R36_build_report.json').read_text());upper=[]
for win in old['openings']:
 if win['type']!='glazed':continue
 target=Vector(win['glass_center']);start=target-inside*4;hits=[]
 for ob in visible:
  iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@start,iv.to_3x3()@inside,distance=4.03)
  if ok:hits.append(((ob.matrix_world@loc-start).length,ob.name))
 hits.sort();row=dict(bay=win['index'],hits=hits);upper.append(row)
 if not hits or hits[0][1]!=f"R27_BAY_{win['index']}_GLASS":fail.append(row)
result=dict(file=r['file'],evaluated_solids=solids,exterior_rays=rays,upper_window_regression=upper,failures=fail,construction_acceptance=False);(B/'reports/R40_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),rays=len(rays),failures=fail),indent=2));assert not fail,fail
