"""Find solid wall bodies inside source-defined clear upper room interiors."""
from pathlib import Path
import bpy,json,math,re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R102_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];UP=json.loads((B/'reports/R96_build_report.json').read_text())['upper_z'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));deps=bpy.context.evaluated_depsgraph_get();solids=[]
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or not re.search('WALL|PIER|SHAFT|RECESS|JAMB|JOIN',ob.name,re.I):continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();vs=[eo.matrix_world@v.co for v in me.vertices];lo=[min(p[i] for p in vs) for i in range(3)];hi=[max(p[i] for p in vs) for i in range(3)]
 if hi[2]>UP+.4 and lo[2]<UP+2.1:solids.append((ob.name,lo,hi,BVHTree.FromPolygons(vs,[list(f.vertices) for f in me.polygons])))
 eo.to_mesh_clear()
regions=dict(STUDIO=json.loads((B/'config/upper_studio.json').read_text())['inner_polygon'],DOCUMENTATION_EAST=json.loads((B/'reports/R96_build_report.json').read_text())['documentation_east_room'])
regions.update({'GALLERY_'+k:v for k,v in json.loads((B/'config/upper_gallery_room.json').read_text())['source_polygons_canonical'].items()})
def inside(x,y,poly):
 ok=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:ok=not ok
 return ok
def edge_distance(x,y,poly):
 p=Vector((x,y));best=1e9
 for a,b in zip(poly,poly[1:]+poly[:1]):
  a=Vector(a);b=Vector(b);d=b-a;best=min(best,(p-(a+d*max(0,min(1,(p-a).dot(d)/d.length_squared)))).length)
 return best*C['meters_per_canonical_pixel']
rows=[];count=0;direction=Vector((.731,.437,.521)).normalized()
for region,poly in regions.items():
 for x in range(math.ceil(min(p[0] for p in poly))+2,math.floor(max(p[0] for p in poly)),4):
  for y in range(math.ceil(min(p[1] for p in poly))+2,math.floor(max(p[1] for p in poly)),4):
   if not inside(x,y,poly) or edge_distance(x,y,poly)<.4:continue
   for h in [.5,1.2,2.1]:
    p=pt(x,y,UP+h);count+=1
    for name,lo,hi,tree in solids:
     if any(p[i]<lo[i] or p[i]>hi[i] for i in range(3)):continue
     hit=tree.ray_cast(p,direction,100)
     if hit[0] is not None and hit[1].dot(direction)>.001:rows.append(dict(region=region,canonical=[x,y],z=p.z,object=name,distance_to_exit=hit[3]))
q=dict(file=r['file'],samples=count,findings=rows,construction_acceptance=False,limits=['Interior sampling beyond400mm source boundary margin. Hits require source classification before any removal.']);(B/'reports/R102_upper_interior_intrusions.json').write_text(json.dumps(q,indent=2));print(count,'samples',len(rows),'findings');print(sorted(set((x['region'],x['object']) for x in rows)))
