import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));s=bpy.context.scene
for ob in list(s.objects):
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bad=[]
 for f in bm.faces:
  q=ob.matrix_world@f.calc_center_median()
  if math.hypot(q.x+57.4,q.y+63.1)>5.4 or q.z<1.2 or q.z>7.5:bad.append(f)
 bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(ob.data);bm.free()
s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=800;s.render.resolution_percentage=100
for label,eye in [('north',(-57.4,-43.1,3.7)),('west',(-77.4,-63.1,3.7))]:
 bpy.ops.object.camera_add(location=eye);s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-57.4,-63.1,3.7))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=12;s.render.filepath=str(R/f'renders/qa/R419_south_tower_{label}_source.png');bpy.ops.render.render(write_still=True)
