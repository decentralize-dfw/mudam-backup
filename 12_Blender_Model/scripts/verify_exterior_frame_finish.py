from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R16_build_report.json').read_text());P=json.loads((B/'config/exterior_frame_finish.json').read_text());fail=[]
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));result={}
 for ob in bpy.context.scene.objects:
  if ob.type not in ['MESH','CURVE']:continue
  geometry=([list(v.co) for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons]) if ob.type=='MESH' else [(s.type,[list(p.co) for p in s.points],s.use_cyclic_u) for s in ob.data.splines]
  result[ob.name]=hashlib.sha256(repr([geometry,[list(x) for x in ob.matrix_world],ob.hide_render,ob.hide_get()]).encode()).hexdigest()
 return result
before=snapshot(B/'scenes'/r['base_scene']);after=snapshot(R/r['file']);changes=[n for n in set(before)|set(after) if before.get(n)!=after.get(n)]
if changes:fail.append(dict(geometry_or_visibility_changes=changes))
for row in r['assignments']:
 ob=bpy.data.objects[row['name']];m=ob.data.materials[0];p=m.node_tree.nodes.get('Principled BSDF')
 if m.name!=row['new_material'] or max(abs(a-b) for a,b in zip(p.inputs['Base Color'].default_value,P['base_color_linear']))>1e-6:fail.append(row)
result=dict(file=r['file'],failures=fail,geometry_objects_checked=len(before),material_assignments_checked=len(r['assignments']),geometry_unchanged=not changes,construction_acceptance=False);(B/'reports/R16_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));assert not fail,fail
