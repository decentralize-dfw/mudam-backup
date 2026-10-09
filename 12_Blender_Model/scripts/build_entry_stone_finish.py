"""R60: source008/011/012/013 entry stone joints and linear canopy underside finish."""
from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R59_KOPRU_TAS_DOSEME_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R60_GIRIS_TAS_TAVAN_YUZEY_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));UV='R60_ENTRY_METRIC_UV';up=Vector((0,0,1));E=json.loads((B/'reports/R57_build_report.json').read_text());across,forward=Vector(E['axis']),Vector(E['outward']);dep=bpy.context.evaluated_depsgraph_get();rows=[];changed=[]
def clone(old,new):
 m=bpy.data.materials[old].copy();m.name=new
 for node in m.node_tree.nodes:
  if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=UV
 m['source_ids']='008,011,012,013';m['status']='entry_appearance_candidate_not_measured';m['limits']='Stone joints and linear underside appearance supported; module, colour, grain and construction unmeasured.';return m
stone=clone('R32_LIMESTONE_APPEARANCE_CANDIDATE','R60_ENTRY_LIMESTONE_CANDIDATE');soffit=clone('R53_LINEAR_MINERAL_SOFFIT_CANDIDATE','R60_ENTRY_LINEAR_MINERAL_SOFFIT_CANDIDATE')
for node in soffit.node_tree.nodes:
 if node.type=='TEX_IMAGE':
  suffix='normal' if 'normal' in node.image.name else 'basecolor';im=bpy.data.images.load(str(B/'textures'/f'R60_soffit_linear_grain_candidate_{suffix}.png'));im.colorspace_settings.name='Non-Color' if suffix=='normal' else 'sRGB';im.pack();node.image=im
targets=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.visible_get() and not o.hide_render and (o.name.startswith('P07_ENTRY_') or o.name.startswith('P07_CANOPY_FASCIA_') or o.name in ['P07_CANOPY_SLAB_ENVELOPE','P07_CORNER_SUPPORT_ENVELOPE'])]
for ob in targets:
 assert not ob.modifiers,ob.name
 ob.data=ob.data.copy();me=ob.data;me.materials.clear();me.materials.append(stone);me.materials.append(soffit);uv=me.uv_layers.get(UV) or me.uv_layers.new(name=UV);me.uv_layers.active=uv;nm=ob.matrix_world.to_3x3().inverted().transposed();faces=[]
 for f in me.polygons:
  n=(nm@f.normal).normalized();slot=1 if ob.name=='P07_CANOPY_SLAB_ENVELOPE' and n.z<-.99 else 0
  if abs(n.z)>.95:u,v=across,forward
  else:u=up.cross(n).normalized();v=n.cross(u).normalized()
  f.material_index=slot
  for li in f.loop_indices:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/3.2,q.dot(v)/2.4)
  faces.append(dict(face=f.index,u=list(u),v=list(v),repeat_m=[3.2,2.4],material=me.materials[slot].name))
 ob['surface_appearance_revision']='R60';ob['surface_source_ids']='008,011,012,013';ob['surface_appearance_status']='Limestone and linear mineral appearance; dimensions/material identity not measured';rows.append(dict(name=ob.name,faces=faces));changed.append(ob.name)
bpy.context.scene['stage']='R60 entry stone and canopy underside appearance';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R60_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=changed,surface_objects=rows,uv_map=UV,materials=[stone.name,soffit.name],evaluated_geometry_changed=False,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id'] in ['008','011','012','013']]
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R60_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=['Source photos show pale coursed stone on column, facade and fascia and a linear grain on canopy underside.','Existing R32/R53 procedural families reused with separate UV/materials. No stone/block identity, mineral species, board species or exact module is claimed.','Canopy lights, movement joints and control panels are separate unfinished details. Geometry and source plans unchanged.']),indent=2),encoding='utf8');print('R60',len(rows),'objects',sum(len(x['faces']) for x in rows),'faces')
