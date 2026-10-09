from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R66_GECIT_YAN_ARMATUR_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R67_GECIT_TAS_DOSEME_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));UV='R67_LINK_METRIC_UV';P=json.loads((B/'reports/R18_build_report.json').read_text())['portals'];u=(Vector(P[-1]['left'])-Vector(P[0]['left'])).normalized();v=(Vector(P[0]['right'])-Vector(P[0]['left'])).normalized();mat=bpy.data.materials['R43_STONE_FLOOR_APPEARANCE_CANDIDATE'].copy();mat.name='R67_LINK_DIAGONAL_STONE_CANDIDATE'
for node in mat.node_tree.nodes:
 if node.type in ['UVMAP','NORMAL_MAP']:node.uv_map=UV
 if node.type=='TEX_IMAGE':
  suffix='normal' if 'normal' in node.image.name else 'basecolor';im=bpy.data.images.load(str(B/'textures'/f'R67_diagonal_floor_candidate_{suffix}.png'));im.colorspace_settings.name='Non-Color' if suffix=='normal' else 'sRGB';im.pack();node.image=im
mat['source_ids']='067';mat['status']='diagonal_joint_family_supported_pattern_unmeasured';mat['limits']='900mm alternating-diagonal cells and1.2mm joints are replaceable appearance candidates.';rows=[];changed=[]
for name in ['P05_LINK_FLOOR','R11_LINK_THRESHOLD']:
 ob=bpy.data.objects[name];ob.data=ob.data.copy();me=ob.data;slot=len(me.materials);me.materials.append(mat);uv=me.uv_layers.new(name=UV);me.uv_layers.active=uv;faces=[];nm=ob.matrix_world.to_3x3().inverted().transposed()
 for f in me.polygons:
  if (nm@f.normal).normalized().z<.99:continue
  f.material_index=slot;faces.append(dict(face=f.index,u=list(u),v=list(v),repeat_m=[3.6,3.6],material=mat.name))
  for li in f.loop_indices:
   q=ob.matrix_world@me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/3.6,q.dot(v)/3.6)
 assert faces,name
 ob['floor_appearance_revision']='R67';ob['surface_source_ids']='067';ob['floor_appearance_limits']='Triangular joint family only; actual slab dimensions,rotation and pattern unmeasured';rows.append(dict(name=name,faces=faces));changed.append(name)
bpy.context.scene['stage']='R67 link pale stone diagonal joint candidate';bpy.context.scene['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R67_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=changed,surface_objects=rows,uv_map=UV,materials=[mat.name],evaluated_geometry_changed=False,construction_acceptance=False),indent=2),encoding='utf8')
sources=[s for s in json.loads((B/'references/source_manifest.json').read_text()) if s['id']=='067']
for s in sources:assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256']
(B/'reports/R67_source_receipt.json').write_text(json.dumps(dict(sources=sources,limits=['Two inherited floor objects,top faces only; openings,levels and thickness retained.','Diagonal triangular joints visible in067; chosen repeat,orientation,colour and all module sizes unmeasured.','Pavilion main floor and movable white box not changed.']),indent=2),encoding='utf8')
