"""Carry the existing link floor into the same placement as its walls and roof."""
from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
out=R/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v011.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R151_ACT_CEVRE_ADAY_v009.blend'))
fit=json.loads((R/'reports/R151_pavilion_registration_candidate.json').read_text())
shift=Vector((*fit['translation_xy'],0));old=fit['old'];start=Vector((15.2,-27.5,0));end=Vector(((old[3][0]+old[4][0])/2,(old[3][1]+old[4][1])/2,0));axis=end-start
o=bpy.context.scene.objects['P05_LINK_FLOOR'];o.data=o.data.copy();inv=o.matrix_world.inverted()
# Split at clamp planes before the piecewise affine displacement, so faces do not
# interpolate across a transition kink and leave an endpoint wedge uncovered.
bm=bmesh.new();bm.from_mesh(o.data)
for p in (start,end):
 normal=o.matrix_world.to_3x3().transposed()@axis.normalized()
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=inv@p,plane_no=normal,clear_inner=False,clear_outer=False)
bm.to_mesh(o.data);bm.free()
for v in o.data.vertices:
 p=o.matrix_world@v.co;t=max(0,min(1,(Vector((p.x,p.y,0))-start).dot(axis)/axis.length_squared));v.co=inv@(p+shift*t)
o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'reports/R151_v011_link_floor_build.json').write_text(json.dumps(dict(file=str(out),changed=['P05_LINK_FLOOR'],new_objects=[],reason='Floor lacked PAV_LINK zone metadata. Split at transition clamp planes, then apply identical endpoint displacement; retain original Z and thickness. v010 failed endpoint sample.',translation=list(shift),accepted=False),indent=2))
print('R151_V011_SAVED',flush=True)
