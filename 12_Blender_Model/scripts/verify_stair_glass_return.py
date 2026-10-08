"""Reopen R03 and check solids, podium recess, support and prior checkpoint geometry."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,struct,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R03_build_report.json').read_text());P=json.loads((B/'config/stair_glass_return.json').read_text())
sys.path.insert(0,str(B/'scripts'));from stair_outline import crossings
def geometry_snapshot():
 result={}
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  h=hashlib.sha256()
  for v in ob.data.vertices:h.update(struct.pack('<3f',*v.co))
  for f in ob.data.polygons:h.update(struct.pack('<'+'I'*len(f.vertices),*f.vertices))
  h.update(struct.pack('<16f',*(v for row in ob.matrix_world for v in row)))
  result[ob.name]=h.hexdigest()
 return result
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/r['base_scene']));base=geometry_snapshot()
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));current=geometry_snapshot();fail=[];solids=[]
for name,value in base.items():
 if current.get(name)!=value:fail.append(dict(test='prior_mesh_unchanged',name=name))
for index,poly in enumerate(r['repaired_footprints_canonical']):
 if list(crossings(poly)):fail.append(dict(test='podium_outline_self_intersection',index=index))
deps=bpy.context.evaluated_depsgraph_get()
for name in r['closed_objects']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);volume=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces)
 solids.append(dict(name=name,volume=volume,nonmanifold=nm,zero_faces=zero))
 if volume<=0 or nm or zero:fail.append(solids[-1])
 bm.free();ob.to_mesh_clear()
for name in ['R03_PODIUM_1_REPAIRED','R03_PODIUM_2_REPAIRED','R03_PODIUM_3_WITH_RECESS']:
 ob=bpy.data.objects[name];top=max(v.co.z for v in ob.data.vertices);wrong=[f.index for f in ob.data.polygons if abs(f.center.z-top)<1e-5 and f.normal.z<.99]
 if wrong:fail.append(dict(test='podium_top_normals',name=name,faces=wrong))
center=Vector(r['center_world']);axis=Vector(r['axis_world']);normal=Vector(r['normal_world']);top=r['podium_top_z']
def vertical_hits(point,names):
 result=[];origin=point+Vector((0,0,2));direction=Vector((0,0,-1))
 for name in names:
  ob=bpy.data.objects[name].evaluated_get(deps);inv=ob.matrix_world.inverted();hit,loc,_,_=ob.ray_cast(inv@origin,inv.to_3x3()@direction,distance=3)
  if hit:result.append(dict(name=name,z=(ob.matrix_world@loc).z))
 return sorted(result,key=lambda v:-v['z'])
# Full scene must not contain an old opaque face above the newly recessed lens.
visible=[ob.name for ob in bpy.context.scene.objects if ob.type=='MESH' and ob.visible_get() and not ob.hide_render]
tests=[]
for radius,wanted,z_wanted in [(0,'R03_UPLIGHT_GLASS_LENS',r['lens_z']),(.30,'R03_RECESSED_STONE_DISH',r['recess_z']),(.57,'R03_PODIUM_3_WITH_RECESS',top)]:
 for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
  point=center+(normal*math.cos(angle)+axis*math.sin(angle))*radius;hits=vertical_hits(point,visible);ok=bool(hits) and hits[0]['name']==wanted and abs(hits[0]['z']-z_wanted)<1e-4
  tests.append(dict(radius=radius,angle=angle,expected=wanted,hits=hits,passed=ok))
  if not ok:fail.append(dict(test='recess_visible_clearance',radius=radius,angle=angle,hits=hits))
# All base-channel samples must lie over the actual retained source podium.
support=[]
for j in range(65):
 angle=-math.radians(P['arc_degrees'])*j/64;p=center+(normal*math.cos(angle)+axis*math.sin(angle))*P['radius_m'];hits=vertical_hits(p,['P09_PODIUM_3']);ok=bool(hits) and abs(hits[0]['z']-top)<1e-4
 support.append(ok)
 if not ok:fail.append(dict(test='source_podium_support',sample=j))
assert all(bpy.data.objects[f'P09_PODIUM_{i}'].hide_render for i in [1,2,3])
assert all(bpy.data.objects[n].hide_render for n in r['cutters'])
# Preserve the prior whole-scene portal test, not merely R03's isolated view.
old=json.loads((B/'reports/R02_build_report.json').read_text());a,b=map(Vector,old['portal_endpoints']);pn=Vector(old['normal']);portal=[]
for t in [.2,.5,.8]:
 for z,expected in [(1.2,False),(old['ground_clear']-.05,False),((old['ground_clear']+old['beam_top'])/2,True),(old['beam_top']+.2,False),(old['upper_head']-.2,False)]:
  p=a.lerp(b,t);p.z=z;hits=[]
  for name in visible:
   ob=bpy.data.objects[name].evaluated_get(deps);inv=ob.matrix_world.inverted()
   if ob.ray_cast(inv@(p-pn*.5),inv.to_3x3()@pn,distance=1)[0]:hits.append(name)
  if bool(hits)!=expected:fail.append(dict(test='R02_portal_regression',t=t,z=z,hits=hits))
  portal.append(dict(t=t,z=z,hits=hits))
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,source_podium_support_samples=len(support),source_podium_support_all_passed=all(support),recess_rays=tests,prior_meshes_unchanged=len(base),portal_regression_rays=portal,construction_acceptance=False,metric_photo_pose_verified=False,full_flight_modeled=False)
(B/'reports/R03_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));assert not fail,fail
