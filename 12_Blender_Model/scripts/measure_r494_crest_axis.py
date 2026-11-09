import bpy,json,statistics
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();out=[]
for i in range(45):
 x=50+i*.5;y=-58.9594593663+(x-49.0444505366)*(2.6615917878/23.0864225673)+.55;zs=[]
 for dy in [-.1,0,.1]:
  h,p,*_=bpy.context.scene.ray_cast(dg,Vector((x,y+dy,20)),Vector((0,0,-1)),distance=50)
  if h:zs.append(p.z)
 out.append([x,y,statistics.median(zs) if zs else None])
(R/'reports/R494_CREST_SOURCE_PROFILE.json').write_text(json.dumps(out,indent=2));print([[round(a,3) if a is not None else None for a in p] for p in out])
