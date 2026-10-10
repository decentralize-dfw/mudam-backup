"""R133 metric atlas on unchanged park ground; v001-v003 subdivisions rejected."""
from pathlib import Path
import bpy,json
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;base=json.loads((B/'reports/R132_build_report.json').read_text())['file'];P=json.loads((B/'reports/R133_texture_receipt.json').read_text());out=B/'scenes/MUDAM_R133_PARK_YOL_KAPLAMALARI_v004.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/base));o=bpy.data.objects['R38_PARK_APPROACH_GROUND'];o.data=o.data.copy();me=o.data;UV='R133_ROUTE_METRIC_UV';uv=me.uv_layers.new(name=UV);me.uv_layers.active=uv;m=bpy.data.materials.new('R133_PARK_ROUTE_ATLAS_CANDIDATE');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.85;un=nt.nodes.new('ShaderNodeUVMap');un.uv_map=UV
for suffix in ['basecolor','normal']:
 im=bpy.data.images.load(str(B/'textures'/f'R133_park_routes_{suffix}.png'));im.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color';im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND';nt.links.new(un.outputs['UV'],tex.inputs['Vector'])
 if suffix=='basecolor':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 else:
  normal=nt.nodes.new('ShaderNodeNormalMap');normal.uv_map=UV;normal.inputs['Strength'].default_value=.45;nt.links.new(tex.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
x0,y0,x1,y1=P['bounds'];slot=len(me.materials);me.materials.append(m);faces=[]
for f in me.polygons:
 if f.normal.z<.99:continue
 f.material_index=slot
 for li in f.loop_indices:
  p=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=((p.x-x0)/(x1-x0),(p.y-y0)/(y1-y0))
 faces.append(dict(face=f.index,material=m.name,u=[1,0,0],v=[0,1,0],repeat_m=[x1-x0,y1-y0],origin=[x0,y0],area=f.area))
assert faces;m['source_ids']='OSM83345393,OSM49910981,OSM50643005,063,096';m['limits']='Mapped route surface families; atlas patterns, module, colour, widths and relief unmeasured';o['surface_revision']='R133';o['surface_limits']=m['limits'];bpy.context.scene['stage']='R133 mapped route finish atlas';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R133_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(base).name,changed_inherited_objects=[o.name],closed_objects=[],surface_objects=[dict(name=o.name,faces=faces)],uv_map=UV,materials=[m.name],routes=P['routes'],atlas_bounds=P['bounds'],route_width_m=P['width_m'],geometry_changed=False,construction_acceptance=False),indent=2)+'\n')
