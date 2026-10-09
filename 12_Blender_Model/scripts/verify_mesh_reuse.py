"""Reopen both scenes: compare evaluated world geometry and UVs, not raw local hashes."""
from pathlib import Path
import bpy,json,numpy as np
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/R41_build_report.json').read_text())
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));deps=bpy.context.evaluated_depsgraph_get();out={}
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  ob=o.evaluated_get(deps);me=ob.to_mesh()
  if me is None:continue
  out[o.name]=dict(vertices=np.array([list(ob.matrix_world@v.co) for v in me.vertices],dtype=float),polys=[(tuple(p.vertices),p.material_index,p.use_smooth) for p in me.polygons],uv=[(l.name,[(float(d.uv.x),float(d.uv.y)) for d in l.data]) for l in me.uv_layers],materials=[m.name if m else None for m in me.materials],visibility=[o.hide_render,o.hide_get()],source_properties={k:str(v) for k,v in o.items() if k not in ['mesh_reuse_revision','mesh_reuse_max_vertex_delta_m']})
  ob.to_mesh_clear()
 return out
before=snapshot(B/'scenes'/r['base_scene']);after=snapshot(R/r['file']);fail=[];rows=[]
if set(before)!=set(after):fail.append(dict(object_name_mismatch=list(set(before)^set(after))))
for name,a in before.items():
 b=after.get(name)
 if b is None:continue
 if a['vertices'].shape!=b['vertices'].shape:fail.append(dict(name=name,vertex_shape=True));continue
 err=float(np.max(np.linalg.norm(a['vertices']-b['vertices'],axis=1))) if len(a['vertices']) else 0.;row=dict(name=name,max_world_vertex_delta_m=err);rows.append(row)
 for k in ['polys','uv','materials','visibility','source_properties']:
  if a[k]!=b[k]:fail.append(dict(name=name,changed=k))
 if err>r['world_vertex_tolerance_m']:fail.append(row)
result=dict(file=r['file'],objects_checked=len(rows),max_world_vertex_delta_m=max(row['max_world_vertex_delta_m'] for row in rows),numerical_tolerance_not_survey_accuracy=True,topology_uv_material_metadata_checked=True,objects=rows,failures=fail,construction_acceptance=False);(B/'reports/R41_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(checked=len(rows),max_delta=result['max_world_vertex_delta_m'],failures=fail),indent=2));assert not fail,fail
