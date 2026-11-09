import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];eye=Vector((-80,0,35));direction=(Vector((-48,37,-5))-eye).normalized();rot=direction.to_track_quat('-Z','Y');right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));out={}
for label,path in [('source','.local_source_cache/r316/museum_ring_reference.blend'),('candidate','scenes/MUDAM_R508_BATI_KULE_EKSEN_ZEMIN_ADAY_v001.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/path));dg=bpy.context.evaluated_depsgraph_get();rows=[]
 for py in [250,350,450,550,650,700,750]:
  for px in range(520,851,10):
   origin=eye+right*((px/1000-.5)*43)+up*((.5-py/1000)*43);h,p,n,*rest=bpy.context.scene.ray_cast(dg,origin,direction,distance=200)
   if h:rows.append(dict(pixel=[px,py],position=list(p),normal=list(n),object=rest[1].name))
 out[label]=rows
(R/'reports/R509_NW_WALL_SCREEN_SECTIONS.json').write_text(json.dumps(out,indent=2))
