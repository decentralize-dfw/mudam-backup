import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R569_GUNEY_SUR_TAM_DONUS_KAPALI_ADAY_v001.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[]
for r in json.loads((R/'reports/R558_PAVILION_RETURN_GROUND.json').read_text()):
 for p in r['sections']:
  if 49<=p['x']<=50.5:continue
  h,v,n,f,o,m=bpy.context.scene.ray_cast(dg,Vector((p['x'],r['y'],-1)),Vector((0,0,-1)),distance=15);rows.append(dict(x=p['x'],y=r['y'],sourceGround=p['z'][1],candidate=v.z if h else None,object=o.name if h else None))
(R/'reports/R572_RETURN_GROUND_CONTACTS.json').write_text(json.dumps(rows,indent=2))
for o in bpy.context.scene.objects:
 if o.name.startswith('R158_TREE_'):o.hide_render=True
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;bpy.ops.object.camera_add(location=(42,-65,40));s.camera=bpy.context.object;s.camera.rotation_euler=(Vector((56,-56,-2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=35;s.render.filepath=str(R/'renders/qa/R572_return_tree_hidden_QA.png');bpy.ops.render.render(write_still=True)
