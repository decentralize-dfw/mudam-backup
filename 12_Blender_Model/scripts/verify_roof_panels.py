"""Reopen the saved P10 scene and check solid integrity and preserved earlier work."""
from pathlib import Path
import bpy,bmesh,json,math
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';report=json.loads((B/'reports/P10_build_report.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/report['file']));fail=[];minimum=1e9;total=0
for name in report['closed_objects']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);volume=bm.calc_volume(signed=True);nonmanifold=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces);finite=all(math.isfinite(c) for v in bm.verts for c in v.co)
 if nonmanifold or zero or volume<=0 or not finite:fail.append(dict(id=name,volume=volume,nonmanifold=nonmanifold,zero_faces=zero,finite=finite))
 minimum=min(minimum,volume);total+=volume;bm.free()
assert not fail,fail[:20]
assert all(f['partition_error_m2']<1e-4 for f in report['facets'])
assert all(bpy.data.objects[f['source']].hide_render for f in report['facets'])
assert all(bpy.data.objects.get('P09_PODIUM_'+str(i)) for i in [1,2,3])
assert len([o for o in bpy.data.objects if o.type=='EMPTY' and o.name.startswith('ENT-')])==6
for key in ['087','119','116']:
 cam=bpy.data.objects['P07_PHOTO_'+key+'_CONDITIONAL'];assert cam.data.background_images[0].image.packed_file
result=dict(file=report['file'],checked_closed_solids=len(report['closed_objects']),failures=fail,minimum_volume_m3=minimum,glass_panels=report['panel_count'],facets=len(report['facets']),max_partition_error_m2=max(f['partition_error_m2'] for f in report['facets']),old_surface_hidden=True,entry_openings_preserved=6,podium_preserved=True,three_photo_cameras_preserved=True,construction_acceptance=False)
(B/'reports/P10_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
