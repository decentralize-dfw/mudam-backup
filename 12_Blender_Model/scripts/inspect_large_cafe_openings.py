"""Locate the visible large horizontal discontinuities; does not alter the scene."""
from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1]
r=json.loads((B/'reports/R109_build_report.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
C=json.loads((B/'config/foundation.json').read_text())['calibration']
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
eye=pt(810,245,1.7);rot=(pt(755,340,4)-eye).to_track_quat('-Z','Y');dep=bpy.context.evaluated_depsgraph_get();rows=[]
for x,y in [(200,300),(200,365),(200,415),(200,480),(325,450),(390,480),(400,600),(600,520)]:
 direction=rot@Vector(((x/1400-.5)*36,(.5-y/1050)*27,-20));direction.normalize();p=eye.copy();hits=[]
 for i in range(12):
  ok,loc,n,idx,o,m=bpy.context.scene.ray_cast(dep,p,direction,distance=100)
  if not ok:break
  hits.append(dict(name=o.name,point=list(loc),distance=(loc-eye).length))
  p=loc+direction*.01
 rows.append(dict(pixel=[x,y],hits=hits))
names={h['name'] for row in rows for h in row['hits']};objects=[]
for name in names:
 o=bpy.data.objects[name]
 objects.append(dict(name=name,vertices=[list(o.matrix_world@v.co) for v in o.data.vertices] if len(o.data.vertices)<100 else [],properties={k:str(v) for k,v in o.items()}))
out=dict(file=r['file'],rays=rows,objects=objects)
(B/'reports/R109_large_cafe_openings.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(rows))
