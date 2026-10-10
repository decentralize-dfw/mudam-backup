"""R141 stone finish continuity on existing west entry and cafe walls."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base=json.loads((B/'reports/R140_build_report.json').read_text())['file'];out=B/'scenes/MUDAM_R141_GIRIS_KAFE_TAS_DUVARLAR_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/base));UV='R141_STONE_METRIC_UV';mats={}
for kind,old in [('grain','R46_STONE_GRAIN_APPEARANCE_CANDIDATE'),('joint','R32_LIMESTONE_APPEARANCE_CANDIDATE')]:
 m=bpy.data.materials[old].copy();m.name='R141_'+kind.upper()+'_STONE_CANDIDATE'
 for node in m.node_tree.nodes:
  if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=UV
 m['source_ids']='066,097,093,102';m['limits']='Existing stone visual family, no surveyed slab dimensions or physical colour';mats[kind]=m
ceilings=[];stairs=[];walls=['R82_ENTRY_INNER_WALL','R83_CAFE_BACK_WALL','R83_CAFE_ENTRY_HEAD'];rows=[]
for name in ceilings+stairs+walls:
 o=bpy.data.objects[name];assert not o.hide_render and o.visible_get();o.data=o.data.copy();me=o.data;nm=o.matrix_world.to_3x3().inverted().transposed();uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;slots={}
 for kind,m in mats.items():slots[kind]=len(me.materials);me.materials.append(m)
 faces=[]
 for f in me.polygons:
  old=me.materials[f.material_index].name
  if old!='P05_NEUTRAL_ENVELOPE':continue
  n=(nm@f.normal).normalized()
  if name in ceilings and n.z>=-.05:continue
  kind='grain' if name in stairs or (name in walls and abs(n.z)>.05) else 'joint';repeat=(2.,2.) if kind=='grain' else (3.2,2.4)
  u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.95 else Vector((1,0,0));u=-u if (u.x<-.00001 or (abs(u.x)<.00001 and u.y<0)) else u;v=n.cross(u).normalized()
  if kind=='joint' and abs(n.z)<.05:v=Vector((0,0,1))
  f.material_index=slots[kind]
  for li in f.loop_indices:
   p=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/repeat[0],p.dot(v)/repeat[1])
  faces.append(dict(face=f.index,material=mats[kind].name,u=list(u),v=list(v),repeat_m=repeat))
 assert faces,name
 o['surface_appearance_revision']='R141';o['surface_source_ids']='066,097,093,102';o['surface_limits']='Photographed stone family. Inherited procedural grain and joints are not a surveyed panel schedule.';rows.append(dict(name=name,faces=faces))
sources=[q for q in json.loads((B/'references/source_manifest.json').read_text()) if q['id'] in ['066','097','093','102']]
for q in sources:assert hashlib.sha256((R/q['path']).read_bytes()).hexdigest()==q['sha256']
bpy.context.scene['stage']='R141 entry and cafe stone wall material continuity';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R141_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[q['name'] for q in rows],closed_objects=[],surface_objects=rows,uv_map=UV,materials=[m.name for m in mats.values()],sources=sources,geometry_changed=False,construction_acceptance=False),indent=2)+'\n');print('R141',len(rows),'objects',sum(len(q['faces']) for q in rows),'faces')
