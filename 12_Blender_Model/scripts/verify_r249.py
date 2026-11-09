import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');p=R/'reports/R249_DISTRICT_FOUNDATIONS.json';d=json.loads(p.read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R249_ALT_MAHALLE_TEMEL_ADAY_v001.blend'));s=bpy.context.scene
# View the largest corrected contact, with the surrounding authored terrain.
o=s.objects['R182_DISTRICT_164179266'];center=sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices);s.camera.location=center+Vector((35,-48,28));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=65;s.render.resolution_x=1200;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=12;s.render.filepath=str(R/'renders/qa/R249_largest_contact.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'exports/r152_clean/r249_foundations_REVIEW.glb'));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);checks.append(dict(name=o.name,boundary=sum(e.is_boundary for e in bm.edges),zero=sum(f.calc_area()<1e-10 for f in bm.faces),finite=all(math.isfinite(x) for v in bm.verts for x in v.co)));bm.free()
assert len(checks)==len(d['changed']);assert all(r['boundary']==0 and r['zero']==0 and r['finite'] for r in checks)
d['reopenedGLB']=checks;d['blendReopened']=True;p.write_text(json.dumps(d,indent=2));print('VALIDATED',len(checks),flush=True)
