from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R195_KALE_BATI_BAGLANTI_v001.blend'))
domains=json.loads((R/'config/r180_track_beds.json').read_text())+json.loads((R/'config/r178_roof_planes.json').read_text())
def inside(x,y,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
removed=[]
for o in list(bpy.data.objects):
 if not o.name.startswith('R157_TREE_'):continue
 x,y,_=o.matrix_world.translation
 matches=[r.get('name','station_roof') for r in domains if inside(x,y,r['xy'])]
 if matches:removed.append(dict(name=o.name,root=list(o.matrix_world.translation),intersections=matches));bpy.data.objects.remove(o,do_unlink=True)
(R/'reports/R197_STATION_CLEARANCE.json').write_text(json.dumps(dict(accepted=False,removed_roots=removed,scope='Only trunks inside mapped rail beds or measured station roof footprint; surrounding forest retained',limits=['Crown overhang outside root footprint retained','Station ground/edge source comparison still required']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R197_ISTASYON_TEMIZ_KORIDOR_v001.blend'),compress=True)
s=bpy.context.scene;t=Vector((-290,235,-10));s.camera.location=t+Vector((-80,-90,70));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=100;s.render.filepath=str(R/'renders/qa/R197_station_clearance_v001.png');bpy.ops.render.render(write_still=True)
print('CLEARED',len(removed),flush=True)
