"""Extend established finish families onto later shell repairs, without geometry edits."""
from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base=json.loads((B/'reports/R137_build_report.json').read_text())['file'];out=B/'scenes/MUDAM_R138_GIRIS_DOLASIM_TAS_ZEMIN_v002.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/base));rows=[];UV='R138_METRIC_FINISH_UV'
walls=[]
floors=['P05_FLOOR_L00_ENT','R28_E_CIRCULATION_FLOOR','R28_W_CIRCULATION_FLOOR']
mats={}
for kind,old in [('floor','R43_STONE_FLOOR_APPEARANCE_CANDIDATE')]:
 m=bpy.data.materials[old].copy();m.name='R138_'+kind.upper()+'_CONTINUITY_CANDIDATE'
 for n in m.node_tree.nodes:
  if n.type in ['UVMAP','NORMAL_MAP']:n.uv_map=UV
 m['source_ids']='017,026,070,077,102';m['limits']='Inherited appearance family and repeat, not surveyed material or joints';mats[kind]=m
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
 o['surface_appearance_revision']='R138';o['surface_limits']='Continuation of neighboring accepted stone family; no new measured dimensions';rows.append(dict(name=name,faces=faces))
bpy.context.scene['stage']='R138 entrance and gallery circulation stone floors';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R138_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[r['name'] for r in rows],closed_objects=[],surface_objects=rows,uv_map=UV,materials=[m.name for m in mats.values()],geometry_changed=False,construction_acceptance=False),indent=2)+'\n')
