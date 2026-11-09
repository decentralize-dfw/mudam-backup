import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R263_ERASMUS_UC_CEPHE_ADAY_v001.blend'));s=bpy.context.scene;t=Vector((150,440,8));s.camera.location=t+Vector((.6542447*60,-.7562829*60,24));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=200;s.render.resolution_x=3400;s.render.resolution_y=1000;s.render.resolution_percentage=100;bpy.context.view_layer.update();out=[]
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith(('R216_ERASMUS_WING','R217_ERASMUS_WING')):continue
 for p in o.data.polygons:
  if p.normal.dot(Vector((.6542447,-.7562829,0)))<.9:continue
  xyz=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];uv=[world_to_camera_view(s,s.camera,v) for v in xyz];out.append(dict(name=o.name,normal=list(p.normal),points=[list(p) for p in xyz],pixels=[[v.x*2048,(1-v.y)*1000*2048/3400] for v in uv]))
(R/'config/r265_upper_planes.json').write_text(json.dumps(out,indent=2));print(out,flush=True)

