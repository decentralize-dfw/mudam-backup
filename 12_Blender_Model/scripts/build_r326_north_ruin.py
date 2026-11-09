"""Independent ruin platform, visible recesses preserved. Candidate only."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R324_MUZE_TERAS_TEMAS_ADAY_v001.blend'))
def xy(p):return (-57+p[0]*44/1200,84.5-p[1]*44/1200)
def prism(name,pixels,lo,hi,mat=None):
 pts=[xy(p) for p in pixels];n=len(pts);vs=[(x,y,z) for z in [lo,hi] for x,y in pts]
 fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 if mat:me.materials.append(mat)
 return o
def subtract(o,cut):
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Architectural recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
def uv(o):
 u=o.data.uv_layers.new(name='UVMap')
 for f in o.data.polygons:
  n=f.normal;a=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.7 else Vector((1,0,0));b=n.cross(a).normalized()
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;u.data[li].uv=(v.dot(a)/4,v.dot(b)/4)
 m=o.data.materials[0]
 for name in {getattr(n,'uv_map','') for n in m.node_tree.nodes}-{'','UVMap'}:
  layer=o.data.uv_layers.new(name=name)
  for a,b in zip(layer.data,u.data):a.uv=b.uv
stone=bpy.data.objects['R152_RUIN_PARTITION_01'].data.materials[0]
# Source top view: inner raised work, excluding the outer ditch. Chamber
# trenches remain open; existing cross-walls divide the bays independently.
outline=[(250,479),(778,167),(1045,631),(306,616)]
holes=[[(292,478),(750,220),(799,296),(344,568)],[(748,384),(826,337),(850,378),(774,421)],[(790,474),(880,430),(900,472),(811,518)],[(841,557),(932,530),(962,574),(863,600)],[(462,565),(505,501),(580,520),(592,550),(524,529),(484,579)]]
platform=prism('R325_NORTH_RUIN_RAISED_PLATFORM',outline,-4.8,-.08,stone)
for i,hole in enumerate(holes):subtract(platform,prism('R325_CUT_'+str(i),hole,-5,1))
uv(platform);platform['level_id']='SITE';platform['source']='Independent raised ruin platform; traced architectural outline and open chamber corridors from R316 source view; source sparse ground levels R325. Recess depths not claimed verified.'
old=[];changed=0
for i in range(1,10):
 ob=bpy.data.objects.get('R152_RUIN_PARTITION_%02d'%i)
 if ob:
  old.extend(v.co.z for v in ob.data.vertices);changed+=len(ob.data.vertices);bpy.data.objects.remove(ob,do_unlink=True)
ribs=[[(364,437),(389,423),(428,489),(404,503)],[(458,383),(482,369),(521,435),(497,449)],[(552,328),(576,314),(618,385),(592,400)],[(650,271),(675,257),(715,325),(690,340)]]
for i,p in enumerate(ribs):
 ob=prism('R326_NORTH_RUIN_CROSSWALL_%02d'%i,p,-4.8,-.08,stone);uv(ob);ob['level_id']='SITE';ob['source']='Independent source-traced planar cross-wall, R325 matched orthographic source view.'
# Central open garden has measured near-zero grade. Keep the central recess
# open and use the same independent outline as the visible triangular court.
garden=prism('R325_NORTH_RUIN_CENTRAL_COURT',[(535,490),(728,386),(894,599),(600,590)],-.13,-.075,bpy.data.objects['R152_CLASS2_TERRAIN'].data.materials[0])
subtract(garden,prism('R325_COURT_RECESS',holes[4],-5,1))
u=garden.data.uv_layers.new(name='UVMap');mi=garden.data.uv_layers.new(name='MicroUV')
for li in garden.data.loops:
 p=garden.data.vertices[li.vertex_index].co;u.data[li.index].uv=((p.x+500)/1150,(p.y+450)/1100);mi.data[li.index].uv=(p.x/2,p.y/2)
garden['level_id']='SITE';garden['source']='Independent court polygon; near-zero sparse source grade; central recess preserved.'
# No removal of surrounding vegetation; only trunks whose origin is inside
# the newly reconstructed raised work are recorded for subsequent inspection.
suspect=[]
def contains(x,y):
 points=[xy(p) for p in outline];inside=False
 for a,b in zip(points,points[1:]+points[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R158_TREE_'):
  bounds=[o.matrix_world@Vector(p) for p in o.bound_box];x=sum(p.x for p in bounds)/8;y=sum(p.y for p in bounds)/8
  if contains(x,y):o.hide_render=True;o.hide_viewport=True;suspect.append(o.name)
out=R/'scenes/MUDAM_R326_KUZEY_KALINTI_PLAN_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in ['R325_NORTH_RUIN_RAISED_PLATFORM','R325_NORTH_RUIN_CENTRAL_COURT','R326_NORTH_RUIN_CROSSWALL_00','R326_NORTH_RUIN_CROSSWALL_01','R326_NORTH_RUIN_CROSSWALL_02','R326_NORTH_RUIN_CROSSWALL_03']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
bpy.ops.object.select_all(action='DESELECT')
for c in checks:bpy.data.objects[c['name']].select_set(True)
glb=R/'exports/r152_clean/r326_north_ruin_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-35,68,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,68,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=44;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R325_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R326_north_ruin_candidate.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));roundtrip=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':roundtrip.append(dict(name=o.name,nonFinite=sum(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices),zeroArea=sum(p.area<1e-10 for p in o.data.polygons)))
(R/'reports/R326_NORTH_RUIN_PLAN.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changedWallVertices=changed,previousWallTop=max(old),revisedWallTop=-.08,outline=outline,recesses=holes,meshChecks=checks,glbChecks=roundtrip,sourceCourtTreesHidden=suspect,limits=['Chamber floors and outer moat still need source checks','Platform material and perimeter alignment require matched-view review','Not a whole-ring acceptance']),indent=2));print('R325_READY',checks,roundtrip)
