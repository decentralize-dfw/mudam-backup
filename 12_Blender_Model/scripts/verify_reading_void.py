"""Check evaluated booleans and the actual saved daylight/floor apertures."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/P17_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[]
for name in r['closed_objects']+r['roof_boolean_targets']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);v=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces)
 if v<=0 or nm or zero:fail.append(dict(name=name,volume=v,nonmanifold=nm,zero_faces=zero))
 bm.free();ob.to_mesh_clear()
assert not fail,fail
center=Vector(r['center_world']);hits=[]
for name in ['P17_READING_FLOOR']+r['roof_boolean_targets']:
 ob=bpy.data.objects[name].evaluated_get(deps)
 for dx,dy in [(0,0),(.1,0),(-.1,0),(0,.1),(0,-.1)]:
  origin=center+Vector((dx,dy,0));local=ob.matrix_world.inverted()@origin;direction=(ob.matrix_world.inverted().to_3x3()@Vector((0,0,1))).normalized();hit=ob.ray_cast(local,direction,distance=35)[0];hits.append(dict(object=name,offset=[dx,dy],blocked=hit));assert not hit,(name,dx,dy)
# Ring still has supporting floor outside the void; the cutter must not erase the room.
floor=bpy.data.objects['P17_READING_FLOOR'].evaluated_get(deps)
mid=(Vector(r['floor_void_world'][0])+Vector(r['floor_void_world'][1]))/2;point=mid+(mid-center).normalized()*.2;point.z=0
assert floor.ray_cast(floor.matrix_world.inverted()@point,Vector((0,0,1)),distance=10)[0]
assert len([o for o in bpy.data.objects if o.name.startswith('P12_LEAF_PIVOT_')])==4
assert len([o for o in bpy.data.objects if o.name.startswith('P10_') and o.get('element_type')=='roof_glass_panel'])==359
result=dict(file=r['file'],evaluated_closed_solids_checked=len(r['closed_objects'])+len(r['roof_boolean_targets']),failures=fail,clear_vertical_rays=hits,outside_floor_preserved=True,earlier_entry_roof_preserved=True,sloping_stone_ceiling_built=False,construction_acceptance=False)
(B/'reports/P17_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
