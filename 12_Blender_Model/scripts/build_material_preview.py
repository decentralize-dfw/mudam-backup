"""P19 optical readability pass; leaves geometry and parameter uncertainty intact."""
from pathlib import Path
import bpy,json,sys
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/material_preview.json').read_text())
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_P19_MALZEME_ISIK_{version}.blend'
if out.exists():raise RuntimeError('Choose new version')
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));S=bpy.context.scene;changes=[]
for name in ['P10_GLASS_PREVIEW','P08_GLAZING_PREVIEW_NOT_SPECIFICATION']:
 m=bpy.data.materials[name];n=m.node_tree.nodes.get('Principled BSDF');g=P['glass'];m.diffuse_color=(*g['base_color'],1)
 for key,value in [('Base Color',(*g['base_color'],1)),('Transmission Weight',g['transmission']),('Roughness',g['roughness']),('IOR',g['ior'])]:n.inputs[key].default_value=value
 m['parameter_source']='material_preview.json';m['physical_specification_verified']=False;changes.append(name)
for name in ['P10_FRAME_PREVIEW','P08_FRAME_PREVIEW_NOT_SPECIFICATION']:
 m=bpy.data.materials[name];n=m.node_tree.nodes.get('Principled BSDF');p=P['dark_metal'];m.diffuse_color=(*p['base_color'],1);n.inputs['Base Color'].default_value=(*p['base_color'],1);n.inputs['Metallic'].default_value=p['metallic'];n.inputs['Roughness'].default_value=p['roughness'];changes.append(name)
world=bpy.data.worlds.new('P19_GENERIC_DAYLIGHT_NOT_PHOTO_CALIBRATED');world.use_nodes=True;nodes=world.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputWorld');background=nodes.new('ShaderNodeBackground');sky=nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=P['daylight']['sun_elevation_rad'];sky.sun_rotation=P['daylight']['sun_rotation_rad'];background.inputs['Strength'].default_value=P['daylight']['world_strength'];world.node_tree.links.new(sky.outputs['Color'],background.inputs['Color']);world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface']);S.world=world
S.view_settings.view_transform='AgX';S.view_settings.exposure=P['daylight']['exposure'];S.render.engine='CYCLES';S.cycles.samples=48;S.cycles.use_denoising=True;S.cycles.max_bounces=16;S.cycles.transmission_bounces=12;S.cycles.glossy_bounces=8
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S['stage']='P19 clear glass and generic daylight; regional geometry still conditional';S['current_file']=out.name;bpy.data.texts.new('P19_MATERIAL_NOTES').write(json.dumps(P,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
renders=[]
for camera,stem,width,height in [('P07_ENTRY_DETAIL','P19_entry_daylight',1600,1400),('P17_READING_DETAIL','P19_reading_daylight',1500,1200),('P07_PHOTO_116_CONDITIONAL','P19_116_daylight',2000,1333)]:
 S.camera=bpy.data.objects[camera];S.render.resolution_x=width;S.render.resolution_y=height;S.render.resolution_percentage=100;S.render.filepath=str(B/'renders/qa'/f'{stem}.png');bpy.ops.render.render(write_still=True);renders.append(S.render.filepath)
result=dict(file=out.relative_to(R).as_posix(),changed_materials=changes,geometry_unchanged=True,renders=renders,lighting_calibrated=False,construction_acceptance=False)
(B/'reports/P19_build_report.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('P19_SAVED',out)
