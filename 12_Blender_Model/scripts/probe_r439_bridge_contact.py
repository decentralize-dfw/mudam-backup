import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R439_KOPRU_BASI_ZEMIN_BAGLANTISI_ADAY_v001.blend'));f=json.loads((R/'.local_source_cache/r154/fort.json').read_text());a=Vector((*f['deck_start'],f['deck_z']));axis=Vector((*f['direction'],0));side=Vector((-axis.y,axis.x,0));obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('R152_PATH_','R152_CLASS2_TERRAIN','R303_','R430_','R431_','R439_'))];rows=[]
for dist in [-2,-1,-.3,0,.3]:
 for off in [-1.1,0,1.1]:
  q=a+axis*dist+side*off;origin=Vector((q.x,q.y,10));hits=[]
  for o in obs:
   inv=o.matrix_world.inverted();hit,loc,no,idx=o.ray_cast(inv@origin,inv.to_3x3()@Vector((0,0,-1)))
   if hit:
    z=(o.matrix_world@loc).z
    if z< f['deck_z']+.1:hits.append((z,o.name))
  rows.append(dict(distance=dist,offset=off,xy=[q.x,q.y],surface=max(hits) if hits else None,deck=f['deck_z']))
(R/'reports/R439_BRIDGE_APPROACH_CONTACT_RAYS.json').write_text(json.dumps(rows,indent=2));print(rows)
