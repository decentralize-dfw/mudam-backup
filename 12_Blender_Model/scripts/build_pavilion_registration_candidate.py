"""Rigid pavilion placement trial, including a continuous link-end transition."""
from pathlib import Path
import bpy,json
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
fit=json.loads((root/'reports/R151_pavilion_registration_candidate.json').read_text())
out=root/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v007.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(root/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v005.blend'))
shift=Vector((*fit['translation_xy'],0));changed=[];linked=[]
old=fit['old'];end=Vector(((old[3][0]+old[4][0])/2,(old[3][1]+old[4][1])/2,0));start=Vector((15.2,-27.5,0));axis=end-start;denom=axis.length_squared
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.name.startswith('R151_ACT_'):continue
    zone=str(o.get('zone_id',''))
    if zone=='PAV' or o.name.startswith(('R13_','R17_')) or o.name=='R25_LOWER_PAVILION_FLOOR':
        o.matrix_world.translation+=shift;changed.append(o.name)
    elif zone=='PAV_LINK':
        o.data=o.data.copy();inv=o.matrix_world.inverted()
        for v in o.data.vertices:
            q=o.matrix_world@v.co;t=max(0,min(1,(Vector((q.x,q.y,0))-start).dot(axis)/denom));v.co=inv@(q+shift*t)
        o.data.update();linked.append(o.name)
scene=bpy.context.scene;cam=scene.camera;cam.location=(92,-130,120);cam.rotation_euler=(Vector((0,5,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=48
scene.render.filepath=str(root/'renders/qa/R151_v007_registration.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(root/'reports/R151_v007_registration_build.json').write_text(json.dumps(dict(accepted=False,file=str(out),rigid_pavilion_objects=changed,link_transition_objects=linked,translation=list(shift),remaining=['Check source and accepted-plan consistency before adopting placement.','Verify all pavilion-associated components and link connections.','Resolve lower base and terrain without inventing ground inside the source building.']),indent=2))
print('R151_v007_SAVED',len(changed),len(linked),flush=True)
