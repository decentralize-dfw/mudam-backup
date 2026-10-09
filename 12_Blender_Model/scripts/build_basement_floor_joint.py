from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R88_BATI_MERDIVEN_CAM_KENAR_v002.blend';out=B/'scenes/MUDAM_R89_ALT_KAT_DOSEME_BIRLESIMI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));changed=[];rows=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.name.startswith(('R29_E_BOUNDARY_','R29_W_BOUNDARY_')):continue
 ps=[ob.matrix_world@v.co for v in ob.data.vertices];old=max(p.z for p in ps);assert -.8<old<-.4;top=-.2;record=dict(name=ob.name,old_top=old,new_top=top,before_vertices=[list(p) for p in ps]);inv=ob.matrix_world.inverted()
 for v,p in zip(ob.data.vertices,ps):
  if abs(p.z-old)<1e-5:p.z=top;v.co=inv@p
 ob['closure_revision']='R89 extend perimeter wall above retained suspended ceiling to ground slab underside; no room clearance change';changed.append(ob.name);rows.append(record)
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=changed,changed_inherited_objects=changed,walls=rows,source_ids=['101','102','104'],construction_acceptance=False,limits=['Section101 supports continuous perimeter wall/slab junction. Existing102/104 footprints and all below-ceiling geometry retained.','Conditional ground slab underside -0.2m is the join datum, not a surveyed detail.','Ceiling and clear height unchanged. No concealed plenum equipment or wall layers invented.','Source footprint mismatch between floors remains a separate plan registration issue.'])
bpy.context.scene['stage']='R89 basement perimeter to ground slab joint';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R89_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R89_build_report.json').write_text(json.dumps(r,indent=2));print('R89',len(changed),'walls')
