from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169'
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_ARKA_CEPHE_ADAY_v017.blend'))
o=bpy.data.objects['R169_MEASURED_ENVELOPE'];data=json.loads((D/'roof_planes_164179202.json').read_text());import numpy as np
p=np.array(data['points']);a=np.load(D/'164179202.npz');ang=float(a['angle']);rot=np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]])
labels=np.full(len(p),-1)
for i,plane in enumerate(data['planes']):labels[plane['indices']]=i
changed=[];roofverts=set()
for f in o.data.polygons:
 if f.normal.z>.25:roofverts.update(f.vertices)
for i in roofverts:
 v=o.data.vertices[i];local=np.array([v.co.x,v.co.y])@rot;dist=np.sum((p[:,:2]-local)**2,axis=1);j=int(dist.argmin());label=int(labels[j])
 if dist[j]>.13 or label<0:continue
 c=data['planes'][label]['coeff'];z=c[0]*local[0]+c[1]*local[1]+c[2];dz=z-v.co.z
 if abs(dz)>.13:continue
 v.co.z=z;changed.append(float(dz))
o.data.update();out=R/'scenes/MUDAM_R169_SIRA_CATI_ADAY_v018.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
(R/'reports/R169_ROW_ROOF_v018.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,changed_roof_vertices=len(changed),max_change_m=max(map(abs,changed)),roof_plane_sample_rmse_m=[p['rmse'] for p in data['planes']],reopened=True,scope='Supported roof vertices constrained to locally sampled planes; unmatched dormer and edge points retained. First building v017 retained. Not full building acceptance.'),indent=2));print('ROOF_PLANES_APPLIED',len(changed))
for source in [False,True]:
 if source:bpy.ops.wm.open_mainfile(filepath=str(D/'source.blend'))
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-320,-45);s.camera.rotation_euler=(Vector((-67,-299,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/('renders/qa/R169_row_roof_'+('source' if source else 'v018')+'.png'));bpy.ops.render.render(write_still=True)
