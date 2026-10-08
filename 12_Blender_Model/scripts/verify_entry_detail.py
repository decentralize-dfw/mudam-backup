"""Reopen P12 and test mesh validity, leaf families and changing review poses."""
from pathlib import Path
import bpy,bmesh,json,math
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/P12_build_report.json').read_text());P=json.loads((B/'config/entry_door_detail.json').read_text());E=json.loads((B/'config/entry_package.json').read_text())['entry'];bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));fail=[]
changed=[o.name for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(('P08_VESTIBULE_GLASS_','P08_VESTIBULE_TOP_')) or o.name=='ENT-02-L00_GLASS_OVER_DOOR')]
for name in r['closed_objects']+changed:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);vol=bm.calc_volume(signed=True);nm=sum(not e.is_manifold for e in bm.edges);zero=sum(f.calc_area()<1e-10 for f in bm.faces)
 if vol<=0 or nm or zero:fail.append(dict(id=name,volume=vol,nonmanifold=nm,zero_faces=zero))
 bm.free()
assert not fail,fail
pose_checks=[]
for family in r['leaf_families']:
 pivot=bpy.data.objects[family['pivot']];original=pivot.rotation_euler.z
 assert all(bpy.data.objects[name].parent==pivot for name in family['objects'])
 tests=[]
 for degrees in [0,45,90]:
  pivot.rotation_euler.z=math.radians(degrees);bpy.context.view_layer.update();points=[bpy.data.objects[name].matrix_world@v.co for name in family['objects'] for v in bpy.data.objects[name].data.vertices];tests.append(dict(angle=degrees,z_min=min(p.z for p in points),z_max=max(p.z for p in points)))
 assert max(t['z_min'] for t in tests)-min(t['z_min'] for t in tests)<1e-5
 assert max(t['z_max'] for t in tests)-min(t['z_max'] for t in tests)<1e-5
 pivot.rotation_euler.z=original;pose_checks.append(dict(pivot=pivot.name,tests=tests))
for row in P['leaf_rows']:
 assert sum(f['width_m'] for f in r['leaf_families'] if f['row']==row['id'])<E['vestibule_width_m']
assert len(r['leaf_families'])==4
roof=bpy.data.objects['P08_VESTIBULE_TOP_GLASS'];assert abs(min(v.co.z for v in roof.data.vertices)-P['vestibule_roof_z_m'])<1e-5
assert all(bpy.data.objects.get('P09_PODIUM_'+str(i)) for i in [1,2,3])
assert len([o for o in bpy.data.objects if o.name.startswith('P10_') and o.get('element_type')=='roof_glass_panel'])==359
result=dict(file=r['file'],closed_solids_checked=len(r['closed_objects'])+len(changed),failures=fail,leaf_pose_checks=pose_checks,vestibule_roof_z=P['vestibule_roof_z_m'],leaf_header_z=P['leaf_header_z_m'],earlier_roof_and_podium_preserved=True,mechanism_verified=False,construction_acceptance=False)
(B/'reports/P12_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
