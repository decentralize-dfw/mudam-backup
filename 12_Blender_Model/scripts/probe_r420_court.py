import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R419_GUNEY_KULE_AVLU_CEPHESI_ADAY_v001.blend'));s=bpy.context.scene;bpy.ops.object.camera_add(location=(-53,-47,4.6));cam=bpy.context.object;cam.rotation_euler=(Vector((-57.4,-63.1,3.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=35;s.camera=cam;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();frame=cam.data.view_frame(scene=s);out=[]
for px,py in [(750,429),(710,436),(300,436),(780,550),(660,500)]:
 # Camera frame upper-right, lower-right, lower-left, upper-left.
 xs=[v.x for v in frame];ys=[v.y for v in frame];z=frame[0].z;v=Vector((min(xs)+(max(xs)-min(xs))*px/1000,max(ys)-(max(ys)-min(ys))*py/800,z));dr=cam.matrix_world.to_3x3()@v.normalized();origin=cam.location.copy();hits=[]
 for o in s.objects:
  if o.type!='MESH' or o.hide_render:continue
  inv=o.matrix_world.inverted();ev=o.evaluated_get(dg);hit,loc,no,fi=ev.ray_cast(inv@origin,inv.to_3x3()@dr)
  if hit:hits.append((o.name,(o.matrix_world@loc-origin).length,tuple(o.matrix_world@loc)))
 out.append(dict(pixel=[px,py],hits=sorted(hits,key=lambda h:h[1])[:5]))
(R/'reports/R420_COURT_INTRUSION_DIAGNOSTIC.json').write_text(json.dumps(out,indent=2));print(out)
