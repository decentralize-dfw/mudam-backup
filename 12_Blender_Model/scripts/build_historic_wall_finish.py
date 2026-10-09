"""R55: appearance on the existing OSM-derived wall and moat; no geometry move."""
from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R54_TARIHI_DUVAR_ALT_CAM_v002.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R55_TARIHI_DUVAR_YUZEY_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));dep=bpy.context.evaluated_depsgraph_get();UV='R55_CONTEXT_METRIC_UV';up=Vector((0,0,1));rows=[];changed=[];baked=[]
def mat(name,rough,strength):
 m=bpy.data.materials.new('R55_'+name.upper()+'_APPEARANCE_CANDIDATE');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough;uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map=UV
 for suffix in ['basecolor','normal']:
  im=bpy.data.images.load(str(B/'textures'/f'R55_{name}_candidate_{suffix}.png'));im.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color';im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT';nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
  if suffix=='basecolor':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  else:
   nn=nt.nodes.new('ShaderNodeNormalMap');nn.uv_map=UV;nn.inputs['Strength'].default_value=strength;nt.links.new(tex.outputs['Color'],nn.inputs['Color']);nt.links.new(nn.outputs['Normal'],bs.inputs['Normal'])
 m['source_ids']='004,063,065,086,116';m['status']='procedural_context_appearance_not_fabric_survey';m['limits']='Course dimensions, exact stones, patina and turf species are not reconstructed. No geometry displacement.';return m
stone=mat('historic_masonry',.86,.55);grass=mat('moat_turf',.94,.22)
targets=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o.visible_get() and (o.name.startswith('R35_WALL_') or o.name=='R35_MOAT_GROUND')]
for ob in targets:
 if ob.modifiers:
  assert all(m.type=='BOOLEAN' for m in ob.modifiers),ob.name
  me=bpy.data.meshes.new_from_object(ob.evaluated_get(dep),preserve_all_data_layers=True,depsgraph=dep);ob.modifiers.clear();ob.data=me;baked.append(ob.name)
 else:ob.data=ob.data.copy();me=ob.data
 wall=ob.name.startswith('R35_WALL_');material=stone if wall else grass;slot=len(me.materials);me.materials.append(material);uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;nm=ob.matrix_world.to_3x3().inverted().transposed();faces=[]
 for f in me.polygons:
  n=(nm@f.normal).normalized()
  if not wall and n.z<.99:continue
  u=up.cross(n).normalized() if abs(n.z)<.95 else Vector((1,0,0));u=-u if u.x<-.00001 else u;v=n.cross(u).normalized();f.material_index=slot
  for li in f.loop_indices:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/4,q.dot(v)/3)
  faces.append(dict(face=f.index,u=list(u),v=list(v),repeat_m=[4.,3.],material=material.name))
 ob['surface_appearance_revision']='R55';ob['surface_source_ids']='004,063,065,086,116';ob['surface_appearance_status']='Rough coursed stone or turf visualization candidate; exact weathering and species unknown';changed.append(ob.name);rows.append(dict(name=ob.name,faces=faces))
bpy.context.scene['stage']='R55 historic wall and moat appearance candidates';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R55_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=changed,surface_objects=rows,baked_boolean_objects=baked,uv_map=UV,materials=[stone.name,grass.name],evaluated_geometry_changed=False,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['004','063','065','086','116']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R55_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=json.loads((B/'reports/R55_texture_receipt.json').read_text())['limits']),ensure_ascii=False,indent=2),encoding='utf8');print('R55',len(rows),'objects',sum(len(q['faces']) for q in rows),'mapped faces')
