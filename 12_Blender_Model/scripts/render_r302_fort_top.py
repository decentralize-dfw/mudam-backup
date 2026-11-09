from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
for key,path in [('source','.local_source_cache/r171/fort_reference.blend'),('authored','scenes/MUDAM_R301_ALT_MAHALLE_ZEMIN_BAGLANTISI_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));s=bpy.context.scene;s.camera.location=(-190,-165,170);s.camera.rotation_euler=(0,0,0);s.camera.data.type='ORTHO';s.camera.data.ortho_scale=210;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=4;s.render.filepath=str(R/f'renders/qa/R302_fort_top_{key}.png');bpy.ops.render.render(write_still=True)
 if key=='authored':
  rows=[]
  for o in s.objects:
   if o.type!='MESH':continue
   p=[o.matrix_world@Vector(v) for v in o.bound_box]
   if min(v.x for v in p)<-160 and max(v.x for v in p)>-220 and min(v.y for v in p)<-110 and max(v.y for v in p)>-145:rows.append(dict(name=o.name,bounds=[[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]))
  (R/'reports/R302_NORTH_COURT_OBJECTS.json').write_text(json.dumps(rows,indent=2))
