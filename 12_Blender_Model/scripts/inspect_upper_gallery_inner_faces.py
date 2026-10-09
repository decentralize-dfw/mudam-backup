"""Find visible inherited geometry ahead of the registered upper gallery faces."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if args:r=json.loads((B/'reports'/args[0]).read_text())
P=json.loads((B/'config/upper_gallery_room.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=4.859074784676
bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);rows=[];total=0;up=Vector((0,0,1))
for side,coords in P['source_polygons_canonical'].items():
 poly=list(map(pt,coords));center=sum(poly,Vector())/len(poly)
 for ei,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  axis=(b-a).normalized();normal=axis.cross(up)
  if normal.dot((a+b)/2-center)<0:normal=-normal
  spec=next((p for p in P['portals'] if p['side']==side and p['edge']==ei),None)
  door=sorted((pt(p)-a).dot(axis) for p in spec['ends']) if spec else None
  steps=math.ceil((b-a).length/.1)
  for i in range(steps):
   d=(i+.5)/steps*(b-a).length
   if d<.35 or (b-a).length-d<.35:continue
   for h in [.2,1.3,2.4,2.7,3,3.15,3.3,5.8]:
    if door and door[0]-.1<d<door[1]+.1 and h<spec['head']+.05:continue
    p=a+axis*d+up*(UP+h);start=p-normal*.6;hit=t.ray_cast(start,normal,1.2);total+=1
    if hit[0] is None or hit[3]<.57:
     rows.append(dict(side=side,edge=ei,distance_along=d,z=UP+h,source_point=list(p),normal=list(normal),object=None if hit[0] is None else owners[hit[2]],protrusion=None if hit[0] is None else .6-hit[3],hit=None if hit[0] is None else list(hit[0])))
q=dict(file=r['file'],checks=total,findings=rows,construction_acceptance=False,limits=['Only five height samples on source gallery inner faces; portal apertures and corners excluded.','A hit is a review candidate, not automatic permission to remove geometry.'])
(B/'reports'/('R103_upper_gallery_inner_faces.json' if args else 'R102_upper_gallery_inner_faces.json')).write_text(json.dumps(q,indent=2));counts={}
for x in rows:counts[x['object']]=counts.get(x['object'],0)+1
print(total,'checks',len(rows),'review findings',counts)
