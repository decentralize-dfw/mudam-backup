from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';b=json.loads((R/'config/r169_building_targets.json').read_text())['buildings'][2];p=[Vector((x,y,0)) for x,y in b['rings'][0][:-1]];t=(p[1]-p[0]).normalized();inside=Vector((t.y,-t.x,0));out=-inside;right=Vector((-out.y,out.x,0));center=(p[0]+p[1])/2
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in tr.vertices] for tr in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);hits=[]
for x in [525,690,905,1080]:
 for y in [540,560,580]:
  target=center+right*((x-800)*.01)+Vector((0,0,b['base']+10+(500-y)*.01));h,*_=tree.ray_cast(target+out*10,inside,20)
  if h is not None:hits.append(dict(pixel=[x,y],offset=(h-center).dot(inside)))
result=dict(offset=float(np.median([h['offset'] for h in hits])),hits=hits,center=list(center),inside=list(inside),right=list(right),base=b['base']);(D/'row_upper_wall_plane.json').write_text(json.dumps(result,indent=2));print('WALL_PLANE',result,flush=True)
