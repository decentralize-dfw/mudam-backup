"""Reload P11, verify closed volumes, lineage and node attachments."""
from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/P11_build_report.json').read_text());previous=json.loads((B/'reports/P10_build_report.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']))
fail=[]
for name in r['closed_objects']+previous['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);volume=bm.calc_volume(signed=True);nonmanifold=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces)
 if volume<=0 or nonmanifold or zero:fail.append(dict(id=name,volume=volume,nonmanifold=nonmanifold,zero_faces=zero))
 bm.free()
assert not fail,fail[:15]
assert all(bpy.data.objects[n].hide_render for n in r['hidden_superseded'])
assert all(bpy.data.objects.get('P09_PODIUM_'+str(i)) for i in [1,2,3])
assert len([o for o in bpy.data.objects if o.type=='EMPTY' and o.name.startswith('ENT-')])==6
# All east rod ends project to the grid intersections, not arbitrary points in glass.
surface=bpy.data.objects['P06_EAST_GLAZED_ROOF'];p=[surface.matrix_world@v.co for v in surface.data.vertices];normal=(p[1]-p[0]).cross(p[3]-p[0]).normalized()
if normal.z<0:normal=-normal
cfg=json.loads((B/'config/side_roof_panels.json').read_text());grid=[p[0]*(1-i/cfg['east_columns'])*(1-j/cfg['east_slope_rows'])+p[1]*(i/cfg['east_columns'])*(1-j/cfg['east_slope_rows'])+p[2]*(i/cfg['east_columns'])*(j/cfg['east_slope_rows'])+p[3]*(1-i/cfg['east_columns'])*(j/cfg['east_slope_rows'])-normal*.06 for i in range(cfg['east_columns']+1) for j in range(cfg['east_slope_rows']+1)]
errors=[]
for ob in bpy.data.objects:
 if ob.name.startswith('P11_EAST_ROD_'):
  end=sum((v.co for v in list(ob.data.vertices)[8:]),Vector())/8;errors.append(min((end-g).length for g in grid))
assert errors and max(errors)<1e-4,max(errors)
result=dict(file=r['file'],closed_solids_checked=len(r['closed_objects'])+len(previous['closed_objects']),failures=fail,new_panels=r['panel_count'],max_panel_plane_deviation_m=r['max_panel_plane_deviation_m'],rod_end_attachment_max_error_m=max(errors),rod_ends_checked=len(errors),entry_and_podium_preserved=True,pavilion_panelization=False,construction_acceptance=False)
(B/'reports/P11_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
