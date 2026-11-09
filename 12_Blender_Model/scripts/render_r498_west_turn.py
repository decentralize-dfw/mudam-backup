import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for label,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('candidate','scenes/MUDAM_R497_ARAZI_YUZEY_NORMAL_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100
 bpy.ops.object.camera_add(location=(49,-55,50));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((49,-55,-3))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/f'renders/qa/R498_west_turn_{label}.png');bpy.ops.render.render(write_still=True)
 dg=bpy.context.evaluated_depsgraph_get();out=[]
 for y in [-58.5,-58,-57.5,-57,-56.5,-56,-55.5,-55,-54.5,-54,-53.5,-53]:
  row=[]
  for x in [48,48.5,49,49.5,50,50.5,51]:
   h,p,n,*rest=s.ray_cast(dg,Vector((x,y,20)),Vector((0,0,-1)),distance=50);row.append(dict(x=x,z=p.z if h else None,normal=list(n) if h else None))
  out.append(dict(y=y,section=row))
 (R/f'reports/R498_west_turn_{label}.json').write_text(json.dumps(out,indent=2))
