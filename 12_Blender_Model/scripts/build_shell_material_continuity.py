"""Extend established finish families onto later shell repairs, without geometry edits."""
from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base=json.loads((B/'reports/R130_build_report.json').read_text())['file'];out=B/'scenes/MUDAM_R131_KABUK_MALZEME_SUREKLILIGI_v001.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/base));rows=[];UV='R131_METRIC_FINISH_UV'
walls=['R116_BRIDGE_NORTH_EAST','R116_BRIDGE_NORTH_WEST','R116_STAIR_PORTAL_JAMB_JOIN','R116_LOWER_FACADE_BACKING','R117_LOWER_FACADE_CORNER_RETURN','R117_E_BRIDGE_WALL_END','R94_EAST_HIGH_WALL_JOIN','R95_EAST_OUTER_END_ABOVE_GLASS']
floors=['R116_AUD_ENTRY_FLOOR_L','R116_AUD_ENTRY_FLOOR_R','R117_E_BRIDGE_FLOOR_JOIN','R117_W_BRIDGE_FLOOR_JOIN']
mats={}
for kind,old in [('wall','R32_LIMESTONE_APPEARANCE_CANDIDATE'),('floor','R43_STONE_FLOOR_APPEARANCE_CANDIDATE')]:
 m=bpy.data.materials[old].copy();m.name='R131_'+kind.upper()+'_CONTINUITY_CANDIDATE'
 for n in m.node_tree.nodes:
  if n.type in ['UVMAP','NORMAL_MAP']:n.uv_map=UV
 m['source_ids']='004,026,051,055,077,116';m['limits']='Inherited appearance family and repeat, not surveyed material or joints';mats[kind]=m
C=json.loads((B/'config/foundation.json').read_text())['calibration'];M=C['pdf_to_utm_matrix'];fu=Vector((M[0][0],M[1][0],0)).normalized();fv=Vector((M[0][1],M[1][1],0)).normalized()
for name in walls+floors:
 o=bpy.data.objects[name];assert o.type=='MESH' and o.visible_get() and not o.hide_render;assert not o.modifiers,name
 o.data=o.data.copy();me=o.data;uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;kind='wall' if name in walls else 'floor';slot=len(me.materials);me.materials.append(mats[kind]);nm=o.matrix_world.to_3x3().inverted().transposed();faces=[]
 for f in me.polygons:
  n=(nm@f.normal).normalized()
  if kind=='wall':
   if abs(n.z)>.05:continue
   u=Vector((-n.y,n.x,0)).normalized();u=-u if (u.x<-.0001 or (abs(u.x)<.0001 and u.y<0)) else u;v=Vector((0,0,1));repeat=(3.2,2.4)
  else:
   if n.z<.99:continue
   u,v=fu,fv;repeat=(3.6,3.6)
  original=me.materials[f.material_index].name;assert original=='P05_NEUTRAL_ENVELOPE',(name,original)
  f.material_index=slot
  for li in f.loop_indices:
   q=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/repeat[0],q.dot(v)/repeat[1])
  faces.append(dict(face=f.index,material=mats[kind].name,u=list(u),v=list(v),repeat_m=repeat))
 assert faces,name
 o['surface_appearance_revision']='R131';o['surface_limits']='Continuation of neighboring accepted stone family; no new measured dimensions';rows.append(dict(name=name,faces=faces))
bpy.context.scene['stage']='R131 stone finish continuity on later shell repairs';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R131_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[r['name'] for r in rows],closed_objects=[],surface_objects=rows,uv_map=UV,materials=[m.name for m in mats.values()],geometry_changed=False,construction_acceptance=False),indent=2)+'\n')
