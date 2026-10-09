from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R76_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[];solids=[];contacts=[];routes=[];trees={};up=Vector((0,0,1))
def geometry(name):
 o=bpy.data.objects[name];return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
for name in r['closed_objects']:
 o=bpy.data.objects[name];trees[name]=geometry(name);bm=bmesh.new();bm.from_mesh(o.data);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),volume=bm.calc_volume(signed=True),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();solids.append(q)
 if q['nonmanifold'] or q['volume']<=0 or q['zero_faces']:fail.append(q)
for a,b in [('R29_W_DIVIDER_END','R07_STAIRWELL_STONE_WEST'),('R10_UPPER_DIAGONAL_WALL','R73_E_CONTINUOUS_GALLERY_WALL')]:
 overlaps=trees[a].overlap(geometry(b));q=dict(a=a,b=b,intersecting_triangles=len(overlaps),passed=bool(overlaps));contacts.append(q)
 if not overlaps:fail.append(q)
p=json.loads((B/'reports/R23_build_report.json').read_text());door=next(d for d in p['portals'] if d['id']=='E_STAIR');a,b,n=map(Vector,[door['start'],door['end'],door['outward']])
for f in [.1,.25,.5,.75,.9]:
 for h in [.3,1.5,2.2]:
  pos=a.lerp(b,f)+up*(p['upper_z']+h);hits=[name for name,t in trees.items() if t.ray_cast(pos-n*.5,n,1.4)[0] is not None];q=dict(route='E_STAIR',fraction=f,height=h,hits=hits,passed=not hits);routes.append(q)
  if hits:fail.append(q)
for record in r['records']:
 old=record['before_world_vertices'];new=record['after_world_vertices']
 if any(abs(a[2]-b[2])>1e-5 for a,b in zip(old,new)):fail.append(dict(height_changed=record['name']))
result=dict(file=r['file'],solids=solids,contacts=contacts,source_portal_routes=routes,failures=fail,construction_acceptance=False,limits=r['limits']);(B/'reports/R76_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R76',len(solids),'solids',len(contacts),'connections',len(routes),'portal rays',len(fail),'failures');assert not fail,fail
