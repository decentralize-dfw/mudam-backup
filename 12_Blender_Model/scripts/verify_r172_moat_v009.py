import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_HENDEK_ADAY_v009.blend'));row=next(r for r in json.loads((R/'reports/R172_TERRACES_v003.json').read_text())['terraces'] if r['name']=='MOAT_EAST');out=[]
for p in row['sourceSamples']:
 hits=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name.startswith(('R154_FAR','R161_ROAD','R172_')):continue
  inv=o.matrix_world.inverted();hit,loc,n,i=o.ray_cast(inv@Vector((p[0],p[1],100)),inv.to_3x3()@Vector((0,0,-1)),distance=300)
  if hit:hits.append([o.name,(o.matrix_world@loc).z])
 out.append({'sample':p,'hits':sorted(hits,key=lambda r:r[1],reverse=True)})
(R/'reports/R172_MOAT_v009_REOPEN.json').write_text(json.dumps(out,indent=2));print(out)
