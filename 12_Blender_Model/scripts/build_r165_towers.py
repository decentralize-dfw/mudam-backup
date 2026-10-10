from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r165';data=json.loads((D/'mesh.json').read_text())
# Keep outer wall bottoms below the registered terrain rather than floating
# at the older OSM-height-derived constant base.
gv=[];gf=[]
for row in json.loads((R/'.local_source_cache/r161/surfaces.json').read_text()):
 off=len(gv);gv.extend(row['vertices']);gf.extend([[i+off for i in f] for f in row['faces']])
ground=BVHTree.FromPolygons(gv,gf,all_triangles=True);contacts=[]
for i in data.get('base_vertices',[]):
 v=data['vertices'][i];hit,*_=ground.ray_cast(Vector((v[0],v[1],150)),Vector((0,0,-1)),400)
 if hit is not None:v[2]=min(v[2],hit.z-.08);contacts.append(hit.z-v[2])
bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'))
sources=[o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for src in sources:src.select_set(True)
bpy.context.view_layer.objects.active=sources[0];bpy.ops.object.join();sources=[bpy.context.object]
mesh=bpy.data.meshes.new('R165_MEASURED_ENVELOPE');mesh.from_pydata(data['vertices'],[],data['faces']);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001);bmesh.ops.dissolve_limit(bm,angle_limit=.001,verts=list(bm.verts),edges=list(bm.edges),delimit={'NORMAL'});bmesh.ops.triangulate(bm,faces=list(bm.faces));slivers=[f for f in bm.faces if f.calc_area()<1e-6];bmesh.ops.delete(bm,geom=slivers,context='FACES');bmesh.ops.split_edges(bm,edges=list(bm.edges));bm.to_mesh(mesh);bm.free()
o=bpy.data.objects.new('R165_MEASURED_ENVELOPE',mesh);bpy.context.scene.collection.objects.link(o)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.004);bpy.ops.object.mode_set(mode='OBJECT')
m=bpy.data.materials.new('R165_SOURCE_BAKED');m.use_nodes=True;o.data.materials.append(m);im=bpy.data.images.new('R165_SOURCE_COLOR',width=4096,height=4096,alpha=False);node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;m.node_tree.nodes.active=node
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.render.bake.use_selected_to_active=True;s.render.bake.cage_extrusion=1.5;s.render.bake.max_ray_distance=5;s.render.bake.margin=8;s.render.bake.use_pass_direct=False;s.render.bake.use_pass_indirect=False;s.render.bake.use_pass_color=True
for src in sources:src.select_set(True)
bpy.context.view_layer.objects.active=o

for sm in sources[0].data.materials:
 if not sm or not sm.use_nodes:continue
 nt=sm.node_tree;tex=next((n for n in nt.nodes if n.type=='TEX_IMAGE' and n.image),None)
 if tex:
  em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],nt.nodes.get('Material Output').inputs['Surface'])
bpy.ops.object.bake(type='EMIT');im.filepath_raw=str(R/'textures/R165_source_color.png');im.file_format='PNG';im.save();m.node_tree.links.new(node.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color']);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
for src in sources:bpy.data.objects.remove(src,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
s.render.bake.use_selected_to_active=False
out=R/'scenes/MUDAM_R165_KUZEY_KULELER_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r165_measured_candidate.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('R165_WORLD');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
bpy.ops.object.light_add(type='SUN',location=(-100,100,150));bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.4,-.5,-.3)
bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=220
for name,eye in [('top',(245,370,400)),('front',(460,200,180))]:
 s.camera.location=eye;s.camera.rotation_euler=(Vector((240,370,40))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/f'renders/qa/R165_{name}.png');bpy.ops.render.render(write_still=True)
report={k:data[k] for k in ['limitations']};report.update(scene=out.name,vertices=len(bpy.data.objects['R165_MEASURED_ENVELOPE'].data.vertices),accepted=False,published=False,ground_contacts=len(contacts),ground_min_overlap=min(contacts) if contacts else None,wall_stats=data.get('wall_stats',[]));(R/'reports/R165_CANDIDATE.json').write_text(json.dumps(report,indent=2));print('R165_CANDIDATE_SAVED',flush=True)
