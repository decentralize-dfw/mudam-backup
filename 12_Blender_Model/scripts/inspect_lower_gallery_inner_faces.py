"""Review basement boundaries against their registered source104 traces."""
from pathlib import Path
import bpy,json,math,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();P=json.loads((B/'config/lower_gallery_rooms.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];LOW=-5.326293513972
bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
def pt(p):
 x,y=p;s,dx,dy=C['basement_registration']['source_to_canonical'];x=s*x+dx;y=s*y+dy;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);rows=[];total=0;up=Vector((0,0,1));outside_starts=0
def inside(p,poly):
 yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:yes=not yes
 return yes
for side,coords in P['rooms'].items():
 poly=list(map(pt,coords));center=sum(poly,Vector())/len(poly)
 for ei,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  axis=(b-a).normalized();normal=axis.cross(up)
  if normal.dot((a+b)/2-center)<0:normal=-normal
  steps=math.ceil((b-a).length/.1)
  for i in range(steps):
   f=(i+.5)/steps;d=f*(b-a).length
   if d<.2 or (b-a).length-d<.2:continue
   native_y=coords[ei][1]+(coords[(ei+1)%len(coords)][1]-coords[ei][1])*f
   if ((side=='E' and ei==1) or (side=='W' and ei==len(poly)-1)) and native_y>392:continue
   for h in [.2,1.3,2.4,3.6,4.55]:
    p=a+axis*d+up*(LOW+h);start=p-normal*2
    if not inside(start,poly):outside_starts+=1;continue
    hit=t.ray_cast(start,normal,2.6);total+=1
    if hit[0] is None or hit[3]<1.97:
     rows.append(dict(side=side,edge=ei,distance_along=d,z=LOW+h,source_point=list(p),normal=list(normal),object=None if hit[0] is None else owners[hit[2]],protrusion=None if hit[0] is None else 2-hit[3]))
known=[x for x in rows if x['object'] in ['R07_STAIRWELL_STONE_WEST','R29_W_DIVIDER_END']];unclassified=[x for x in rows if x not in known]
q=dict(file=r['file'],checks=total,outside_source_polygon_starts_excluded=outside_starts,findings=rows,known_R76_registration_offsets=known,unclassified=unclassified,construction_acceptance=False,limits=['Five elevations; source104 door approaches excluded. Source registration and heights remain candidates.','R76 deliberately reconciled the source104 schematic divider to the adjoining R07 wall. Do not move that wall back based solely on the old floor outline.','A remaining 50mm back-face step between R07 and R29 is separately addressed in R104; source axes stay fixed.','Findings require comparison with individual wall source evidence; no automatic deletion.'])
(B/'reports/R103_lower_gallery_inner_faces.json').write_text(json.dumps(q,indent=2));counts={}
for x in rows:counts[x['object']]=counts.get(x['object'],0)+1
print(total,'checks',len(rows),'review findings',counts)
