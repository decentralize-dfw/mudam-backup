from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R79_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];up=Vector((0,0,1));fail=[]
def point(p,z=0):
 x,y=p;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def tree(name):
 o=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());me=o.to_mesh();t=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);o.to_mesh_clear();return t
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/r['base_scene']));before=tree('P05_MAIN_ROOF_DECK');before_reading=tree('R39_PUBLIC_CEILING_13');bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));after=tree('P05_MAIN_ROOF_DECK');after_reading=tree('R39_PUBLIC_CEILING_13');solids=[];samples=[]
for name in r['closed_objects']:
 o=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());me=o.to_mesh();bm=bmesh.new();bm.from_mesh(me);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();o.to_mesh_clear();solids.append(q)
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
for side,poly in r['restored_roof_regions'].items():
 a,b,c=map(Vector,poly)
 for i in range(1,20):
  for j in range(1,20-i):
   xy=a+(b-a)*i/20+(c-a)*j/20;p=point(xy,12);old=before.ray_cast(p,up,1);new=after.ray_cast(p,up,1);q=dict(side=side,canonical=list(xy),before_covered=old[0] is not None,after_covered=new[0] is not None);samples.append(q)
   if not q['after_covered']:fail.append(q)
# The old square and the revised cutter have identical north boundaries.
north=[]
for x in range(470,688,16):
 for y in range(342,464,16):
  p=point([x,y],12);a=before.ray_cast(p,up,1)[0] is not None;b=after.ray_cast(p,up,1)[0] is not None;q=dict(canonical=[x,y],before=a,after=b);north.append(q)
  if a!=b:fail.append(q)
reading=[];deps=bpy.context.evaluated_depsgraph_get()
for dx,dy in [(0,0),(-5,0),(5,0),(0,-5),(0,5),(-3,-3),(3,3)]:
 xy=[575+dx,642+dy];p=point(xy,4.7);old=before_reading.ray_cast(p,-up,1)[0] is not None;new=after_reading.ray_cast(p,-up,1)[0] is not None;hit,loc,no,ix,ob,mat=bpy.context.scene.ray_cast(deps,p,-up,distance=8);q=dict(canonical=xy,old_ceiling_blocked=old,new_ceiling_blocked=new,lower_support_name=ob.name if hit else None,lower_support_z=loc.z if hit else None);reading.append(q)
 if not old or new or not hit or abs(loc.z)>.05:fail.append(q)
q=dict(file=r['file'],solids=solids,roof_corner_samples=samples,north_roof_preservation=north,reading_void=reading,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R79_verification.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('R79',len(samples),'roof closure',len(north),'north preservation',len(reading),'reading void',len(fail),'failures');assert not fail,fail
