from pathlib import Path
import bpy,bmesh,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R170_KAYNAK_ADA_BORDUR_ADAY_v002.blend'));vs=[];fs=[]
for o in bpy.context.scene.objects:
 if o.name not in ['R152_CLASS2_TERRAIN','R154_FAR_GROUND']:continue
 o.data.calc_loop_triangles();off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend([off+i for i in t.vertices] for t in o.data.loop_triangles)
tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEK_BINA_ADAY_v068.blend'));o=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];bm=bmesh.new();bm.from_mesh(o.data);edges=[e for e in bm.edges if e.is_boundary];points={tuple(v.co) for e in edges for v in e.verts if v.co.z<-71};clear=[];missing=0
for p in points:
 h,*_=tree.ray_cast(Vector((p[0],p[1],100)),Vector((0,0,-1)),250)
 if h:clear.append(p[2]-h.z)
 else:missing+=1
r=dict(boundary_edges=len(edges),bottom_points=len(points),missing_ground=missing,maximum_air_gap_m=max(clear),minimum_clearance_m=min(clear),floating_points=sum(x>.02 for x in clear),scope='Existing R170 terrain at actual bottom boundary coordinates; open underground bottom is not a facade opening.');(R/'reports/R169_GROUND_CONTACT_v068.json').write_text(json.dumps(r,indent=2));print(r)
