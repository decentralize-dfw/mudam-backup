"""P21 checkpoint export of visible current geometry, preserving element IDs."""
from pathlib import Path
import bpy,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';sys.path.insert(0,str(B/'scripts'));from release_utils import verified_current_scene
r=verified_current_scene()
bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));deps=bpy.context.evaluated_depsgraph_get();bpy.ops.object.select_all(action='DESELECT');selected=[];bounds=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 ob.select_set(True);selected.append(ob.name);eo=ob.evaluated_get(deps);bounds.extend(eo.matrix_world@Vector(c) for c in eo.bound_box)
out=B/'exports'/f"{Path(r['file']).stem}_preview.glb";out.parent.mkdir(exist_ok=True)
if out.exists():raise RuntimeError('Export version exists')
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_yup=True)
minimum=[min(p[i] for p in bounds) for i in range(3)];maximum=[max(p[i] for p in bounds) for i in range(3)]
result=dict(source_scene=r['file'],file=out.relative_to(R).as_posix(),selected_mesh_count=len(selected),selected_names=selected,blender_world_bounds=dict(min=minimum,max=maximum),format='glTF 2.0 binary; meters; Y-up',limitations=['Checkpoint geometry only, not a finished museum model.','Generic sky lighting is not embedded in GLB. Material response depends on viewer support for transmission.','Element IDs retained; optimization and target engine review remain open.'],construction_acceptance=False)
(B/'reports/P21_export_report.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('P21_EXPORTED',out,len(selected))
