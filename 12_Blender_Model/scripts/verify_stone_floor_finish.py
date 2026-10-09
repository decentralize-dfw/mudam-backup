"""R43 exact evaluated-geometry preservation and independent metric UV checks."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R43_build_report.json').read_text());P=json.loads((B/'config/stone_floor_finish.json').read_text())
def geometry(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));deps=bpy.context.evaluated_depsgraph_get();snap={}
 for ob in bpy.context.scene.objects:
  if ob.type not in ['MESH','CURVE']:continue
  o=ob.evaluated_get(deps);me=o.to_mesh()
  if me is None:continue
  data=[[list(o.matrix_world@v.co) for v in me.vertices],[list(f.vertices) for f in me.polygons],ob.hide_render,ob.hide_get()];snap[ob.name]=hashlib.sha256(repr(data).encode()).hexdigest();o.to_mesh_clear()
 return snap
before=geometry(B/'scenes'/r['base_scene']);after=geometry(R/r['file']);fail=[]
if before!=after:fail.append(dict(changed_geometry=[n for n in set(before)|set(after) if before.get(n)!=after.get(n)]))
checks=[];u=Vector(r['basis_u']);v=Vector(r['basis_v'])
for row in r['surface_objects']:
 ob=bpy.data.objects[row['name']];uv=ob.data.uv_layers[r['uv_map']];errors=[]
 for fi in row['faces']:
  f=ob.data.polygons[fi]
  if ob.data.materials[f.material_index].name!=r['material']:fail.append(dict(name=ob.name,face=fi,wrong_material=True))
  for li in f.loop_indices:
   q=ob.matrix_world@ob.data.vertices[ob.data.loops[li].vertex_index].co;expected=Vector((q.dot(u)/P['repeat_m'],q.dot(v)/P['repeat_m']));errors.append((uv.data[li].uv-expected).length)
 check=dict(name=ob.name,faces=len(row['faces']),max_uv_error=max(errors));checks.append(check)
 if max(errors)>2e-6:fail.append(check)
images=[i for i in bpy.data.images if i.name.startswith('R43_')]
if len(images)!=2 or any(not i.packed_file for i in images):fail.append('Two packed maps required')
result=dict(file=r['file'],evaluated_geometry_objects_checked=len(before),geometry_identical=before==after,uv_checks=checks,packed_images=[i.name for i in images],failures=fail,construction_acceptance=False);(B/'reports/R43_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2));assert not fail,fail
