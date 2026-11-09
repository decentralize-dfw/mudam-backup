import bpy,json,bmesh
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R275_AVLU_ZEMIN_BIRLESIM_ADAY_v001.blend'))
regions=[[(82.45,389.866667),(90.033333,397.2),(99.533333,386.2),(92.033333,379.7)],[(155.65,453.216667),(163.233333,460.55),(172.733333,449.55),(165.233333,443.05)]]
def inside(p,poly):
 cs=[(poly[(i+1)%4][0]-a[0])*(p.y-a[1])-(poly[(i+1)%4][1]-a[1])*(p.x-a[0]) for i,a in enumerate(poly)];return min(cs)>=0 or max(cs)<=0
removed=[]
for o in list(bpy.context.scene.objects):
 if not o.name.startswith('R158_TREE_'):continue
 pts=[o.matrix_world@Vector(c) for c in o.bound_box];center=sum(pts,Vector())/8
 if not any(inside(center,p) for p in regions):continue
 removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
path=R/'scenes/MUDAM_R276_AVLU_BITKI_CAKISMA_TEMIZLIGI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.camera.location=(92.7,387.2,100);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=20;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R276_left_court_authored.png');bpy.ops.render.render(write_still=True)
(R/'reports/R276_COURT_VEGETATION.json').write_text(json.dumps(dict(removed=removed,reason='Previously procedural tree centers inside authored roof footprints; source roof vegetation retained as roof material',accepted=False,published=False),indent=2));print('R276_READY',removed,flush=True)
