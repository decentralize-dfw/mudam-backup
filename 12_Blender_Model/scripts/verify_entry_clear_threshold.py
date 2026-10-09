from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R64_build_report.json').read_text());O,U,N=map(Vector,[r['origin'],r['axis'],r['outward']]);Z=Vector((0,0,1));fail=[]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));deps=bpy.context.evaluated_depsgraph_get();trees={}
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or ob.name.startswith('P12_LEAF_'):continue
  eo=ob.evaluated_get(deps);me=eo.to_mesh();w=eo.matrix_world.copy();vs=[w@v.co for v in me.vertices];fs=[list(f.vertices) for f in me.polygons];eo.to_mesh_clear()
  if not vs:continue
  pts=[p-O for p in vs];xx=[p.dot(U) for p in pts];dd=[p.dot(N) for p in pts];zz=[p.z for p in pts]
  if min(xx)>1.15 or max(xx)<-1.15 or min(dd)>.22 or max(dd)<-.22 or min(zz)>2.12 or max(zz)<-.04:continue
  trees[ob.name]=BVHTree.FromPolygons(vs,fs)
 return trees
def hits(trees,start,direction,length):
 a=[]
 for name,t in trees.items():
  p,n,i,d=t.ray_cast(start,direction,length)
  if p is not None:a.append(dict(name=name,distance=d,point=list(p)))
 return sorted(a,key=lambda q:q['distance'])
old=snapshot(B/'scenes'/r['base_scene']);before=[]
for i in range(21):
 x=-1.0+i*.10;before.append(hits(old,O+U*x-N*.20+Z*.20,N,.40))
assert all(any(q['name']=='ENT-02-L00_FRAME_SILL' for q in a) for a in before),'Regression must detect former obstruction'
new=snapshot(R/r['file']);rays=[];floor=[]
for i in range(21):
 x=-1.0+i*.10
 for h in [.03,.10,.20,.26,.50,1.,1.5,2.,2.1]:
  a=hits(new,O+U*x-N*.20+Z*h,N,.40);q=dict(x=x,z=h,hits=a);rays.append(q)
  if a:fail.append(q)
 for d in [-.15,0,.15]:
  a=hits(new,O+U*x+N*d+Z*.02,-Z,.06);q=dict(x=x,d=d,hit=a[0] if a else None);floor.append(q)
  if not a or not -.0121<=a[0]['point'][2]<=.001:fail.append(q)
solids=[]
for name in r['closed_objects']:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges));solids.append(q);bm.free()
 if q['volume']<=0 or q['nonmanifold']:fail.append(q)
result=dict(tested_static_clear_width_m=2.0,full_width_note='The 2.2m-wide probe catches the photographed right panel near x=-1.10,z=1.5; see R64_full_width_probe.json. Do not claim the full post-to-post width is clear at all heights.',file=r['file'],former_obstruction_samples=len(before),static_passage_rays=rays,floor_samples=floor,solids=solids,failures=fail,construction_acceptance=False,limits='Static opening rays intentionally exclude operable P12 leaf families. No claim of a fully open current pose or verified door mechanism.');(B/'reports/R64_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R64 former',len(before),'clear',len(rays),'floor',len(floor),'fail',len(fail));assert not fail,fail
