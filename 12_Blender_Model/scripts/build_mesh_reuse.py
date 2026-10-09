"""R41 loss-bounded data reuse, never merging object identities or changing topology."""
from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R39_GIRIS_TAVAN_BUTUNLUGU_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R41_MESH_PAYLASIMI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));groups={};before=len({o.data.as_pointer() for o in bpy.context.scene.objects if o.type=='MESH'});changed=[];records=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.modifiers or o.constraints or o.vertex_groups or o.data.shape_keys or o.data.has_custom_normals or not o.data.vertices or o.hide_render or not o.visible_get():continue
 me=o.data;origin=me.vertices[0].co.copy();coords=[[round(float(x),5) for x in v.co-origin] for v in me.vertices];polys=[(list(p.vertices),p.material_index,p.use_smooth) for p in me.polygons];uv=[(layer.name,[[round(float(x),8) for x in d.uv] for d in layer.data]) for layer in me.uv_layers];key=hashlib.sha256(repr([coords,polys,uv,[m.name if m else None for m in me.materials]]).encode()).hexdigest();groups.setdefault(key,[]).append((o,origin))
for key,items in groups.items():
 if len(items)<2:continue
 ref,ref_origin=items[0];me=ref.data.copy();me.name=f'R41_SHARED_{len(records):04d}'
 for v in me.vertices:v.co-=ref_origin
 me.update();members=[]
 for ob,origin in items:
  before_coords=[ob.matrix_world@v.co for v in ob.data.vertices];matrix=ob.matrix_world@Matrix.Translation(origin);err=max((matrix@v.co-p).length for v,p in zip(me.vertices,before_coords))
  if err>2e-5:continue
  ob.data=me;ob.matrix_world=matrix;ob['mesh_reuse_revision']='R41';ob['mesh_reuse_max_vertex_delta_m']=err;changed.append(ob.name);members.append(dict(name=ob.name,max_vertex_delta_m=err))
 if len(members)>1:records.append(dict(mesh=me.name,members=members,vertices=len(me.vertices),polygons=len(me.polygons)))
after=len({o.data.as_pointer() for o in bpy.context.scene.objects if o.type=='MESH'});assert after<before
# Drop only newly unused mesh data blocks; no scene objects or source references removed.
unused=[m for m in bpy.data.meshes if m.users==0]
for m in unused:bpy.data.meshes.remove(m)
bpy.context.scene['stage']='R41 shared mesh data, unchanged architecture';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R41_LIMITS').write('Data storage optimization only. World vertex delta <=0.02 mm; this is a numerical regression tolerance, NOT building measurement accuracy. All object names, source properties, topology and visible materials retained. Source model uncertainties remain.');bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R41_build_report.json').write_text(json.dumps(dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=changed,shared_groups=records,mesh_datablocks_before=before,mesh_datablocks_after=after,world_vertex_tolerance_m=.00002,construction_acceptance=False),indent=2),encoding='utf8');print('R41',before,after,len(changed))
