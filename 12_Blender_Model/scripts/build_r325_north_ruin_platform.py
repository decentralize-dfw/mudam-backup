"""Independent ruin platform, visible recesses preserved. Candidate only."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R324_MUZE_TERAS_TEMAS_ADAY_v001.blend'))
def xy(p):return (-120+p[0]*220/1400,95-p[1]*220/1400)
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
outline=[(452,181),(577,108),(635,212),(468,211)]
holes=[[(467,181),(575,121),(587,143),(482,195)],[(587,143),(600,157),(623,202),(600,206),(580,165)],[(511,185),(519,174),(534,181),(536,187),(520,182),(514,191)]]
platform=prism('R325_NORTH_RUIN_RAISED_PLATFORM',outline,-4.8,-.08,stone)
for i,hole in enumerate(holes):subtract(platform,prism('R325_CUT_'+str(i),hole,-5,1))
uv(platform);platform['level_id']='SITE';platform['source']='Independent raised ruin platform; traced architectural outline and open chamber corridors from R316 source view; source sparse ground levels R325. Recess depths not claimed verified.'
wall=bpy.data.objects['R152_RUIN_PARTITION_02'];old=[v.co.z for v in wall.data.vertices];changed=0
for v in wall.data.vertices:
 if v.co.z>-.22:v.co.z=-.22;changed+=1
wall.data.update()
# Central open garden has measured near-zero grade. Keep the central recess
# open and use the same independent outline as the visible triangular court.
garden=prism('R325_NORTH_RUIN_CENTRAL_COURT',[(520,180),(580,146),(613,207),(533,202)],-.13,-.075,bpy.data.objects['R152_CLASS2_TERRAIN'].data.materials[0])
subtract(garden,prism('R325_COURT_RECESS',holes[2],-5,1))
u=garden.data.uv_layers.new(name='UVMap');mi=garden.data.uv_layers.new(name='MicroUV')
for li in garden.data.loops:
 p=garden.data.vertices[li.vertex_index].co;u.data[li.index].uv=((p.x+500)/1150,(p.y+450)/1100);mi.data[li.index].uv=(p.x/2,p.y/2)
garden['level_id']='SITE';garden['source']='Independent court polygon; near-zero sparse source grade; central recess preserved.'
# No removal of surrounding vegetation; only trunks whose origin is inside
# the newly reconstructed raised work are recorded for subsequent inspection.
suspect=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.name.startswith('R158_TREE_'):
  c=o.matrix_world.translation
  if -50<c.x<-19 and 61<c.y<79:suspect.append(o.name)
out=R/'scenes/MUDAM_R325_KUZEY_KALINTI_PLATFORM_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in ['R325_NORTH_RUIN_RAISED_PLATFORM','R325_NORTH_RUIN_CENTRAL_COURT','R152_RUIN_PARTITION_02']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
bpy.ops.object.select_all(action='DESELECT')
for c in checks:bpy.data.objects[c['name']].select_set(True)
glb=R/'exports/r152_clean/r325_north_ruin_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True)
s=bpy.context.scene;bpy.ops.object.camera_add(location=(-35,68,70));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-35,68,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=44;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R325_Survey');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;s.render.filepath=str(R/'renders/qa/R325_north_ruin_candidate.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));roundtrip=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':roundtrip.append(dict(name=o.name,nonFinite=sum(not all(math.isfinite(x) for x in v.co) for v in o.data.vertices),zeroArea=sum(p.area<1e-10 for p in o.data.polygons)))
(R/'reports/R325_NORTH_RUIN_PLATFORM.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changedWallVertices=changed,previousWallTop=max(old),revisedWallTop=-.22,outline=outline,recesses=holes,meshChecks=checks,glbChecks=roundtrip,treesForInspection=suspect,limits=['Chamber floors and outer moat still need source checks','Platform material and perimeter alignment require matched-view review','Not a whole-ring acceptance']),indent=2));print('R325_READY',checks,roundtrip)
