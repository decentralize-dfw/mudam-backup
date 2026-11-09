from pathlib import Path
import bpy,json,struct,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R161_YOL_BAGLANTILARI_WKI_THOMAS_MORE_v001.blend'));s=bpy.context.scene
names=[]
for key in ['near_site','r161_additions']:
 raw=(R/f'exports/r152_clean/{key}.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);names.append([n['name'] for n in j['nodes'] if 'mesh' in n])
def sig(o):return hashlib.sha256(str((tuple(o.matrix_world),[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
before={o.name:sig(o) for o in s.objects if o.type=='MESH' and not o.name.startswith('R158_')}
m=bpy.data.materials.new('R163_REGISTERED_ACT_SURFACE');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.92;tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'textures/R163_surface_with_existing_fallback.png'));tex.extension='EXTEND';uv=m.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='R163_WorldAtlas';m.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector']);m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
changed=[]
for o in s.objects:
 if o.type!='MESH' or not (o.name in ['R152_CLASS2_TERRAIN','R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or o.name.startswith(('R152_PATH_','R152_FORECOURT_'))):continue
 o.data.materials.clear();o.data.materials.append(m);layer=o.data.uv_layers.get('R163_WorldAtlas') or o.data.uv_layers.new(name='R163_WorldAtlas');o.data.uv_layers.active=layer
 for loop in o.data.loops:
  q=o.matrix_world@o.data.vertices[loop.vertex_index].co;layer.data[loop.index].uv=((q.x+500)/1150,(q.y+475)/1150)
 for f in o.data.polygons:f.material_index=0
 changed.append(o.name)
assert all(sig(bpy.data.objects[n])==h for n,h in before.items())
out=R/'scenes/MUDAM_R163_KAYNAK_ZEMIN_DOKUSU_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
for key,ns in zip(['r163_near','r163_district'],names):
 bpy.ops.object.select_all(action='DESELECT')
 for n in ns:
  if n in bpy.data.objects:bpy.data.objects[n].select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(R/f'exports/r152_clean/{key}.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
for label,eye,target in [('roads',(130,150,250),(-60,320,5)),('site',(260,-240,260),(20,40,0))]:
 s.camera.location=eye;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='PERSP';s.camera.data.lens=40;s.render.filepath=str(R/f'renders/qa/R163_{label}.png');bpy.ops.render.render(write_still=True)
(R/'reports/R163_SURFACE_CANDIDATE.json').write_text(json.dumps(dict(scene=out.name,changed_objects=changed,geometry_unchanged=True,reopened=True,accepted=False,limits=['Overhead color projection includes roof/canopy occlusion; not reconstructed ground under trees.','Road color boundaries follow scan; individual kerbs and markings are not separate geometry.','No change to museum coordinates, terrain elevations or tree geometry.']),indent=2));print('R163_SURFACE_READY',flush=True)

