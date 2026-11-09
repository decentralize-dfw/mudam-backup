from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_SUREKLI_SACAK_v085.blend'));vs=[];fs=[];names=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices)
 for t in o.data.loop_triangles:fs.append([off+i for i in t.vertices]);names.append(o.name)
t=BVHTree.FromPolygons(vs,fs,all_triangles=True);m=json.loads((R/'reports/R169_SHELL_COVERAGE_v085.json').read_text())['worst'][0];p=Vector(m['origin']);d=Vector(m['direction'])
for i in range(20,49):
 pos=p+d*(i*.25);loc,n,idx,dist=t.find_nearest(pos);print(round(i*.25,2),tuple(round(a,3) for a in pos),round(dist,3),names[idx])
