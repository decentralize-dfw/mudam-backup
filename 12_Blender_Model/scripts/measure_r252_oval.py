import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r171/north_reference.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();k=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([k+j for j in t.vertices] for t in o.data.loop_triangles)
g=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def xy(p):return [277.5+p[0]*85/1400,440.5-p[1]*85/1400]
def h(p):
 q=xy(p);hit,n,*_=g.ray_cast(Vector((*q,100)),Vector((0,0,-1)),200);return float(hit.z) if hit else None
outer=[(215,390),(355,355),(348,300),(382,245),(430,225),(478,225),(530,245),(570,160),(655,213),(750,305),(850,419),(948,570),(1025,700),(1095,820),(1155,1010),(1045,1040),(1065,1100),(1035,1150),(990,1180),(940,1190),(892,1165),(829,1240),(740,1170),(630,1050),(522,920),(430,785),(356,650),(280,500)]
roofsamples=[(320,450),(410,600),(480,740),(580,890),(680,1030),(790,1130),(655,310),(780,450),(925,650),(1020,850),(1090,970)]
# Independently traced skylight cross-sections, left and right eaves from plan.
stations=[[(438,350),(487,319)],[(459,437),(566,387)],[(502,562),(695,493)],[(572,697),(802,618)],[(676,850),(900,774)],[(800,992),(965,923)],[(921,1071),(978,1033)]]
rows=[]
for pair in stations:
 a,b=[np.array(v,dtype=float) for v in pair];mid=(a+b)/2
 rows.append(dict(left=xy(a),right=xy(b),leftZ=h(a),ridgeZ=h(mid),rightZ=h(b)))
out=dict(outer=[xy(p) for p in outer],roofObservations=[dict(pixel=p,z=h(p)) for p in roofsamples],sections=rows,limits=['Manual architectural plan trace; sampled heights only; no source triangles reused'])
(R/'config/r252_oval_architecture.json').write_text(json.dumps(out,indent=2));print(out,flush=True)
