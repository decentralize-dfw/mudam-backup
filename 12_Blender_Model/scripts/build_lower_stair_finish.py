"""R49 appearance only: source-supported pale stair finish and grey handrail metal."""
from pathlib import Path
import bpy,json,sys,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R48_KUPESTE_BIRLESIMI_v002.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R49_ALT_MERDIVEN_YUZEY_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));UV='R49_MINERAL_FINISH_UV';stone=bpy.data.materials['R46_STONE_GRAIN_APPEARANCE_CANDIDATE'].copy();stone.name='R49_MINERAL_APPEARANCE_CANDIDATE'
for node in stone.node_tree.nodes:
 if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=UV
stone.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.42
metal=bpy.data.materials.new('R49_GREY_METAL_APPEARANCE_CANDIDATE');metal.use_nodes=True;bs=metal.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.48,.50,.49,1);bs.inputs['Metallic'].default_value=.85;bs.inputs['Roughness'].default_value=.36
for mat in [stone,metal]:mat['source_ids']='049,050,051,052';mat['status']='unmeasured_surface_appearance_candidate';mat['limits']='No calibrated sample, metal alloy, exact mineral type or fabrication finish inferred.'
targets=[o for o in bpy.context.scene.objects if not o.hide_render and (o.name.startswith('R05_TREAD_') or o.name.startswith('R05_STONE_EDGE_'))];rows=[];changed=[]
for ob in targets:
 ob.data=ob.data.copy();me=ob.data;me.materials.clear();me.materials.append(stone);uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;nm=ob.matrix_world.to_3x3().inverted().transposed();faces=[]
 for face in me.polygons:
  face.material_index=0;n=(nm@face.normal).normalized();u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.95 else Vector((1,0,0));u=-u if u.x<-.00001 else u;v=n.cross(u).normalized()
  for li in face.loop_indices:
   p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/2,p.dot(v)/2)
  faces.append(dict(face=face.index,u=list(u),v=list(v),repeat_m=2.))
 ob['surface_appearance_revision']='R49';ob['surface_source_ids']='049,050,051,052';ob['surface_appearance_status']='Pale mineral appearance candidate; grain, colour and actual material unverified; no displacement or added joints';rows.append(dict(name=ob.name,faces=faces));changed.append(ob.name)
metals=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.name.startswith(('R48_CONTINUOUS_RAIL_','R05_BASE_','R05_GROUND_EDGE_BASE_')):continue
 ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(metal)
 for face in ob.data.polygons:face.material_index=0
 ob['surface_appearance_revision']='R49';ob['surface_source_ids']='049,050,052';ob['surface_appearance_status']='Grey reflective metal family; alloy, roughness and colour not measured';metals.append(ob.name);changed.append(ob.name)
bpy.context.scene['stage']='R49 lower stair finish candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=changed,surface_objects=rows,metal_objects=metals,uv_map=UV,material=stone.name,metal_material=metal.name,geometry_changed=False,construction_acceptance=False);(B/'reports/R49_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');manifest=json.loads((B/'references/source_manifest.json').read_text());sources=[s for s in manifest if s['id'] in ['049','050','051','052','102','104','101']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R49_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits='Procedural appearance only; not material identification, calibrated colour or as-built finish.'),ensure_ascii=False,indent=2),encoding='utf8');print('R49 saved',out)
