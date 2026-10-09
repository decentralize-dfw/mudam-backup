"""Check existing pavilion lantern rod frame ends against actual evaluated steel profiles."""
from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R109_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));deps=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or not ob.name.startswith('R13_FRAME_') or '_FRAME_' not in ob.name:continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for face in me.polygons:fs.append(tuple(off+i for i in face.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);rows=[]
for ob in bpy.context.scene.objects:
 if not ob.name.startswith('R13_TOWER_X_'):continue
 ps=[ob.matrix_world@v.co for v in ob.data.vertices];n=len(ps)//2
 for i,ring in enumerate([ps[:n],ps[n:]]):
  p=sum(ring,Vector())/n;hit=t.find_nearest(p);radius=max((v-p).length for v in ring);signed=(p-hit[0]).dot(hit[1]);rows.append(dict(name=ob.name,end=i,endpoint=list(p),nearest_frame=owners[hit[2]],nearest_distance=hit[3],signed_distance=signed,review_gap=max(0,signed-radius)))

q=dict(file=r['file'],checks=rows,findings=[x for x in rows if x['review_gap']>.002],construction_acceptance=False,limits=['Nearest-surface signed distance at intended frame attachment; intersections and weld/fastener design are separate.','Inherited widths and rod diameters remain representative.']);(B/'reports/R109_pavilion_rod_contacts.json').write_text(json.dumps(q,indent=2));print(len(rows),'contacts',len(q['findings']),'gaps');print(json.dumps(q['findings'][:8],indent=2))
