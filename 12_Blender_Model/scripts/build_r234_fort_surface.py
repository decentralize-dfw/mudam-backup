from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
R=Path('C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model');bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R232_ERASMUS_ENINE_CAM_KOT_ADAY_v001.blend'));mat=bpy.data.materials['R172_MOAT_EARTH'].copy();mat.name='R234_DRY_FORT_EARTH';mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.29,.25,.18,1);bs.inputs['Roughness'].default_value=.94;mat.diffuse_color=(.29,.25,.18,1);changes=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith('R187_OUTER_BASTIONS'):continue
 changes.append(dict(name=o.name,old=[m.name for m in o.data.materials],area=sum(p.area for p in o.data.polygons)));o.data.materials.clear();o.data.materials.append(mat)
assert changes
path=R/'scenes/MUDAM_R234_KALE_TOPRAK_YUZEY_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);bpy.ops.wm.open_mainfile(filepath=str(path))
for o in bpy.context.scene.objects:o.select_set(o.name.startswith('R187_OUTER_BASTIONS'))
glb=R/'exports/r152_clean/r234_fort_earth_REVIEW.glb';bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb));checks=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);checks.append(dict(name=o.name,zero=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(c['zero']for c in checks)
(R/'reports/R234_FORT_SURFACE.json').write_text(json.dumps(dict(accepted=False,published=False,geometryChanged=False,changes=changes,reopen=checks,scope='Outer fort earth surfaces only; green moat vegetation retained',limits=['Material correction only; geometry and11region acceptance unchanged','Dry earth colour approximate from source appearance; no scan image copied','Stone weathering/earth texture, vegetation and boundary geometry remain incomplete']),indent=2))
bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;t=Vector((-210,-175,-20));s.camera.location=t+Vector((90,-150,180));s.camera.rotation_euler=(t-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=260;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.cycles.samples=8;s.render.filepath=str(R/'renders/qa/R234_fort_material_candidate.png');bpy.ops.render.render(write_still=True)
