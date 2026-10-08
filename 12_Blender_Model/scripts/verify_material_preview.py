"""Reload optical release and ensure earlier verified geometry did not change."""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/material_preview.json').read_text());r=json.loads((B/'reports/P19_build_report.json').read_text())
def geometry_snapshot():
 return {o.name:hashlib.sha256(repr((tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(tuple(row) for row in o.matrix_world))).encode()).hexdigest() for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));before=geometry_snapshot();bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));after=geometry_snapshot();assert before==after,'Geometry changed during material-only pass'
checks=[]
for name in r['changed_materials'][:2]:
 n=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF');trans=n.inputs['Transmission Weight'].default_value;rough=n.inputs['Roughness'].default_value;assert trans==1 and rough<.03;checks.append(dict(name=name,transmission=trans,roughness=rough))
assert bpy.context.scene.cycles.transmission_bounces>=12
assert all(Path(p).is_file() for p in r['renders'])
result=dict(file=r['file'],mesh_objects_unchanged=len(before),failures=[],glass_checks=checks,renders_exist=True,construction_acceptance=False)
(B/'reports/P19_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
