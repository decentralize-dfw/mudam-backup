import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
exec((R/'scripts/audit_r555_coverage.py').read_text().split('bpy.ops.wm.open_mainfile')[0])
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R557_KUZEY_YAKLASIM_ZEMIN_BUTUNLUGU_ADAY_v001.blend'));bv=tree();rows=[]
for q in json.loads((R/'reports/R555_EXPOSED_COVERAGE_GAPS.json').read_text())['rows']:
 p=bv.ray_cast(Vector((q['x'],q['y'],60)),Vector((0,0,-1)),140)[0];rows.append(dict(**q,candidateZ=p.z if p else None))
(R/'reports/R560_TARGETED_GROUND_RECHECK.json').write_text(json.dumps(rows,indent=2));del bv
bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for i in range(25):
 y=-58.5+i*.25
 for z in [-3.7,-3.4,-3.1,-2.9,-2.7,-2.5,-2.3,-2.1,-1.9]:
  h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((48.8,y,z)),Vector((1,0,0)),distance=2.2)
  if h:rows.append(dict(y=y,z=z,x=p.x,normal=list(n)))
(R/'reports/R560_RETURN_FACE_CONTROLS.json').write_text(json.dumps(rows,indent=2));print('FACE CONTROLS',len(rows),flush=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=900;s.render.resolution_y=650;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(40,-61,3));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((50,-55,-2.5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=15;s.render.filepath=str(R/'renders/qa/R560_return_source.png');bpy.ops.render.render(write_still=True)
