from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R161_YOL_BAGLANTILARI_WKI_THOMAS_MORE_v001.blend'))
def sig(o):return hashlib.sha256(str((tuple(o.matrix_world),[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
replaced=[o.name for o in bpy.context.scene.objects if o.name.startswith(('R161_24457411_','R161_24457477_'))];keep={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in replaced and not o.name.startswith('R158_')}
for n in replaced:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
for filename,name in [
 ('MUDAM_R162_TARAMA_CATI_CEPHE_ADAY_v004.blend','R162_MEASURED_ENVELOPE'),
 ('MUDAM_R164_KAYNAK_BINA_DETAY_ADAY_v001.blend','R164_MEASURED_ENVELOPE'),
 ('MUDAM_R165_KUZEY_KULELER_ADAY_v001.blend','R165_MEASURED_ENVELOPE')]:
 with bpy.data.libraries.load(str(R/'scenes'/filename),link=False) as (src,dst):dst.objects=[name]
 for o in dst.objects:bpy.context.scene.collection.objects.link(o)
assert all(sig(bpy.data.objects[n])==h for n,h in keep.items())
out=R/'scenes/MUDAM_R165_YEDI_BINA_ENTEGRE_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));bpy.ops.object.select_all(action='DESELECT')
for n in ['R162_MEASURED_ENVELOPE','R164_MEASURED_ENVELOPE','R165_MEASURED_ENVELOPE','R161_ROAD_CONNECTIONS']:bpy.data.objects[n].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'exports/r152_clean/r165_district.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.camera.location=(480,-60,320);s.camera.rotation_euler=(Vector((30,290,15))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='PERSP';s.camera.data.lens=40;s.render.filepath=str(R/'renders/qa/R165_integrated.png');bpy.ops.render.render(write_still=True)
(R/'reports/R165_INTEGRATION.json').write_text(json.dumps(dict(scene=out.name,replaced_objects=replaced,preserved_objects=len(keep),preserved_geometry_hashes=True,reopened=True,status='work_in_progress_review_release',whole_context_complete=False,limits=['Source-derived roof and facade candidate; fine window recesses and scan-boundary artifacts still open.','Museum, other buildings, roads and tree geometry retained.']),indent=2));print('R165_INTEGRATED',flush=True)
