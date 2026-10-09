"""Check saved portal volumes and rays at lower / upper openings and beam."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R02_build_report.json').read_text());r['file']=json.loads((B/'reports/R116_build_report.json').read_text())['file'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[]
for name in r['closed_objects']:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);assert bm.calc_volume(signed=True)>0 and all(e.is_manifold for e in bm.edges) and all(f.calc_area()>1e-10 for f in bm.faces);bm.free()
assert all(bpy.data.objects[n].hide_render for n in r['hidden_superseded'])
deps=bpy.context.evaluated_depsgraph_get();visible_meshes=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
a,b=map(Vector,r['portal_endpoints']);normal=Vector(r['normal']);tests=[]
for t in [.2,.5,.8]:
 for z,should_hit in [(1.2,False),(r['ground_clear']-.05,False),((r['ground_clear']+r['beam_top'])/2,True),(r['beam_top']+.2,False),(r['upper_head']-.4,False)]:
  p=a.lerp(b,t);p.z=z;hits=[]
  for ob in visible_meshes:
   name=ob.name;hit=ob.ray_cast(ob.matrix_world.inverted()@(p-normal*.5),ob.matrix_world.inverted().to_3x3()@normal,distance=1)[0]
   if hit:hits.append(name)
  assert bool(hits)==should_hit,(t,z,hits);tests.append(dict(t=t,z=z,hits=hits))
assert len([o for o in bpy.data.objects if o.name.startswith('P10_') and o.get('element_type')=='roof_glass_panel'])==359
assert all(bpy.data.objects.get('P09_PODIUM_'+str(i)) for i in [1,2,3])
result=dict(file=r['file'],closed_solids_checked=len(r['closed_objects']),failures=[],portal_ray_tests=tests,earlier_roof_podium_preserved=True,metric_interior_camera_verified=False,construction_acceptance=False)
(B/'reports/R116_portal_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
