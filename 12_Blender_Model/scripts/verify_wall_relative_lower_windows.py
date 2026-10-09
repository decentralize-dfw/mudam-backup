from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R54_build_report.json').read_text());P=json.loads((B/'config/lower_windows_wall_relative.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));S=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get();a,u,n=map(Vector,[r['origin'],r['axis'],r['inside']]);up=Vector((0,0,1));fail=[];checks=[];rays=[]
for name in r['closed_objects']+r['changed_inherited_objects']:
 ob=bpy.data.objects[name].evaluated_get(dep);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);q=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));checks.append(q);bm.free();ob.to_mesh_clear()
 if q['volume']<=0 or q['nonmanifold'] or q['zero_faces']:fail.append(q)
objects=[o.evaluated_get(dep) for o in S.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def cast(p,d,dist,only_name=None):
 hits=[]
 for o in objects:
  if only_name is not None and o.name!=only_name:continue
  inv=o.matrix_world.inverted();hit,q,_,_=o.ray_cast(inv@p,inv.to_3x3()@d,distance=dist)
  if hit:hits.append(((o.matrix_world@q-p).length,o.name,list(o.matrix_world@q)))
 return min(hits) if hits else None
for w in r['windows']:
 for t in [-.35,0,.35]:
  for z in [P['inner_sill_z']+.2,(P['inner_sill_z']+P['glass_head_z'])/2,P['glass_head_z']-.2]:
   p=a+u*(w['t']+t)+n*(-.7)+up*z;hit=cast(p,n,2);q=dict(id=w['id'],kind='outside_to_glass',t_offset=t,z=z,hit=hit);rays.append(q)
   if not hit or hit[1]!=w['glass']:fail.append(q)
 p=a+u*w['t']+n*(-.2)+up*(P['historic_top_z']-.025);hit=cast(p,-up,4);q=dict(id=w['id'],kind='top_open_notch',hit=hit);rays.append(q)
 if not hit or hit[1]!=f'R54_WINDOW_{w["id"]:02d}_SILL':fail.append(q)
 for sign in [-1,1]:
  p=a+u*(w['t']+sign*1.5)+n*(-.7)-up*2.3;hit=cast(p,n,1.8,P['historic_wall_object']);q=dict(id=w['id'],kind='retained_historic_side',side=sign,hit=hit,nearest_visible_surface=cast(p,n,1.8));rays.append(q)
  if not hit or hit[1]!=P['historic_wall_object']:fail.append(q)
result=dict(file=r['file'],closed_checks=checks,rays=rays,failures=fail,visual_acceptance=False,construction_acceptance=False);(B/'reports/R54_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(closed=len(checks),rays=len(rays),failures=fail),indent=2));assert not fail,fail
