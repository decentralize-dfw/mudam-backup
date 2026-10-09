"""R59: subdivide unchanged deck surfaces for dark paving and pale edge strips."""
from pathlib import Path
import bpy,bmesh,json,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R58_KOPRU_CAM_KORKULUK_v005.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R59_KOPRU_TAS_DOSEME_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));dep=bpy.context.evaluated_depsgraph_get();Q=json.loads((B/'reports/R58_build_report.json').read_text());P=json.loads((B/'config/site_bridges.json').read_text());ob=bpy.data.objects['R34_APPROACH_CONTINUOUS_DECK'];me=bpy.data.meshes.new_from_object(ob.evaluated_get(dep),preserve_all_data_layers=True,depsgraph=dep);ob.modifiers.clear();ob.data=me;assert ob.matrix_world.is_identity;bm=bmesh.new();bm.from_mesh(me);regions=[];up=Vector((0,0,1))
for run in Q['guard_runs']:
 a,b=Vector(run['start']),Vector(run['end']);u=(b-a).normalized();n=u.cross(up).normalized();bridge=next(w for w in P['ways'] if w['id']==('759551375' if run['way']=='759554470' else '759551376'));center=sum((Vector((x-293425,y-5499960,0)) for x,y in bridge['xy']),Vector())/len(bridge['xy']);n=-n if n.dot(center-(a+b)/2)<0 else n
 # The pale band includes the guard centerline and extends inward; deck outline is preserved.
 regions.append(dict(a=list(a),u=list(u),n=list(n),length=(b-a).length,width=.65))
 for p,normal in [(a-u*.03,u),(b+u*.03,u),(a-n*.05,n),(a+n*.65,n)]:
  bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=p,plane_no=normal,clear_inner=False,clear_outer=False)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();UV='R59_APPROACH_METRIC_UV';uv=me.uv_layers.new(name=UV);me.uv_layers.active=uv
paving=bpy.data.materials.new('R59_DARK_STONE_PAVING_CANDIDATE');paving.use_nodes=True;nt=paving.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86;un=nt.nodes.new('ShaderNodeUVMap');un.uv_map=UV
for suffix in ['basecolor','normal']:
 im=bpy.data.images.load(str(B/'textures'/f'R59_paving_candidate_{suffix}.png'));im.colorspace_settings.name='sRGB' if suffix=='basecolor' else 'Non-Color';im.pack();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.links.new(un.outputs['UV'],tex.inputs['Vector'])
 if suffix=='basecolor':nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 else:
  nn=nt.nodes.new('ShaderNodeNormalMap');nn.uv_map=UV;nn.inputs['Strength'].default_value=.45;nt.links.new(tex.outputs['Color'],nn.inputs['Color']);nt.links.new(nn.outputs['Normal'],bs.inputs['Normal'])
edge=bpy.data.materials['R53_REVEAL_SILL_STONE_CANDIDATE'].copy();edge.name='R59_PALE_STONE_EDGE_CANDIDATE'
for node in edge.node_tree.nodes:
 if node.type=='UVMAP':node.uv_map=UV
 if node.type=='NORMAL_MAP':node.uv_map=UV
slots={}
for mat in [paving,edge]:slots[mat.name]=len(me.materials);me.materials.append(mat)
e=json.loads((B/'reports/R57_build_report.json').read_text());ex,en=Vector(e['axis']),Vector(e['outward']);faces=[]
for f in me.polygons:
 c=f.center;normal=f.normal;chosen=None;u=v=None;repeat=None
 if normal.z>.99 and abs(c.z)<1e-4:
  chosen=paving;u,v=ex,en;repeat=[3.2,3.2]
  for q in regions:
   a,ru,rn=Vector(q['a']),Vector(q['u']),Vector(q['n']);d=c-a;t=d.dot(ru);off=d.dot(rn)
   if -.0301<t<q['length']+.0301 and -.0501<off<q['width']+.0001:chosen=edge;u,v=ru,rn;repeat=[3.6,3.6];break
 elif abs(normal.z)<.01:
  chosen=edge;u=up.cross(normal).normalized();v=up;repeat=[3.6,3.6]
 if chosen:
  f.material_index=slots[chosen.name]
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/repeat[0],p.dot(v)/repeat[1])
  faces.append(dict(index=f.index,material=chosen.name,u=list(u),v=list(v),repeat=repeat))
ob['surface_revision']='R59';ob['surface_sources']='008,011,012,013';ob['surface_limits']='Dark small paving and pale edge band appearance candidates. 0.65m band and 0.1x0.08m stone module unmeasured. Surface subdivision only; deck outline and elevations unchanged.';bpy.context.scene['stage']='R59 approach paving and pale edge finish';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R59_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=[ob.name],closed_objects=[],surface_object=ob.name,faces=faces,regions=regions,uv_map=UV,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['008','011','012','013']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R59_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=json.loads((B/'reports/R59_texture_receipt.json').read_text())['limits']+['Pale band width0.65m and deck side cladding layout are candidates; no physical survey.']),indent=2),encoding='utf8');print('R59',len(faces),'material faces')
