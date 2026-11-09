from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r169/source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in f.vertices] for f in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);cam=Vector((-80,-285,-48));rot=(Vector((-67,-299,-64))-cam).to_track_quat('-Z','Y');hits=[]
pixels=[(265,630),(347,646),(281,592),(382,622),(433,689),(548,720),(468,665),(582,696)]
for x,y in pixels:
 start=cam+rot@Vector(((x-600)/60,(500-y)/60,0));h,*_=tree.ray_cast(start,rot@Vector((0,0,-1)),100);assert h is not None;hits.append(list(h))
print(list(zip(pixels,hits)))
(R/'.local_source_cache/r169/rear_feature_corners_v047.json').write_text(json.dumps(dict(pixels=pixels,hits=hits)))
