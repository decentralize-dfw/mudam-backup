"""Current full-scene route check, independent of superseded R28 object names."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];r=json.loads((B/'reports'/args[0]).read_text());P=json.loads((B/'config/ground_gallery_access.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);up=Vector((0,0,1));rows=[]
def hit(a,b):
 h=t.ray_cast(a,(b-a).normalized(),(b-a).length)
 return None if h[0] is None else owners[h[2]]
for name,ends in P['routes'].items():
 a,b=map(pt,ends);normal=(b-a).normalized().cross(up)
 for offset in [-.35,0,.35]:
  for h in [.3,1.5,2.1]:
   ob=hit(a+normal*offset+up*h,b+normal*offset+up*h);rows.append(dict(route=name,kind='passage',offset=offset,height=h,object=ob,passed=ob is None))
  for f in [0,.2,.4,.6,.8,1]:
   p=a+(b-a)*f+normal*offset+up*.04;floor=hit(p,p-up*.09);head=hit(p,p+up*2.06);rows.append(dict(route=name,kind='support_headroom',offset=offset,fraction=f,floor=floor,head=head,passed=floor is not None and head is None))
q=dict(file=r['file'],checks=rows,failures=[x for x in rows if not x['passed']],construction_acceptance=False,limits=['Registered four ground gallery routes only; 0.7m sampled width is not a code clearance certification.','Uses active evaluated geometry, including replacements for retired R28 walls.'])
(B/'reports'/args[1]).write_text(json.dumps(q,indent=2));print(len(rows),'route checks',len(q['failures']),'failures');assert not q['failures'],q['failures']
