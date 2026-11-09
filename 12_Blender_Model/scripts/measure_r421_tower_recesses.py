import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();trees=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':trees.append((o,BVHTree.FromObject(o,dg)))
cx,cy=-57.4,-63.1;rows=[]
for angle in range(0,360):
 a=math.radians(angle);n=Vector((math.cos(a),math.sin(a),0));values=[]
 for z in [2.2,2.5,2.8,3.1,3.4,3.7]:
  origin=Vector((cx,cy,z))+n*6;hits=[]
  for o,t in trees:
   inv=o.matrix_world.inverted();loc,no,idx,dist=t.ray_cast(inv@origin,inv.to_3x3()@(-n),4)
   if loc is not None:
    p=o.matrix_world@loc;hits.append((p-origin).length)
  values.append(None if not hits else 6-min(hits))
 rows.append(dict(angle=angle,radii=values))
(R/'reports/R421_SOUTH_RADIAL_MEASUREMENTS.json').write_text(json.dumps(dict(method='Radial measurement of source only; no source geometry transferred',heights=[2.2,2.5,2.8,3.1,3.4,3.7],rows=rows),indent=2));print('DONE')
