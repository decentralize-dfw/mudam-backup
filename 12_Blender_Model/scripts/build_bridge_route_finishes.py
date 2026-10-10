"""R142 extend mapped route finish atlas across existing entry bridge."""
raise RuntimeError('R142 rejected: would overwrite accepted R62 herringbone and R59 pale edge band; use R141 or newer accepted scene.')
from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base=json.loads((B/'reports/R141_build_report.json').read_text())['file'];P=json.loads((B/'reports/R142_texture_receipt.json').read_text());out=B/'scenes/MUDAM_R142_KOPRU_YOL_KAPLAMA_DEVAMI_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/base));UV='R142_ROUTE_METRIC_UV';m=bpy.data.materials.new('R142_PARK_ROUTE_ATLAS_CANDIDATE');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85;un=nt.nodes.new('ShaderNodeUVMap');un.uv_map=UV
for suffix in ['basecolor','normal']:
 im=bpy.data.images.load(str(B/'textures'/f'R142_park_routes_{suffix}.png'));im.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color';im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND';nt.links.new(un.outputs['UV'],tex.inputs['Vector'])
 if suffix=='basecolor':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 else:
  normal=nt.nodes.new('ShaderNodeNormalMap');normal.uv_map=UV;normal.inputs['Strength'].default_value=.45;nt.links.new(tex.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
x0,y0,x1,y1=P['bounds'];rows=[]
for name in ['R38_PARK_APPROACH_GROUND','R34_APPROACH_CONTINUOUS_DECK']:
 o=bpy.data.objects[name];o.data=o.data.copy();me=o.data;uv=me.uv_layers.new(name=UV);me.uv_layers.active=uv
 slot=len(me.materials);me.materials.append(m);faces=[]
 for f in me.polygons:
  if f.normal.z<.99:continue
  f.material_index=slot
  for li in f.loop_indices:
   p=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((p.x-x0)/(x1-x0),(p.y-y0)/(y1-y0))
  faces.append(dict(face=f.index,material=m.name,u=[1,0,0],v=[0,1,0],repeat_m=[x1-x0,y1-y0],origin=[x0,y0],area=f.area))
 assert faces
 rows.append(dict(name=o.name,faces=faces));o['surface_revision']='R142'
assert faces;m['source_ids']='OSM83345393,OSM49910981,OSM50643005,OSM51768378,063,096';m['limits']='Mapped route surface families; atlas patterns, module, colour, widths and relief unmeasured';o['surface_revision']='R142';o['surface_limits']=m['limits'];bpy.context.scene['stage']='R142 mapped route finish atlas';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R142_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[q['name'] for q in rows],closed_objects=[],surface_objects=rows,uv_map=UV,materials=[m.name],routes=P['routes'],atlas_bounds=P['bounds'],route_width_m=P['width_m'],geometry_changed=False,construction_acceptance=False),indent=2)+'\n')
