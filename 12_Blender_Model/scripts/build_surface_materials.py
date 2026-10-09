"""R32 metric UV appearance layers; geometry must not move."""
from pathlib import Path
import bpy,json,sys,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/surface_materials.json').read_text());version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R32_TAS_AHSAP_YUZEY_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));changed=[];rows=[];UV='R32_METRIC_SURFACE_UV';SX,SY=P['repeat_m']
def material(label,roughness):
 m=bpy.data.materials.new('R32_'+label.upper()+'_APPEARANCE_CANDIDATE');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=roughness;uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map=UV
 for suffix in ['basecolor','normal']:
  image=bpy.data.images.load(str(B/'textures'/f'R32_{label}_candidate_{suffix}.png'),check_existing=True);image.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color';image.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='REPEAT';nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
  if suffix=='basecolor':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
  else:
   normal=nt.nodes.new('ShaderNodeNormalMap');normal.uv_map=UV;normal.inputs['Strength'].default_value=P['normal_strength'];nt.links.new(tex.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],bs.inputs['Normal'])
 m['status']='procedural_appearance_candidate_not_measured';m['repeat_m']=json.dumps(P['repeat_m']);m['source_ids']=','.join(P['source_ids']);return m
stone=material('limestone',P['stone_roughness']);wood=material('wood',P['wood_roughness']);white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'];facade_inside=Vector(json.loads((B/'reports/R27_build_report.json').read_text())['inside']);finish_faces=[]
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or not ob.visible_get() or ob.hide_render:continue
 names=[m.name if m else '' for m in ob.data.materials];stone_ok=P['stone_material_name'] in names and any(ob.name.startswith(p) for p in P['stone_prefixes']);wood_ok=P['wood_material_name'] in names
 if not stone_ok and not wood_ok:continue
 me=ob.data.copy();ob.data=me;uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;world=[ob.matrix_world@v.co for v in me.vertices];normal_matrix=ob.matrix_world.to_3x3().inverted().transposed();selected=[]
 if wood_ok:
  pts=np.array([[v.x,v.y] for v in world]);vals,vecs=np.linalg.eigh(np.cov(pts.T));u=Vector((*vecs[:,np.argmax(vals)],0));u=-u if u.x<0 else u;v=Vector((-u.y,u.x,0));wood_basis=[list(u),list(v)]
 else:wood_basis=None
 slot={}
 if ob.name.startswith('R27_') and stone_ok:slot['white']=len(me.materials);me.materials.append(white)
 for key,mat in [('stone',stone),('wood',wood)]:
  if (key=='stone' and stone_ok) or (key=='wood' and wood_ok):slot[key]=len(me.materials);me.materials.append(mat)
 for face in me.polygons:
  original=names[face.material_index];n=(normal_matrix@face.normal).normalized();kind=None
  if 'white' in slot and original==P['stone_material_name'] and n.dot(facade_inside)>.99:
   face.material_index=slot['white'];finish_faces.append(dict(name=ob.name,face=face.index,material=white.name));continue
  if stone_ok and original==P['stone_material_name'] and abs(n.z)<.05:
   kind='stone';u=Vector((-n.y,n.x,0)).normalized();u=-u if (u.x<-.0001 or (abs(u.x)<.0001 and u.y<0)) else u;v=Vector((0,0,1))
  elif wood_ok and original==P['wood_material_name'] and n.z>.95:kind='wood';u,v=map(Vector,wood_basis)
  if kind:
   face.material_index=slot[kind]
   for li in face.loop_indices:
    q=world[me.loops[li].vertex_index];uv.data[li].uv=(q.dot(u)/SX,q.dot(v)/SY)
   selected.append(dict(face=face.index,kind=kind,u=list(u),v=list(v)))
 if selected:
  changed.append(ob.name);rows.append(dict(name=ob.name,faces=selected,uv_map=UV));ob['surface_appearance_status']='R32 procedural candidate; module and colour unmeasured';ob['surface_source_ids']=','.join(P['source_ids'])
 # Empty added slots are harmless but still a material change and must be reported.
 elif slot:changed.append(ob.name);rows.append(dict(name=ob.name,faces=[],uv_map=UV))
bpy.context.scene['stage']='R32 stone joint and timber appearance candidates';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R32_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R32_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=[],changed_inherited_objects=changed,surface_objects=rows,interior_finish_faces=finish_faces,materials=[stone.name,wood.name],texture_repeat_m=P['repeat_m'],geometry_changed=False,construction_acceptance=False),indent=2),encoding='utf8');print('Surface targets',len(rows),'faces',sum(len(r['faces']) for r in rows))
