import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));eye=Vector((90,-105,55));forward=(Vector((28,-36,-3))-eye).normalized();rot=forward.to_track_quat('-Z','Y');right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));dg=bpy.context.evaluated_depsgraph_get();out=[]
for px,py in [(410,510),(430,515),(450,521),(470,527),(490,533),(510,539),(530,545),(550,551),(570,557)]:
 origin=eye+right*((px/800-.5)*75)+up*((.5-py/680)*63.75);h,p,n,*_=bpy.context.scene.ray_cast(dg,origin,forward,distance=250);out.append(dict(pixel=[px,py],position=list(p) if h else None,normal=list(n) if h else None))
(R/'reports/R494_VISIBLE_WALL_CREST.json').write_text(json.dumps(out,indent=2));print(out)
