"""Reopen the clean-site candidate, compare museum inheritance and local contacts."""
from pathlib import Path
import bpy,json,hashlib,struct,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
version=sys.argv[-1] if '--' in sys.argv else 'v008'
def signature(o):
 h=hashlib.sha256()
 for row in o.matrix_world:h.update(struct.pack('4d',*row))
 for v in o.data.vertices:h.update(struct.pack('3d',*v.co))
 for p in o.data.polygons:h.update(struct.pack(str(len(p.vertices))+'I',*p.vertices))
 return h.hexdigest()
def inventory():return {o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o.visible_get() and not o.name.startswith('R151_ACT_')}
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R151_WEB_CLEAN_v002.blend'));before=inventory()
base_vertices={o.name:[tuple(o.matrix_world@v.co) for v in o.data.vertices] for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith(('R35_WALL_51946353_','R17_WALL_','R17_WINDOW_')) or o.name in ('P05_FRONT_0','P05_FRONT_9','P05_FRONT_10'))}
bpy.ops.wm.open_mainfile(filepath=str(R/f'scenes/MUDAM_R152_TEMIZ_YAKIN_CEVRE_{version}.blend'));after=inventory();s=bpy.context.scene
changed=[n for n in before.keys()&after.keys() if before[n]!=after[n]];removed=sorted(before.keys()-after.keys());added=sorted(after.keys()-before.keys())
unexpected=[n for n in changed if not n.startswith(('R35_WALL_51946353_','R17_WALL_','R17_WINDOW_')) and n not in ('P05_FRONT_0','P05_FRONT_9','P05_FRONT_10')]+[n for n in removed if n!='R151_PAV_GROUND_JOIN']
vs=[];fs=[];degenerate=[];triangles=0
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith('R152_'):continue
 o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
 if any(p.area<1e-10 for p in o.data.polygons):degenerate.append(o.name)
 if o.name=='R152_CLASS2_TERRAIN' or o.name.startswith(('R152_PATH_','R152_FORECOURT_')):
  offset=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(offset+i for i in t.vertices) for t in o.data.loop_triangles)
terrain=BVHTree.FromPolygons(vs,fs,all_triangles=True)
foundation_checks=0;floating_bases=[];non_base_changes=[]
for name in changed:
 if name not in base_vertices:continue
 o=s.objects[name];old=base_vertices[name];cutoff=-4 if name.startswith('R17_') else min(v[2] for v in old)+.001
 for v,prior in zip(o.data.vertices,old):
  q=o.matrix_world@v.co
  if abs(q.z-prior[2])>1e-5 and (abs(q.x-prior[0])>1e-5 or abs(q.y-prior[1])>1e-5 or q.z>prior[2] or prior[2]>cutoff):non_base_changes.append(name)
  if prior[2]>cutoff:continue
  hit=terrain.ray_cast(Vector((q.x,q.y,100)),Vector((0,0,-1)),200)[0]
  if hit is not None:
   foundation_checks+=1
   if q.z>hit.z+.03:floating_bases.append(dict(name=name,gap=q.z-hit.z))
 for e in o.data.edges:
  a,b=e.vertices
  if old[a][2]>cutoff or old[b][2]>cutoff:continue
  va=o.matrix_world@o.data.vertices[a].co;vb=o.matrix_world@o.data.vertices[b].co;count=max(2,int((vb-va).length/.5))
  for i in range(1,count):
   q=va.lerp(vb,i/count);hit=terrain.ray_cast(Vector((q.x,q.y,100)),Vector((0,0,-1)),200)[0]
   if hit is not None:
    foundation_checks+=1
    if q.z>hit.z+.03:floating_bases.append(dict(name=name,gap=q.z-hit.z,edge=True))
constraints=json.loads((R/'.local_source_cache/r152/site_constraints.json').read_text());penetrations=[];sampled=0
for f in constraints['floors']:
 xy=f['xy'];x=sum(q[0] for q in xy)/3;y=sum(q[1] for q in xy)/3
 hit=terrain.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200)[0]
 if hit is not None:
  sampled+=1
  if hit.z>f['z']+.03:penetrations.append(dict(name=f['name'],terrain_z=hit.z,cap=f['z']))
report=dict(reopened=True,source_scene='R151_WEB_CLEAN_v002',candidate='R152_TEMIZ_YAKIN_CEVRE_v005',inherited_visible=len(before),changed=changed,removed=removed,added_count=len(added),unexpected_inherited_changes=unexpected,new_triangles=triangles,zero_area_objects=degenerate,floor_centroid_samples=sampled,terrain_above_floor_cap=penetrations,scope='Targeted geometry/inheritance check; not a complete site or building acceptance.')
report['candidate']='R152_TEMIZ_YAKIN_CEVRE_'+version
report.update(foundation_vertex_samples=foundation_checks,floating_tested_bases=floating_bases,changes_above_base_or_horizontal=non_base_changes)
(R/'reports/R152_CLEAN_SITE_QA.json').write_text(json.dumps(report,indent=2));print('R152_QA',json.dumps(report),flush=True)
assert not unexpected and not degenerate and not penetrations and not floating_bases and not non_base_changes
