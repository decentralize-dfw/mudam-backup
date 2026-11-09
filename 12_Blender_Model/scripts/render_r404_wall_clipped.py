import bpy,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));s=bpy.context.scene
for ob in list(s.objects):
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);bad=[]
 for f in bm.faces:
  q=ob.matrix_world@f.calc_center_median()
  if q.x-q.y>9 or q.z>5 or q.x+q.y < -119 or q.x+q.y > -61:bad.append(f)
 bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(ob.data);bm.free()
bpy.ops.object.camera_add(location=(0,-90,-.5));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-39,-42,-.5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=55;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1600;s.render.resolution_y=800;s.render.resolution_percentage=100;s.render.filepath=str(R/'renders/qa/R404_fort_east_wall_source_clipped.png');bpy.ops.render.render(write_still=True)
