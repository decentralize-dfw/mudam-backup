from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(r'C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');C=json.loads((B/'config/foundation.json').read_text())['calibration'];q=json.loads((B/'reports/KABUK_SIK_TARAMA.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/q['file']));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or not o.visible_get() or o.get('level_id')=='SITE':continue
 eo=o.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(o.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);rows=[]
for shift in [-.2,-.05,0,.05,.2]:
 for angle in [44,44.9,45,45.1,46]:
  a=math.radians(angle);v=pt(587+shift,689,1.2);h=t.ray_cast(v,Vector((math.cos(a),math.sin(a),0)),200);rows.append(dict(shift_px=shift,angle=angle,hit=None if h[0] is None else owners[h[2]],distance=h[3]))
(B/'reports/R101_entry_escape_diagnostic.json').write_text(json.dumps(dict(file=q['file'],rows=rows,construction_acceptance=False),indent=2));print(json.dumps(rows,indent=2))
