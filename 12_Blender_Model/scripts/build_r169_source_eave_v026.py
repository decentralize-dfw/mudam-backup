from pathlib import Path
import bpy,bmesh,json,math,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';samples=json.loads((D/'row_eave_normal_samples.json').read_text());rows=[r for r in samples if r['edge']==2];a=Vector((rows[0]['x'],rows[0]['y'],0));end=next(r for r in rows if r['t']==1 and r['inset']==0);b=Vector((end['x'],end['y'],0));t=(b-a).normalized();n=Vector((t.y,-t.x,0));center=Vector((-67,-299,0))
if (center-a).dot(n)<0:n=-n
length=(b-a).length
def correction(p):
 u=max(0,min(1,(p-a).dot(t)/length));dist=(p-a).dot(n)
 if dist<-.01 or dist>1.01:return 0
 # Interpolate the measured source minus fitted-plane residual, fading to plane at 1m.
 values=[]
 for step in [0,.25,.5,1.]:
  q=[r for r in rows if r['inset']==step];values.append(float(np.interp(u,[r['t'] for r in q],[r['delta'] if step<1 else 0 for r in q])))
 return float(np.interp(dist,[0,.25,.5,1.],values))
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_SIRA_BUTUN_CATI_ADAY_v023.blend'));o=bpy.data.objects['R169_ROW_CONTINUOUS_HIP'];bm=bmesh.new();bm.from_mesh(o.data)
for normal,offsets in [(t,[length*j/10 for j in range(1,10)]),(n,[.25,.5,1.])]:
 for offset in offsets:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=a+normal*offset,plane_no=normal)
moves=[]
for v in bm.verts:
 dz=correction(v.co)
 if dz:v.co.z+=dz;moves.append(dz)
bm.normal_update();bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.calc_loop_triangles();assert all(tr.area>1e-9 for tr in o.data.loop_triangles)
out=R/'scenes/MUDAM_R169_KAYNAK_SACAK_ADAY_v026.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));report=dict(scene=out.name,accepted=False,published=False,source='row_eave_normal_samples.json',moved_vertices=len(moves),max_drop_m=-min(moves),limits=['Interpolated source samples measured perpendicular to eave; source noise and manual trace uncertainty remain','Retained source fragments can overlap eave and need review','Raised details not flattened']);(R/'reports/R169_SOURCE_EAVE_v026.json').write_text(json.dumps(report,indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False;s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('VIEW');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8;bpy.ops.object.light_add(type='SUN');bpy.context.object.data.energy=2;bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.location=(-80,-320,-45);s.camera.rotation_euler=(Vector((-67,-299,-66))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=20;s.render.filepath=str(R/'renders/qa/R169_row_roof_v026.png');bpy.ops.render.render(write_still=True);print('SOURCE_EAVE_BUILT',report,flush=True)
