"""Export separate static building/context layers from the web copy."""
from pathlib import Path
import bpy,json,subprocess
from mathutils import Vector
R=Path(__file__).resolve().parents[1];out=R/'exports/r151_web_v002';out.mkdir(exist_ok=True)
source=R/'scenes/MUDAM_R151_WEB_LOD_v002.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render and o.visible_get()];layers=[]
def layer(o):
 if not o.name.startswith('R151_ACT_'):return 'building'
 bounds=[o.matrix_world@Vector(c) for c in o.bound_box]
 return 'near_context' if min((p.x*p.x+p.y*p.y)**.5 for p in bounds)<180 else 'far_context'
for key in ('building','near_context','far_context'):
 selected=[o for o in objects if layer(o)==key]
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.select_set(True)
 raw=out/f'{key}_unbatched.glb';target=out/f'{key}.glb';assert not target.exists()
 bpy.ops.export_scene.gltf(filepath=str(raw),export_format='GLB',use_selection=True,export_apply=True,export_extras=False,export_cameras=False,export_lights=False,export_yup=True)
 subprocess.run(['C:/Users/yigit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-X','utf8',str(R/'scripts/batch_web_glb.py'),str(raw),str(target)],check=True)
 subprocess.run(['C:/Users/yigit/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe','-X','utf8',str(R/'scripts/verify_web_lod_glb.py'),str(target)],check=True)
 report=json.loads(Path(str(target)+'.json').read_text());report={k:v for k,v in report.items() if k not in ('file','source')};report['url']='../exports/r151_web_v002/'+target.name+'.gz';report['key']=key;layers.append(report)
manifest=dict(source_scene=source.name,revision='R151 WEB LOD v002',layers=layers,scope='Separate local web LOD; original v011 preserved. Not architectural acceptance.',accepted=False)
(R/'config/r151_web_lod.json').write_text(json.dumps(manifest,indent=2))
cam=s.camera;cam.location=(92,-130,120);cam.rotation_euler=(Vector((0,5,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48;s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R151_web_lod_museum.png');bpy.ops.render.render(write_still=True)
print('WEB_LAYERS_EXPORTED',flush=True)
