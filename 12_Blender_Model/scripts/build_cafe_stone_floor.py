"""R148 stone finish continuity on existing west cafe floor."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base=json.loads((B/'reports/R147_build_report.json').read_text())['file'];out=B/'scenes/MUDAM_R148_KAFE_TAS_DOSEME_v001.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/base));rows=[];UV='R148_METRIC_FINISH_UV'
walls=[]
floors=['P05_FLOOR_L00_WEST_CAFE']
mats={}
for kind,old in [('floor','R43_STONE_FLOOR_APPEARANCE_CANDIDATE')]:
 m=bpy.data.materials[old].copy();m.name='R148_'+kind.upper()+'_CONTINUITY_CANDIDATE'
 for n in m.node_tree.nodes:
  if n.type in ['UVMAP','NORMAL_MAP']:n.uv_map=UV
 m['source_ids']='CF01,CF02,102';m['limits']='Inherited appearance family and repeat, not surveyed material or joints';mats[kind]=m
C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];fu=Vector((M[0][0],M[1][0],0)).normalized();fv=Vector((M[0][1],M[1][1],0)).normalized()
for name in walls+floors:
 o=bpy.data.objects[name];assert o.type=='MESH' and o.visible_get() and not o.hide_render

 if o.modifiers:
  dep=bpy.context.evaluated_depsgraph_get();evaluated=o.evaluated_get(dep);o.data=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=dep);o.modifiers.clear()
 else:o.data=o.data.copy()
 me=o.data;uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;kind='wall' if name in walls else 'floor';slot=len(me.materials);me.materials.append(mats[kind]);nm=o.matrix_world.to_3x3().inverted().transposed();faces=[]
 for f in me.polygons:
  n=(nm@f.normal).normalized()
  if kind=='wall':
   if abs(n.z)>.05:continue
   u=Vector((-n.y,n.x,0)).normalized();u=-u if (u.x<-.0001 or (abs(u.x)<.0001 and u.y<0)) else u;v=Vector((0,0,1));repeat=(3.2,2.4)
  else:
   if n.z<.99:continue
   u,v=fu,fv;repeat=(3.6,3.6)
  original=me.materials[f.material_index].name;assert original in ['P05_NEUTRAL_ENVELOPE','P05_FLOOR_REFERENCE'],(name,original)
  f.material_index=slot
  for li in f.loop_indices:
   q=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/repeat[0],q.dot(v)/repeat[1])
  faces.append(dict(face=f.index,material=mats[kind].name,u=list(u),v=list(v),repeat_m=repeat))
 assert faces,name
 o['surface_appearance_revision']='R148';o['surface_limits']='Continuation of neighboring accepted stone family; no new measured dimensions';rows.append(dict(name=name,faces=faces))
sources=[q for q in json.loads((B/'references/source_manifest.json').read_text()) if q['id'] in ['CF01','CF02','102']]
for q in sources:assert hashlib.sha256((R/q['path']).read_bytes()).hexdigest()==q['sha256']
bpy.context.scene['stage']='R148 west cafe stone floor';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R148_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[r['name'] for r in rows],closed_objects=[],surface_objects=rows,uv_map=UV,materials=[m.name for m in mats.values()],sources=sources,geometry_changed=False,construction_acceptance=False),indent=2)+'\n')
