from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R57_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));dep=bpy.context.evaluated_depsgraph_get();fail=[];solids=[];origin,u,n=map(Vector,[r['origin'],r['axis'],r['outward']]);up=Vector((0,0,1))
for name in r['closed_objects']+r['changed_inherited_objects']:
 eo=bpy.data.objects[name].evaluated_get(dep);me=eo.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();eo.to_mesh_clear()
targets=[bpy.data.objects[name].evaluated_get(dep) for name in r['closed_objects']+r['changed_inherited_objects']]
def floor_at(x,d):
 p=origin+u*x+n*d+up*.03;hits=[]
 for ob in targets:
  iv=ob.matrix_world.inverted();ok,loc,no,ix=ob.ray_cast(iv@p,iv.to_3x3()@(-up),distance=.10)
  if ok:hits.append(dict(name=ob.name,z=(ob.matrix_world@loc).z))
 return sorted(hits,key=lambda q:-q['z'])
samples=[]
for i in range(21):
 for j in range(21):
  x=-1.045+i*2.09/20;d=.085+j*2.03/20;hits=floor_at(x,d);q=dict(x=x,d=d,top=hits[0] if hits else None);samples.append(q)
  if not hits or hits[0]['z']<-.0121 or hits[0]['z']>.0001 or not hits[0]['name'].startswith('R57_'):fail.append(q)
outside=[]
for x,d in [(-1.1,.5),(1.1,.5),(0,.04),(0,2.16)]:
 hits=floor_at(x,d);q=dict(x=x,d=d,top=hits[0] if hits else None);outside.append(q)
 if not hits or abs(hits[0]['z'])>1e-5 or hits[0]['name'].startswith('R57_'):fail.append(q)
poses=[];leaves=json.loads((B/'reports/P12_build_report.json').read_text())['leaf_families']
for f in leaves:
 pivot=bpy.data.objects[f['pivot']];angle=pivot.rotation_euler.z
 for deg in range(-90,91,15):
  pivot.rotation_euler.z=math.radians(deg);bpy.context.view_layer.update();z=min((bpy.data.objects[name].matrix_world@v.co).z for name in f['objects'] for v in bpy.data.objects[name].data.vertices);q=dict(pivot=pivot.name,angle_deg=deg,lowest_z=z,clearance_above_insert=z);poses.append(q)
  if z<.03:fail.append(q)
 pivot.rotation_euler.z=angle
result=dict(file=r['file'],closed_solids=solids,insert_samples=samples,unchanged_outer_floor_samples=outside,door_pose_clearances=poses,failures=fail,construction_acceptance=False,limits='Vertical clearance only; not a real door-mechanism or full collision certification.');(B/'reports/R57_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),floor_samples=len(samples),poses=len(poses),failures=fail),indent=2));assert not fail,fail
