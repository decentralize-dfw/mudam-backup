"""Reopen: ceiling support, lens opening, closed parts and inherited collisions."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R70_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']))
deps=bpy.context.evaluated_depsgraph_get();trees={};bounds={};solids=[];fail=[];rays=[];collisions=[];connections=[];names=set(r['closed_objects']);up=Vector((0,0,1));ex=Vector(r['canonical_x_world'])
def geometry(name):
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();vs=[ob.matrix_world@v.co for v in me.vertices];polys=[list(f.vertices) for f in me.polygons];tree=BVHTree.FromPolygons(vs,polys);box=([min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)])
 bm=bmesh.new();bm.from_mesh(me);q=dict(name=name,nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces),volume=bm.calc_volume(signed=True));bm.free();ob.to_mesh_clear();return tree,box,q
for name in names:
 trees[name],bounds[name],q=geometry(name);solids.append(q)
 if q['nonmanifold'] or q['zero_faces'] or q['volume']<=0:fail.append(q)
ceiling,_,_=geometry('R28_E_FLAT_CEILING')
for track in r['tracks']:
 a,b=Vector(track['start']),Vector(track['end'])
 for i in range(31):
  for offset in [-.0175,0,.0175]:
   start=a.lerp(b,i/30)+ex*offset+up*(r['soffit_z']-.1);p,n,index,d=ceiling.ray_cast(start,up,.2);ok=p is not None and abs(p.z-r['soffit_z'])<2e-5;row=dict(track=track['id'],sample=i,offset=offset,passed=ok);rays.append(row)
   if not ok:fail.append(row)
for fixture in r['fixtures']:
 pivot=Vector(fixture['pivot']);axis=Vector(fixture['axis']);hits=[]
 for name in fixture['parts']:
  p,n,index,d=trees[name].ray_cast(pivot+axis*.35,-axis,.5)
  if p is not None:hits.append((d,name))
 hit=min(hits) if hits else None;ok=hit is not None and hit[1]==fixture['lens'];row=dict(fixture=fixture['id'],front_ray_hit=hit,passed=ok);rays.append(row)
 if not ok:fail.append(row)
 # Quantify assembly contact instead of accepting disconnected cosmetic parts.
 for suffix,other in [('_STEM','_ADAPTER'),('_STEM','_YOKE_TOP'),('_YOKE_+1','_YOKE_TOP'),('_YOKE_-1','_YOKE_TOP'),('_PIVOT_PIN','_YOKE_+1'),('_PIVOT_PIN','_YOKE_-1'),('_PIVOT_PIN','_BODY'),('_BACK_CAP','_BODY'),('_BEZEL','_BODY'),('_LENS','_BEZEL')]:
  a=fixture['id']+suffix;b=fixture['id']+other;ok=bool(trees[a].overlap(trees[b]));row=dict(a=a,b=b,passed=ok);connections.append(row)
  if not ok:fail.append(row)
def overlaps(a,b):return all(a[0][i]<b[1][i]-1e-5 and a[1][i]>b[0][i]+1e-5 for i in range(3))
overall=([min(box[0][i] for box in bounds.values()) for i in range(3)],[max(box[1][i] for box in bounds.values()) for i in range(3)])
nearby=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.name in names or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);vs=[eo.matrix_world@Vector(v) for v in eo.bound_box];box=([min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)])
 if not overlaps(overall,box):continue
 tree,box,q=geometry(ob.name);nearby.append(ob.name)
 for name in names:
  if overlaps(bounds[name],box) and trees[name].overlap(tree):collisions.append([name,ob.name])
if collisions:fail.append(dict(inherited_surface_collisions=collisions))
minimum=min(box[0][2] for box in bounds.values());maximum=max(box[1][2] for box in bounds.values())
if minimum<3.9 or maximum>r['soffit_z']+2e-5:fail.append(dict(unexpected_height=[minimum,maximum]))
result=dict(file=r['file'],solids=solids,rays=rays,connections=connections,nearby_inherited_objects=nearby,inherited_collisions=collisions,height_range=[minimum,maximum],failures=fail,construction_acceptance=False,limits='Assembly and geometric tests do not validate fixture count, measured coordinates, electrical system or lighting performance.')
(B/'reports/R70_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('R70',len(solids),'solids',len(rays),'rays',len(connections),'contacts',len(fail),'failures');assert not fail,fail
