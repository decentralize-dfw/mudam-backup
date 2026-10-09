from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';bpy.ops.wm.open_mainfile(filepath=str(B/'scenes/MUDAM_R56_PARK_AGAC_TACI_v002.blend'));E=json.loads((B/'config/entry_package.json').read_text())['entry'];C=json.loads((B/'config/foundation.json').read_text())['calibration']
def xy(p):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];u=k*p[0]+ox;v=k*p[1]+oy;return Vector((M[0][0]*u+M[0][1]*v+M[0][2]-293425,M[1][0]*u+M[1][1]*v+M[1][2]-5499960,0))
a,b=map(xy,E['chain'][3:5]);u=(b-a).normalized();n=(xy([575,816])-xy([575,688])).normalized();mid=(a+b)/2;dep=bpy.context.evaluated_depsgraph_get();obs=[o.evaluated_get(dep) for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o.visible_get()];rows=[]
for x in [-1,-.5,0,.5,1]:
 for d in [.1,.7,1.4,2.1]:
  p=mid+u*x+n*d+Vector((0,0,.025));hits=[]
  for o in obs:
   iv=o.matrix_world.inverted();ok,loc,no,ix=o.ray_cast(iv@p,iv.to_3x3()@Vector((0,0,-1)),distance=.25)
   if ok:hits.append(dict(name=o.name,z=(o.matrix_world@loc).z))
  rows.append(dict(x=x,d=d,hits=hits))
(B/'reports/R57_floor_probe.json').write_text(json.dumps(dict(origin=list(mid),axis=list(u),outward=list(n),samples=rows),indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
