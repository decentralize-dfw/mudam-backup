from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
B=Path(__file__).resolve().parents[1];R=B.parent;r=json.loads((B/'reports/R134_build_report.json').read_text());out=B/'scenes/MUDAM_R135_ODITORYUM_AHSAP_DAMAR_v001.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(R/r['file']));UV='R135_WOOD_METRIC_UV'
m=bpy.data.materials['R19_WOOD_FINISH_CANDIDATE'].copy();m.name='R135_AUDITORIUM_WOOD_GRAIN_CANDIDATE';nt=m.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(B/'textures/R135_auditorium_wood_basecolor.png'));tex.image.pack();uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map=UV;nt.links.new(uvn.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],nt.nodes.get('Principled BSDF').inputs['Base Color']);rows=[]
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or o.hide_render or not o.visible_get():continue
 ids=[i for i,ma in enumerate(o.data.materials) if ma and ma.name=='R19_WOOD_FINISH_CANDIDATE']
 if not ids:continue
 o.data=o.data.copy();me=o.data;uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;slot=len(me.materials);me.materials.append(m);nm=o.matrix_world.to_3x3().inverted().transposed();faces=[]
 for f in me.polygons:
  if f.material_index not in ids:continue
  n=(nm@f.normal).normalized();u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.95 else Vector((1,0,0));v=n.cross(u).normalized()
  if v.z<0:v=-v
  f.material_index=slot
  for li in f.loop_indices:
   p=o.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/1.2,p.dot(v)/2.4)
  faces.append(dict(face=f.index,material=m.name,u=list(u),v=list(v),repeat_m=[1.2,2.4]))
 if faces:rows.append(dict(name=o.name,faces=faces));o['surface_appearance_revision']='R135';o['surface_limits']='Vertical wood grain appearance from 073. Species, veneer and repeat dimensions unmeasured.'
assert rows
bpy.context.scene['stage']='R135 auditorium timber grain';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R135_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=Path(r['file']).name,changed_inherited_objects=[x['name'] for x in rows],closed_objects=[],surface_objects=rows,uv_map=UV,materials=[m.name],geometry_changed=False,source_ids=['071','072','073','076'],construction_acceptance=False),indent=2)+'\n');print('R135',len(rows),'objects')
