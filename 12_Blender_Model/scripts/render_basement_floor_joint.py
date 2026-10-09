from pathlib import Path
import bpy,json
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R89_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));S=bpy.context.scene;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
S.cycles.device='GPU';S.cycles.samples=32;S.render.resolution_x=1600;S.render.resolution_y=1100;S.render.resolution_percentage=100
images=[]
for key in ['087','116']:
 S.camera=bpy.data.objects['P07_PHOTO_'+key+'_CONDITIONAL'];S.render.filepath=str(B/'renders/qa'/f'R89_overview_{key}.png');bpy.ops.render.render(write_still=True);images.append(Path(S.render.filepath).name)
(B/'reports/R89_overview_render.json').write_text(json.dumps(dict(file=r['file'],images=images,all_active_surroundings=True,metric_camera_match=False),indent=2))
