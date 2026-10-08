"""R09 saved-file passage clearance, floor joins and wall/ceiling seams."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R09_build_report.json').read_text());q=json.loads((B/'reports/R09_ceiling_verification.json').read_text());assert q['file']==r['file'];fail=list(q['failures']);bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render];up=Vector((0,0,1));center=sum(map(Vector,r['room_inner_world']),Vector())/8
def ray(p,d,length,only=None):
 hits=[]
 for ob in visible:
  if only and ob.name not in only:continue
  inv=ob.matrix_world.inverted();ok,loc,_,_=ob.ray_cast(inv@p,inv.to_3x3()@d,distance=length)
  if ok:hits.append(dict(name=ob.name,distance=(ob.matrix_world@loc-p).length))
 return sorted(hits,key=lambda h:h['distance'])
floor=bpy.data.objects[r['changed_floor']].evaluated_get(deps);me=floor.to_mesh();bm=bmesh.new();bm.from_mesh(me);solid=dict(name=floor.name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));bm.free();floor.to_mesh_clear()
if solid['volume']<=0 or solid['nonmanifold'] or solid['zero_faces']:fail.append(solid)
clear=[];supports=[]
for portal in r['portals']:
 a,b=map(Vector,[portal['a'],portal['b']]);mid=(a+b)/2;t=(b-a).normalized();normal=(mid-center);normal=(normal-t*normal.dot(t)).normalized()
 for f in [.15,.5,.85]:
  p=a.lerp(b,f)+up*(portal['floor_z']+1.6);hits=ray(p-normal*.65,normal,1.3);row=dict(portal=portal['id'],fraction=f,hits=hits,passed=not hits);clear.append(row)
  if hits:fail.append(row)
  for d in [-.65,0,.65]:
   p=a.lerp(b,f)+normal*d+up*(portal['floor_z']+.03);hits=ray(p,-up,.08);head=ray(p,up,2.1);ok=bool(hits) and not head;row=dict(portal=portal['id'],fraction=f,offset_m=d,support=hits[:2],head=head,passed=ok);supports.append(row)
   if not ok:fail.append(row)
seams=[]
for i,p in enumerate(map(Vector,r['outer_ceiling_world'])):
 # Both adjacent wall solids must terminate at this same lower ceiling vertex.
 found=[]
 for name in r['walls']:
  ob=bpy.data.objects[name]
  if any((ob.matrix_world@v.co-p).length<1e-5 for v in ob.data.vertices):found.append(name)
 seams.append(dict(corner=i,walls=found,passed=len(found)==2))
 if len(found)!=2:fail.append(seams[-1])
result=dict(file=r['file'],failures=fail,ceiling_verification='R09_ceiling_verification.json',joined_floor_solid=solid,portal_clearance_rays=clear,portal_floor_headroom=supports,wall_ceiling_seams=seams,source_corner_max_offset_canonical=r['source_corner_max_offset_canonical'],door_leaves_assigned=False,construction_acceptance=False);(B/'reports/R09_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(floor=solid,failures=fail),indent=2));assert not fail,fail
