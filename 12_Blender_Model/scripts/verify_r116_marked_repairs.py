"""Full-scene 2.1m review headroom across tread interiors; not statutory acceptance."""
from pathlib import Path
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];r=json.loads((B/'reports/R116_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));vs=[];fs=[];owners=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get():continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
tree=BVHTree.FromPolygons(vs,fs);up=Vector((0,0,1));checks=[];C=json.loads((B/'config/foundation.json').read_text())['calibration']
def pt(x,y,z):
 k=C['canonical_to_pdf_scale'];ox,oy=C['canonical_to_pdf_offset'];M=C['pdf_to_utm_matrix'];a=k*x+ox;b=k*y+oy;return Vector((M[0][0]*a+M[0][1]*b+M[0][2]-293425,M[1][0]*a+M[1][1]*b+M[1][2]-5499960,z))
def check(label,ok,**data):checks.append(dict(label=label,passed=bool(ok),**data))
for n in ['R87_ROOM_SIDE','R87_ROOM_FRONT_LEFT','R87_ROOM_FRONT_RIGHT','R87_ROOM_DOOR_HEAD']:check('SS4 removed '+n,bpy.data.objects[n].hide_render)
for n,z in [('R116_PETITE_CAFE_BOUNDARY',13.723118),('R116_BRIDGE_NORTH_WEST',12.523118),('R116_BRIDGE_NORTH_EAST',12.523118)]:
 o=bpy.data.objects[n];check('wall top '+n,abs(max((o.matrix_world@v.co).z for v in o.data.vertices)-z)<.001)
s,dx,dy=C['basement_registration']['source_to_canonical']
for side,x,y in [('L',483,418),('L',483,420),('R',560,418),('R',561,420)]:
 a=pt(s*x+dx,s*y+dy,-5.3062935);h=tree.ray_cast(a,-up,.06);check('SS8 floor '+str((side,x,y)),h[0] is not None,owner=None if h[0] is None else owners[h[2]])
wr=json.loads((B/'reports/R54_build_report.json').read_text());wp=json.loads((B/'config/lower_windows_wall_relative.json').read_text());origin=Vector(wr['origin']);axis=Vector(wr['axis']);normal=Vector(wr['inside'])
for i,t in enumerate(wp['centers_along_wall_m'],1):
 a=origin+axis*t-normal*1+up*((wp['inner_sill_z']+wp['glass_head_z'])/2);h=tree.ray_cast(a,normal,1.7);name=None if h[0] is None else owners[h[2]];check('SS1 lower window '+str(i),name==f'R54_WINDOW_{i:02d}_GLASS',owner=name)
for n in ['R116_STAIR_PORTAL_JAMB_JOIN','R116_E_GALLERY_END_RETURN']:
 o=bpy.data.objects[n];check('SS3/7 closure '+n,not o.hide_render and len(o.data.polygons)>0)
q=dict(file=r['file'],checks=checks,failures=[c for c in checks if not c['passed']],construction_acceptance=False,limits=['Local geometry and user-marked boundary checks only; not full building or surveyed accuracy acceptance.']);(B/'reports/R116_verification.json').write_text(json.dumps(q,indent=2));print(q['failures'])
