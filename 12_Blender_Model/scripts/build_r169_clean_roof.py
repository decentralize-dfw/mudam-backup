from pathlib import Path
import bpy,json,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';fit=json.loads((D/'hip_roof_fit_33.json').read_text());zr,yr,xl,xr,af,ab,al,ar=fit['parameters'];a=np.load(D/'164179154.npz');ang=float(a['angle']);rot=np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]]);pts=np.array(json.loads((D/'roof_planes_33.json').read_text())['points']);lo=pts[:,:2].min(0)+2;hi=pts[:,:2].max(0)-2
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_CEPHE_GEOMETRI_ADAY_v010.blend'));o=bpy.data.objects['R169_MEASURED_ENVELOPE'];m=bpy.data.materials.new('R169_33_CLEAN_UPPER_ROOF');m.use_nodes=True;m.diffuse_color=(.34,.40,.42,1);bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.34,.40,.42,1);bs.inputs['Roughness'].default_value=.72;o.data.materials.append(m);matidx=len(o.data.materials)-1
valid={};changes=[]
for v in o.data.vertices:
 x,y=np.array([v.co.x,v.co.y])@rot
 if not(lo[0]<x<hi[0] and lo[1]<y<hi[1]):continue
 z=min(zr-af*(y-yr),zr+ab*(y-yr),zr+al*(x-xl),zr-ar*(x-xr));delta=z-v.co.z
 if abs(delta)>.35:continue
 valid[v.index]=z
for f in o.data.polygons:
 if f.normal.z>.4 and all(i in valid for i in f.vertices):f.material_index=matidx
for i,z in valid.items():changes.append(abs(z-o.data.vertices[i].co.z));o.data.vertices[i].co.z=z
o.data.update();path=R/'scenes/MUDAM_R169_TEMIZ_CATI_ADAY_v011.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=1
bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.context.object.rotation_euler=(.4,-.5,-.3);bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(62,-315,-40);s.camera.rotation_euler=(Vector((38,-273,-67))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=35;s.render.filepath=str(R/'renders/qa/R169_33_geometry_v011.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_CLEAN_ROOF_v011.json').write_text(json.dumps(dict(scene=path.name,reopened=True,accepted=False,published=False,changed_vertices=len(changes),max_displacement_m=max(changes),upper_roof_fit=fit,limits=['Roof tone is a provisional material','Dormers and skirt remain unresolved','Right balcony, rear facade and entrances incomplete']),indent=2));print('UPPER_ROOF_REBUILT',len(changes))
