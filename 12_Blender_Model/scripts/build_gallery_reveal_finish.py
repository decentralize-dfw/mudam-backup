"""R53 material/UV coordination of the accepted R52 recess geometry."""
from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R52_GALERI_CAM_HIZA_v009.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R53_GALERI_NIS_YUZEY_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));UV='R53_REVEAL_METRIC_UV';dep=bpy.context.evaluated_depsgraph_get()
def clone(old,new):
 m=bpy.data.materials[old].copy();m.name=new
 for node in m.node_tree.nodes:
  if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=UV
 return m
stone=clone('R32_LIMESTONE_APPEARANCE_CANDIDATE','R53_REVEAL_LIMESTONE_CANDIDATE');floor=clone('R43_STONE_FLOOR_APPEARANCE_CANDIDATE','R53_REVEAL_SILL_STONE_CANDIDATE');floor.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.50
soffit=bpy.data.materials.new('R53_LINEAR_MINERAL_SOFFIT_CANDIDATE');soffit.use_nodes=True;nt=soffit.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.62;uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map=UV
for suffix in ['basecolor','normal']:
 im=bpy.data.images.load(str(B/'textures'/f'R53_soffit_linear_grain_candidate_{suffix}.png'));im.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color';im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT';nt.links.new(uvn.outputs['UV'],tex.inputs['Vector'])
 if suffix=='basecolor':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 else:
  nn=nt.nodes.new('ShaderNodeNormalMap');nn.uv_map=UV;nn.inputs['Strength'].default_value=.25;nt.links.new(tex.outputs['Color'],nn.inputs['Color']);nt.links.new(nn.outputs['Normal'],bs.inputs['Normal'])
for m in [stone,floor,soffit]:m['source_ids']='004,061,062,116';m['status']='procedural_appearance_candidate_not_measured';m['limits']='Material family only. Courses, grain, colour, roughness and mineral identity are not calibrated. No displacement.'
build52=json.loads((B/'reports/R52_build_report.json').read_text());windows={q['bay']:q for q in build52['windows']};rows=[];changed=[];baked=[]
targets=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render and ((o.name.startswith('R27_') and not any(s in o.name for s in ['FRAME','GLASS'])) or (o.name.startswith('R52_BAY_') and any(s in o.name for s in ['THRESHOLD','SOFFIT','RETURN_'])))]
for ob in targets:
 if ob.modifiers:
  assert all(m.type=='BOOLEAN' for m in ob.modifiers),ob.name
  me=bpy.data.meshes.new_from_object(ob.evaluated_get(dep),preserve_all_data_layers=True,depsgraph=dep);ob.modifiers.clear();ob.data=me;baked.append(ob.name)
 else:ob.data=ob.data.copy();me=ob.data
 me.materials.clear()
 for m in [stone,floor,soffit]:me.materials.append(m)
 uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;normal_matrix=ob.matrix_world.to_3x3().inverted().transposed();faces=[]
 for face in me.polygons:
  n=(normal_matrix@face.normal).normalized();slot=0;repeat=[3.2,2.4]
  if 'THRESHOLD' in ob.name and n.z>.99:slot=1;repeat=[3.6,3.6]
  if ('SOFFIT' in ob.name or ob.name=='R27_CONTINUOUS_HEAD') and n.z<-.99:slot=2
  if abs(n.z)>.95:
   bay=2 if '_2_' in ob.name else 4;u=Vector(windows[bay]['outward']);v=Vector((0,0,1)).cross(u)
  else:
   u=Vector((0,0,1)).cross(n).normalized();u=-u if u.x<-.00001 else u;v=n.cross(u).normalized()
  face.material_index=slot
  for li in face.loop_indices:
   p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/repeat[0],p.dot(v)/repeat[1])
  faces.append(dict(face=face.index,u=list(u),v=list(v),repeat_m=repeat,material=me.materials[slot].name))
 ob['surface_appearance_revision']='R53';ob['surface_source_ids']='004,061,062,116';ob['surface_appearance_status']='Stone sides/sill and linear mineral underside candidate; not measured or material identification';rows.append(dict(name=ob.name,faces=faces));changed.append(ob.name)
bpy.context.scene['stage']='R53 gallery recess material candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=changed,surface_objects=rows,baked_boolean_objects=baked,uv_map=UV,materials=[stone.name,floor.name,soffit.name],evaluated_geometry_changed=False,construction_acceptance=False);(B/'reports/R53_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['004','061','062','102','116','PDF2016']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R53_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits='Uncalibrated appearance candidates only. Stone sidewall courses and slab sill supported by061/062; linear underside grain not proof of precise construction method.'),ensure_ascii=False,indent=2),encoding='utf8');print('R53',len(rows),'objects',sum(len(r['faces']) for r in rows),'mapped faces')
