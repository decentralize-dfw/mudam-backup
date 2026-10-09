from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R34_build_report.json').read_text());P=json.loads((B/'config/site_bridges.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[]
def point(x,y,z=0):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()
visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def ray(p,q):
 d=(q-p).normalized();hits=[]
 for ob in visible:
  iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@p,iv.to_3x3()@d,distance=(q-p).length)
  if ok:hits.append(ob.name)
 return hits
passages=[];support=[]
for name,(start,end) in r['routes'].items():
 a,b=Vector((*start,0)),Vector((*end,0))
 for h in [.3,1.5,2.05]:
  hits=ray(a+Vector((0,0,h)),b+Vector((0,0,h)));row=dict(route=name,h=h,hits=hits);passages.append(row)
  if hits:fail.append(row)
 for i in range(61):
  p=a.lerp(b,i/60)+Vector((0,0,.04));hits=ray(p,p-Vector((0,0,.09)));head=ray(p,p+Vector((0,0,2.06)));row=dict(route=name,t=i/60,support=hits,head=head);support.append(row)
  if r['deck'] not in hits or head:fail.append(row)
footprints=[]
for id,poly in r['osm_footprints'].items():
 # OSM six-node rectangles retain one collinear point on each outer edge.
 a,b,c,d=map(lambda p:Vector((*p,0)),[poly[0],poly[1],poly[3],poly[4]])
 for i in range(1,10):
  for j in range(1,6):
   p=a.lerp(b,i/10).lerp(d.lerp(c,i/10),j/6)+Vector((0,0,.04));hits=ray(p,p-Vector((0,0,.09)));row=dict(way=id,u=i/10,v=j/6,hits=hits);footprints.append(row)
   if r['deck'] not in hits:fail.append(row)
# Independently ray-cast the retained old entrance mesh, even though superseded/hidden.
old=bpy.data.objects['P07_CANOPY_PAVING_DISPLAY'].evaluated_get(deps);deck=bpy.data.objects[r['deck']].evaluated_get(deps);verts=[old.matrix_world@v.co for v in old.data.vertices];lo=[min(p[k] for p in verts) for k in range(2)];hi=[max(p[k] for p in verts) for k in range(2)];retained=[]
for i in range(21):
 for j in range(21):
  p=Vector((lo[0]+(hi[0]-lo[0])*(i+.5)/21,lo[1]+(hi[1]-lo[1])*(j+.5)/21,.04));iv=old.matrix_world.inverted();hit,loc,no,ix=old.ray_cast(iv@p,iv.to_3x3()@Vector((0,0,-1)),distance=.09)
  if hit:
   iv=deck.matrix_world.inverted();ok,loc,no,ix=deck.ray_cast(iv@p,iv.to_3x3()@Vector((0,0,-1)),distance=.09);retained.append(dict(x=p.x,y=p.y,supported=ok))
   if not ok:fail.append(dict(old_paving_lost=list(p)))
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,passage_rays=passages,support_head_samples=support,footprint_samples=footprints,retained_old_paving_samples=retained,construction_acceptance=False);(B/'reports/R34_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),failures=fail),indent=2));assert not fail,fail
