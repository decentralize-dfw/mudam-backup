from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_R68_PAVYON_HENDEK_KOLU_v001.blend'));r=json.loads((B/'reports/R05_build_report.json').read_text());c=Vector(r['center_world']);ex=Vector(r['canonical_x_world']);ey=Vector(r['canonical_y_world']);ob=bpy.data.objects['R06_FOYER_CEILING_AND_CURVED_FASCIA'];dep=bpy.context.evaluated_depsgraph_get();o=ob.evaluated_get(dep);iv=o.matrix_world.inverted();rows=[]
for i in range(61):
 for j in range(61):
  x=-6+i*.25;y=-6+j*.25;p=c+ex*x+ey*y+Vector((0,0,-2));ok,q,n,k=o.ray_cast(iv@p,iv.to_3x3()@Vector((0,0,1)),distance=3)
  if ok:rows.append(dict(x=x,y=y,z=(o.matrix_world@q).z))
(B/'reports/R69_ceiling_probe.json').write_text(json.dumps(dict(center=list(c),ex=list(ex),ey=list(ey),samples=rows),indent=2),encoding='utf8');print('probe',len(rows))
