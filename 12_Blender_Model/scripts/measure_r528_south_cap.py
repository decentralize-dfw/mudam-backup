import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];rows=[]
for label,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('candidate','scenes/MUDAM_R525_BATI_TERAS_EGIMLI_KENAR_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));dg=bpy.context.evaluated_depsgraph_get()
 for x in [50,54,58,60,62,66,70]:
  hits=[]
  for k in range(130):
   y=-65+k*.1;h,p,n,i,o,m=bpy.context.scene.ray_cast(dg,Vector((x,y,30)),Vector((0,0,-1)),distance=70)
   if h:hits.append(dict(y=y,z=p.z,nz=n.z,object=o.name))
  rows.append(dict(label=label,x=x,hits=hits));print(label,x,[(round(h['y'],1),round(h['z'],2))for h in hits if -1.6<h['z']<-1.3 and h['nz']>.7],flush=True)
(R/'reports/R528_SOUTH_WALL_CAP_SECTIONS.json').write_text(json.dumps(rows,indent=2))
