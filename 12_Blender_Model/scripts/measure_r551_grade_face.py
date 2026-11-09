import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();c=json.loads((R/'reports/R548_SLOPE_PLANES.json').read_text())['coefficients'];rows=[]
for i in range(27):
 x=-26.5+i*.5;top=c[0]*x+c[1]*1+c[2]+c[3]*max(x+20,0)+c[4]*max(x+16,0)
 for j in range(4):
  z=-7.25+j*(top-.5+7.25)/3;h,p,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((x,-2,z)),Vector((0,1,0)),distance=5)
  if h:rows.append(dict(x=x,z=z,y=p.y,normal=list(n)))
(R/'reports/R551_NORTH_GRADE_FACE_CONTROLS.json').write_text(json.dumps(rows,indent=2));print(len(rows))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1100;s.render.resolution_y=500;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-20,-15,0));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-20,1,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=22;s.render.filepath=str(R/'renders/qa/R551_north_grade_source.png');bpy.ops.render.render(write_still=True)
