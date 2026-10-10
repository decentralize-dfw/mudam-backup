from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R161_YOL_BAGLANTILARI_WKI_THOMAS_MORE_v001.blend'))
vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name in ('R152_CLASS2_TERRAIN','R154_FAR_GROUND'):
  o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([[off+k for k in t.vertices] for t in o.data.loop_triangles])
bvh=BVHTree.FromPolygons(vs,fs,all_triangles=True);buried=[];count=0
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('R152_PATH_','R154_FAR_ROADS','R161_ROAD_CONNECTIONS')):continue
 for p in o.data.polygons:
  c=o.matrix_world@p.center;hit,_,_,_=bvh.ray_cast(Vector((c.x,c.y,170)),Vector((0,0,-1)),500)
  count+=1
  if hit and hit.z-c.z>.03:buried.append([o.name,p.index,hit.z-c.z])
(R/'reports/R161_ROAD_OCCLUSION.json').write_text(json.dumps(dict(samples=count,buried_faces=len(buried),max_depth=max([x[2] for x in buried],default=0),examples=buried[:20]),indent=2));print('ROAD_CHECK',count,len(buried),flush=True)
