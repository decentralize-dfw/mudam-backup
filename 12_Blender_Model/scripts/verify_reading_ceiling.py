"""R08: manifold solids, planar ceiling facets, lightwell, walk ring and anchors."""
from pathlib import Path
import bpy,bmesh,json,math,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];r=json.loads((B/'reports'/(args[0] if args else 'R08_build_report.json')).read_text());report_name=args[1] if len(args)>1 else 'R08_verification.json';P=json.loads((B/'config/reading_ceiling.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();fail=[];solids=[];planarity=[]
for name in r['closed_objects']+r['roof_boolean_targets']:
 ob=bpy.data.objects[name].evaluated_get(deps);me=ob.to_mesh();bm=bmesh.new();bm.from_mesh(me);row=dict(name=name,volume=bm.calc_volume(signed=True),nonmanifold=sum(not e.is_manifold for e in bm.edges),zero_faces=sum(f.calc_area()<1e-10 for f in bm.faces));solids.append(row)
 if row['volume']<=0 or row['nonmanifold'] or row['zero_faces']:fail.append(row)
 bm.free();ob.to_mesh_clear()
 if name in r['ceiling_facets']:
  raw=bpy.data.objects[name].data;poly=raw.polygons[0];vs=[raw.vertices[i].co for i in poly.vertices];n=(vs[1]-vs[0]).cross(vs[2]-vs[0]).normalized();error=max(abs((v-vs[0]).dot(n)) for v in vs);planarity.append(dict(name=name,error_m=error))
  if error>1e-4:fail.append(planarity[-1])
up=Vector((0,0,1));center=Vector(r['center_world']);visible=[o.evaluated_get(deps) for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render]
def rays(p,d,length,only=None,opaque_only=False):
 hits=[]
 for ob in visible:
  if only and ob.name not in only:continue
  if opaque_only and any('GLASS' in m.name.upper() for m in ob.data.materials if m):continue
  inv=ob.matrix_world.inverted();hit,loc,_,_=ob.ray_cast(inv@p,inv.to_3x3()@d,distance=length)
  if hit:hits.append(dict(name=ob.name,distance=(ob.matrix_world@loc-p).length))
 return sorted(hits,key=lambda h:h['distance'])
# Derive axes from a source-mapped ceiling diagonal; samples avoid fixture spokes.
a=Vector(r['inner_ceiling_world'][0])-center;a.z=0;a.normalize();b=Vector(r['inner_ceiling_world'][1])-center;b.z=0;b.normalize();daylight=[]
for j in range(12):
 angle=(j*30+7.5)*math.pi/180;p=center+(a*math.cos(angle)+b*math.sin(angle))*.85;p.z=r['floor_z']+.2;hits=rays(p,up,20,opaque_only=True);daylight.append(dict(point=list(p),hits=hits,passed=not hits))
 if hits:fail.append(dict(test='open_lightwell',point=list(p),hits=hits))
reading=json.loads((B/'reports/P17_build_report.json').read_text());void=list(map(Vector,reading['floor_void_world']));walk=[]
for i in range(4):
 for f in [.2,.4,.6,.8]:
  p=void[i].lerp(void[(i+1)%4],f);p+=(p-center).normalized()*.4;p.z=r['floor_z']+.03;support=rays(p,-up,.08,only=['P17_READING_FLOOR']);head=rays(p,up,2);ok=bool(support) and not head;walk.append(dict(point=list(p),support=support,head=head,passed=ok))
  if not ok:fail.append(walk[-1])
anchors=[]
for row in r['light_anchors']:
 p=Vector(row['point']);hits=rays(p,up,.08,only=r['ceiling_facets']);ok=bool(hits) and abs(hits[0]['distance']-.03)<1e-4;anchors.append(dict(index=row['index'],hits=hits,passed=ok))
 if not ok:fail.append(anchors[-1])
tubes=[o.name for o in bpy.data.objects if o.name.startswith('R08_LIGHT_TUBE_')]
if len(tubes)!=24:fail.append(dict(test='observed_arm_count',actual=len(tubes)))
result=dict(file=r['file'],failures=fail,evaluated_solids=solids,ceiling_planarity=planarity,open_daylight_rays=daylight,upper_walk_ring=walk,ceiling_anchor_rays=anchors,observed_arm_count=len(tubes),fixture_dimensions_verified=False,construction_acceptance=False);(B/'reports'/report_name).write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(solids=len(solids),planarity=planarity,failures=fail),indent=2));assert not fail,fail
