from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/fort_reference.blend'))
t=Vector((-229.6,-192.1,-18));cam=t+Vector((35,-45,45));rot=(t-cam).to_track_quat('-Z','Y');vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+i for i in tr.vertices] for tr in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
pts=[]
for x,y in [(440,348),(463,477),(593,449)]:
 origin=cam+rot@Vector(((x/1000-.5)*48,(.5-y/850)*48*850/1000,0));h,n,_,_=g.ray_cast(origin,rot@Vector((0,0,-1)),300);pts.append(list(h))
d=dict(points=pts,pixels=[[440,348],[463,477],[593,449]],source='R239_ruin_source.png',method='Three source ray measurements define two independent straight partition walls; no scan mesh transfer',accepted=False)
(R/'config/r239_ruin_partitions.json').write_text(json.dumps(d,indent=2));print(d)
