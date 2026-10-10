from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];d=json.loads((R/'config/r168_junction.json').read_text());d.update(json.loads((R/d['mesh_cache']).read_text()));bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R167_GUNEY_BINALARI_ENTEGRE_v002.blend'));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.camera.location=(180,40,310);s.camera.rotation_euler=(Vector((0,315,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=900;s.render.filepath=str(R/'renders/qa/R168_before.png');bpy.ops.render.render(write_still=True)
gv=[];gf=[]
for row in json.loads((R/'.local_source_cache/r161/surfaces.json').read_text()):
 off=len(gv);gv.extend(row['vertices']);gf.extend([[i+off for i in f] for f in row['faces']])
for terrain_name in ['R152_CLASS2_TERRAIN','R154_FAR_GROUND']:
 terrain=bpy.data.objects.get(terrain_name)
 if terrain is None:continue
 terrain.data.calc_loop_triangles();off=len(gv);gv.extend([tuple(terrain.matrix_world@v.co) for v in terrain.data.vertices]);gf.extend([[int(i)+off for i in tri.vertices] for tri in terrain.data.loop_triangles])
bvh=BVHTree.FromPolygons(gv,gf,all_triangles=True);hits=0;valid=[]
for v in d['vertices']:
 h,*_=bvh.ray_cast(Vector((v[0],v[1],150)),Vector((0,0,-1)),400)
 valid.append(h is not None)
 if h is not None:v[2]=h.z+.025;hits+=1
original_faces=len(d['faces']);d['faces']=[f for f in d['faces'] if all(valid[i] for i in f)];excluded_faces=original_faces-len(d['faces']);used=sorted({i for f in d['faces'] for i in f});remap={old:new for new,old in enumerate(used)};d['vertices']=[d['vertices'][i] for i in used];d['faces']=[[remap[i] for i in f] for f in d['faces']]
assert excluded_faces/original_faces<.1, 'Too much corridor lacks terrain support'
print('EXCLUDED_UNSUPPORTED',excluded_faces,original_faces,flush=True)
mesh=bpy.data.meshes.new('R168_JUNCTION');mesh.from_pydata(d['vertices'],[],d['faces']);mesh.update();o=bpy.data.objects.new('R168_SOURCE_JUNCTION',mesh);s.collection.objects.link(o)
m=bpy.data.materials.new('R168_ACT_ROAD_COLOR');m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Roughness'].default_value=.9;tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures/R168_junction_source.png'));m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);mesh.materials.append(m);uv=mesh.uv_layers.new(name='SourceRoadUV')
for loop in mesh.loops:
 v=mesh.vertices[loop.vertex_index].co;px=(v.x+500)*4096/1150;py=(675-v.y)*4096/1150;uv.data[loop.index].uv=((px-300)/3000,1-(py-650)/1300)
s.render.filepath=str(R/'renders/qa/R168_after.png');bpy.ops.render.render(write_still=True)
out=R/'scenes/MUDAM_R168_DOGU_KAVSAK_ADAY_v002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT')
for name in ['R162_MEASURED_ENVELOPE','R164_MEASURED_ENVELOPE','R165_MEASURED_ENVELOPE','R166_MEASURED_ENVELOPE','R167_MEASURED_ENVELOPE','R161_ROAD_CONNECTIONS','R168_SOURCE_JUNCTION']:bpy.data.objects[name].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r168_district.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
(R/'reports/R168_JUNCTION.json').write_text(json.dumps(dict(scene=out.name,ground_samples=hits,excluded_unsupported_triangles=excluded_faces,area_m2=d['area_m2'],triangles=len(d['faces']),render_offset_m=.025,reopened=True,accepted=False,limits=d['limits']),indent=2))
