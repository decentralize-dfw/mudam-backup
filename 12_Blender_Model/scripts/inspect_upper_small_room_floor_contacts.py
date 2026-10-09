"""Probe floor just inside actual upper small-room wall faces, beyond schematic bounds.

This covers the blind spot that allowed the R105 contact gap to survive a room grid.
"""
from pathlib import Path
import bpy,json,math,sys,re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();P={'source_polygons_canonical':{'STUDIO':json.loads((B/'config/upper_studio.json').read_text())['inner_polygon'],'READING':json.loads((B/'config/reading_room.json').read_text())['room_inner_polygon'],'DOCUMENTATION_EAST':json.loads((B/'reports/R96_build_report.json').read_text())['documentation_east_room']}};C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
def pt(p):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy
 return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,0))
def inside(p,poly):
 yes=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:yes=not yes
 return yes
vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);rows=[];total=0;up=Vector((0,0,1));UP=4.859074784676
for side,coords in P['source_polygons_canonical'].items():
 coords=[p[:] for p in coords]
 poly=list(map(pt,coords))
 for ei,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  axis=(b-a).normalized();normal=axis.cross(up)
  if inside((a+b)/2+normal*.02,poly):normal=-normal
  steps=math.ceil((b-a).length/.1)
  for i in range(steps):
   d=(i+.5)/steps*(b-a).length
   if d<.2 or (b-a).length-d<.2:continue
   p=a+axis*d+up*(UP+1.3);start=p-normal*2
   if not inside(start,poly):continue
   hit=t.ray_cast(start,normal,4)
   if hit[0] is None or abs(hit[1].z)>.05:continue
   q=hit[0]-normal*.015
   for label,z,direction in [('floor',UP+.03,-up)]:
    total+=1;q.z=z;h=t.ray_cast(q,direction,.12)
    if h[0] is None:rows.append(dict(side=side,edge=ei,distance_along=d,kind=label,wall=owners[hit[2]],position=list(q),wall_surface=list(hit[0]),surface_normal=list(normal)))
revision='R'+re.search(r'_R(\d+)_',r['file'])[1];q=dict(file=r['file'],checks=total,findings=rows,construction_acceptance=False,limits=['Local15mm inward probes against actual wall faces, not room-grid bounds.','Windows/recesses and genuine high portals can lack a floor/ceiling at these levels and require source classification.','Wall search range4m; missing walls are a separate diagnostic.'])
(B/'reports'/f'{revision}_upper_small_room_floor_contacts.json').write_text(json.dumps(q,indent=2));counts={}
for x in rows:counts[(x['side'],x['kind'],x['wall'])]=counts.get((x['side'],x['kind'],x['wall']),0)+1
print(total,'checks',len(rows),'review candidates',counts)
