import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R301_ALT_MAHALLE_ZEMIN_BAGLANTISI_ADAY_v001.blend'));dg=bpy.context.evaluated_depsgraph_get();hits=[]
for x in range(-216,-163,2):
 for y in range(-140,-110,2):
  ok,p,n,fi,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,100)),Vector((0,0,-1)),distance=300)
  if ok:hits.append(dict(x=x,y=y,z=p.z,name=o.name))
(R/'reports/R302_COURT_RAYS.json').write_text(json.dumps(hits));bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'));s=bpy.context.scene;s.camera.location=(-155,-125,170);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=300;s.render.resolution_x=1400;s.render.resolution_y=1400;s.render.resolution_percentage=100;s.cycles.samples=4;s.render.filepath=str(R/'renders/qa/R302_fort_wide_source.png');bpy.ops.render.render(write_still=True)
