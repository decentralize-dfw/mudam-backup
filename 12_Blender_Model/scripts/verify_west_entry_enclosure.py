"""R82 inspect retained floor, added cover/sides and open stair entry."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R82_build_report.json').read_text());C=json.loads((B/'config/foundation.json').read_text())['calibration'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));up=Vector((0,0,1));fail=[];solids=[];trees={}
def point(u,v,z=0):
 x=(u+v)/2;y=(u-v)/2;k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
for name in r['closed_objects']+['R14_GROUND_ENTRY']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();solids.append(dict(name=name,volume_m3=vol,nonmanifold_edges=bad));trees[name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(f.vertices) for f in ob.data.polygons])
 if bad or vol<=0:fail.append(solids[-1])
samples=[];ev=(point(0,1)-point(0,0)).normalized()
for u in range(1122,1173,2):
 for v in range(580,604,2):
  p=point(u,v,1.2);down=trees['R14_GROUND_ENTRY'].ray_cast(p,-up,2)[0] is not None;roof=trees['R82_ENTRY_GLASS_1'].ray_cast(p,up,3)[0] is not None
  if not down or not roof:fail.append(dict(u=u,v=v,floor=down,roof=roof))
  samples.append(dict(u=u,v=v,floor=down,roof=roof))
 for z in [.1,1.2,3.0]:
  for name,v,normal in [('R82_ENTRY_GLASS_0',604,ev),('R82_ENTRY_INNER_WALL',578,-ev)]:
   hit=trees[name].ray_cast(point(u,v,z)-normal*.4,normal,.8)[0] is not None
   if not hit:fail.append(dict(name=name,u=u,z=z))
# No glazing or wall across the connection axis.
a=point(1116,591,1.2);b=point(1180,591,1.2);d=(b-a).normalized();obstacles=[n for n,t in trees.items() if t.ray_cast(a,d,(b-a).length)[0] is not None]
if obstacles:fail.append(dict(entry_obstructions=obstacles))
q=dict(file=r['file'],solids=solids,cover_floor_samples=len(samples),side_samples=26*6,entry_obstructions=obstacles,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R82_verification.json').write_text(json.dumps(q,indent=2),encoding='utf8');print('R82',len(samples),'floor/cover',len(fail),'failures');assert not fail,fail
