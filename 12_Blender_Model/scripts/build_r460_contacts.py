import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R458_BATI_SERVIS_AVLU_KOTU_ADAY_v001.blend'))
# Keep the inherited support until its mixed-level ground can be rebuilt with breaklines.
ob=bpy.data.objects['R152_FORECOURT_0'];ob.hide_render=False;ob.hide_viewport=False;ob.data.materials.clear();ob.data.materials.append(bpy.data.objects['R152_CLASS2_TERRAIN'].data.materials[0]);ob['R460']='Residual old forecourt retained as provisional grass support to avoid exposing a terrain hole. Not elevation accepted.'
c=json.loads((R/'reports/R457_LOADING_COURT_GRADE.json').read_text())['coefficients'];w=json.loads((R/'reports/R458_WEST_PLAZA_GRADE.json').read_text())['coefficients'];xe=-120+465*220/1400
ob=bpy.data.objects['R457_NORTH_LOADING_COURT'];count=0
for v in ob.data.vertices:
 x,y,z=v.co;t=max(0,min(1,(x-xe)/2));weight=(1-t*t*(3-2*t))*max(0,min(1,(y-(95-340*220/1400))/(21*220/1400)));a=[1,xe,y,xe*xe,xe*y,y*y];delta=sum(ai*(wi-ci) for ai,wi,ci in zip(a,w,c))*weight
 if abs(delta)>1e-8:v.co.z+=delta;count+=1
ob.data.update();out=R/'scenes/MUDAM_R460_KUZEY_AVLU_GECIS_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out))
(R/'reports/R460_COURT_CONTACT.json').write_text(json.dumps(dict(scene=out.name,modifiedVertices=count,blendWidth=2,accepted=False,published=False,limits=['Residual forecourt grass support has unverified slopes; quadratic ground attempt R459 rejected RMS .446m max1.227m.','2m ramp transition chosen after inspecting residuals: residuals are diagnostic, not independent holdout acceptance.','Full museum ring remains unfinished.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(-28,48,95));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((-28,48,-5))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=100;s.render.filepath=str(R/'renders/qa/R460_service_plaza.png');bpy.ops.render.render(write_still=True)
