"""R104 reconcile the back faces of an existing continuous lower stair wall."""
from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];C=json.loads((B/'config/foundation.json').read_text())['calibration'];base=json.loads((B/'reports/R103_build_report.json').read_text());out=B/'scenes/MUDAM_R104_ALT_MERDIVEN_DUVAR_DEVAMI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B.parent/base['file']))
ob=bpy.data.objects['R29_W_DIVIDER_END'];neighbor=bpy.data.objects['R07_STAIRWELL_STONE_WEST'];before=[list(ob.matrix_world@v.co) for v in ob.data.vertices];ref=[neighbor.matrix_world@v.co for v in neighbor.data.vertices]
# Existing R76 front face and source termination remain fixed. Only the four
# vertices on the gallery-facing back are projected to their neighbor's plane.
axis=(ref[1]-ref[0]);axis.z=0;axis.normalize();normal=axis.cross(Vector((0,0,1))).normalized();plane=ref[2];back=[2,3,6,7];old_offsets=[];ob.data=ob.data.copy();iv=ob.matrix_world.inverted()
for i in back:
 p=ob.matrix_world@ob.data.vertices[i].co;d=(p-plane).dot(normal);old_offsets.append(d);ob.data.vertices[i].co=iv@(p-normal*d)
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob['R104_note']='Existing continuous stair-wall back aligned to R07; R76 front face, access termination and z extents retained. Neighbor 300mm thickness remains a visualization candidate.'
r=dict(file=out.relative_to(B.parent).as_posix(),base_scene=Path(base['file']).name,closed_objects=[ob.name],changed_inherited_objects=[ob.name],object=ob.name,neighbor=neighbor.name,before_world=before,back_indices=back,plane_point=list(plane),plane_normal=list(normal),old_back_offsets=old_offsets,construction_acceptance=False,limits=['Source104 continuous wall and previously adopted R76 registration retained.','Only the 50mm back-face step between two existing wall pieces is reconciled; no opening, wall axis or floor level moved.','300mm neighbor thickness is inherited and unmeasured; this is geometric continuity, not an as-built thickness claim.'])
bpy.context.scene['current_file']=out.name;bpy.context.scene['stage']='R104 lower stair wall back continuity';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R104_build_report.json').write_text(json.dumps(r,indent=2));print('R104 old offsets',old_offsets)
