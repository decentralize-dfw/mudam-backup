from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v070.blend'));o=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];me=o.data;before=np.array([tuple(v.co) for v in me.vertices]);after=before.copy();roofids={i for f in me.polygons[:35200] for i in f.vertices};roofpos={tuple(np.round(before[i],5)) for i in roofids};moved=[]
for v in me.vertices:
 if v.index in roofids or tuple(np.round(before[v.index],5)) in roofpos or v.co.z<-71.2:continue
 h,n,idx,dist=tree.find_nearest(v.co)
 if h and .005<dist<.6 and abs(n.z)<.75 and abs(n.dot(v.normal))>.65:after[v.index]=h;moved.append(v.index)
groups={}
for i,p in enumerate(before):groups.setdefault(tuple(np.round(p,6)),[]).append(i)
for ids in groups.values():
 if len(ids)>1 and not np.allclose(after[ids],after[ids[0]],atol=1e-7):after[ids]=before[ids]
lookup={i:ids for ids in groups.values() for i in ids}
me.calc_loop_triangles();tris=np.array([t.vertices for t in me.loop_triangles]);oldcross=np.cross(before[tris[:,1]]-before[tris[:,0]],before[tris[:,2]]-before[tris[:,0]])
reverted=set()
for _ in range(8):
 cross=np.cross(after[tris[:,1]]-after[tris[:,0]],after[tris[:,2]]-after[tris[:,0]]);bad=(np.einsum('ij,ij->i',oldcross,cross)<=0)|(np.linalg.norm(cross,axis=1)<1e-8)
 if not bad.any():break
 ids=np.array(sorted({j for i in np.unique(tris[bad]) for j in lookup[int(i)]}));after[ids]=before[ids];reverted.update(ids.tolist())
for v in me.vertices:v.co=after[v.index]
me.update();delta=np.linalg.norm(after-before,axis=1);report=dict(projected_vertices=int(np.sum(delta>1e-5)),max_move_m=float(delta.max()),reverted_for_triangle_orientation=len(reverted),roof_unchanged=bool(np.all(after[list(roofids)]==before[list(roofids)])),accepted=False,scope='Only nearby compatible visible source facade planes; roof and bottom vertices fixed.');(R/'reports/R169_FACADE_PROJECTION_v071.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v071.blend'),compress=True);print(report)

