from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';base='MUDAM_R45_TAS_TUTAMAK_v005.blend';out=B/'scenes'/f'MUDAM_R46_MERDIVEN_TAS_YUZEY_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));T=json.loads((B/'reports/R45_build_report.json').read_text());chain=[Vector(p) for p in T['front_chain_world']];lengths=[0.]
for a,b in zip(chain,chain[1:]):lengths.append(lengths[-1]+(b-a).length)
def arc(p):
 best=(1e20,0)
 for i,(a,b) in enumerate(zip(chain,chain[1:])):
  d=b-a;t=max(0,min(1,Vector((p.x-a.x,p.y-a.y,0)).dot(d)/d.length_squared));q=a+d*t;err=(Vector((p.x,p.y,0))-q).length_squared
  if err<best[0]:best=(err,lengths[i]+t*d.length)
 return best[1]
UV='R46_STONE_FINISH_UV';grain=bpy.data.materials.new('R46_STONE_GRAIN_APPEARANCE_CANDIDATE');grain.use_nodes=True;nt=grain.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.36;uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map=UV
for suffix in ['basecolor','normal']:
 im=bpy.data.images.load(str(B/'textures'/f'R46_stone_grain_candidate_{suffix}.png'));im.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color';im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT';nt.links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
 if suffix=='basecolor':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 else:
  nn=nt.nodes.new('ShaderNodeNormalMap');nn.uv_map=UV;nn.inputs['Strength'].default_value=.15;nt.links.new(tex.outputs['Color'],nn.inputs['Color']);nt.links.new(nn.outputs['Normal'],bs.inputs['Normal'])
joint=bpy.data.materials['R32_LIMESTONE_APPEARANCE_CANDIDATE'].copy();joint.name='R46_STONE_JOINT_APPEARANCE_CANDIDATE'
for node in joint.node_tree.nodes:
 if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=UV
targets=['R45_STAIR_RECESS_CONTINUOUS','R45_STONE_GRIP_FINISH_CANDIDATE','R04_STONE_SIDE_ENVELOPE','R04_RECESS_JAMB_FOOT','R04_RECESS_TOP_BELOW_LANDING','R04_RECESS_TOP_LINTEL','R04_RECESS_HEAD','R03_PODIUM_1_REPAIRED','R03_PODIUM_2_REPAIRED','R03_PODIUM_3_WITH_RECESS']+[f'R04_TREAD_ENVELOPE_{i:02}' for i in range(1,29)];rows=[]
for name in targets:
 ob=bpy.data.objects[name];assert not ob.hide_render;ob.data=ob.data.copy();me=ob.data;me.materials.clear();me.materials.append(grain);me.materials.append(joint);uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;nm=ob.matrix_world.to_3x3().inverted().transposed();curved=name.startswith('R45_');stair=name.startswith('R04_TREAD') or name.startswith('R03_PODIUM');faces=[]
 for face in me.polygons:
  n=(nm@face.normal).normalized();use_joint=((curved and abs(n.z)<.65) or abs(n.z)<.05) and not stair;face.material_index=int(use_joint);sx,sy=(3.2,2.4) if use_joint else (2.,2.);u=Vector((-n.y,n.x,0)).normalized() if abs(n.z)<.95 else Vector((1,0,0));u=-u if u.x<-.00001 else u;v=Vector((0,0,1)) if abs(n.z)<.95 else Vector((0,1,0))
  projection='wall_arc_height' if curved and abs(n.z)<.65 else 'world_plane'
  for li in face.loop_indices:
   p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(arc(p)/sx,p.z/sy) if projection=='wall_arc_height' else (p.dot(u)/sx,p.dot(v)/sy)
  coords=[uv.data[li].uv.copy() for li in face.loop_indices];area=abs(sum(a.x*b.y-b.x*a.y for a,b in zip(coords,coords[1:]+coords[:1])))/2
  if area<1e-10:
   projection='world_plane'
   # Build a true tangent basis for sloping end/reveal faces.
   u=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.95 else Vector((1,0,0));v=n.cross(u).normalized()
   for li in face.loop_indices:
    p=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/sx,p.dot(v)/sy)
  faces.append(dict(face=face.index,joint=use_joint,projection=projection,u=list(u),v=list(v),repeat=[sx,sy]))
 ob['surface_appearance_revision']='R46';ob['surface_appearance_limits']='Joint module, colour and grain are procedural candidates; no displacement';rows.append(dict(name=name,faces=faces))
for mat in [grain,joint]:mat['source_ids']='021,022,023,024';mat['status']='procedural_appearance_candidate_not_measured'
bpy.context.scene['stage']='R46 upper stair stone finish candidate';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=targets,surface_objects=rows,uv_map=UV,front_chain_world=T['front_chain_world'],materials=[grain.name,joint.name],geometry_changed=False,construction_acceptance=False);(B/'reports/R46_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');m=json.loads((B/'references/source_manifest.json').read_text(encoding='utf8'));sources=[x for x in m if x['id'] in ['021','022','023','024','101','102','103']]
for x in sources:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
(B/'reports/R46_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits='Material family only. Colour, module, finish and hidden stone assembly not surveyed.'),ensure_ascii=False,indent=2),encoding='utf8')
