"""Read-only floor contact probe for the visible west gallery entry edge."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);rows=[]
for y in [470,480,500,520,540,580,610]:
 for x in [687,688,688.5,689,690,692,695,700]:
  p=pt(x,y,.03);hit=t.ray_cast(p,Vector((0,0,-1)),8)
  rows.append(dict(x=x,y=y,object=None if hit[0] is None else owners[hit[2]],z=None if hit[0] is None else hit[0].z))
(B/'reports/R104_ground_floor_edge.json').write_text(json.dumps(dict(file=r['file'],samples=rows,construction_acceptance=False),indent=2))
print(json.dumps(rows,indent=2))
