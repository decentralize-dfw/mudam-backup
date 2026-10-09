"""Reconcile the west end wall with the saved curve endpoint; keep all heights."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R76_MERDIVEN_DUVAR_UCLARI_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R77_BATI_UC_DUVAR_BAGLANTISI_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base))
names=['P05_WEST_END','P11_WEST_STONE_BASE_17'];obs=[bpy.data.objects[n] for n in names];vs=[[o.matrix_world@v.co for v in o.data.vertices] for o in obs];before={n:[list(v) for v in a] for n,a in zip(names,vs)}
def xy(v):return Vector((v.x,v.y,0))
def cross(a,b):return a.x*b.y-a.y*b.x
p=xy(vs[1][1]);back_start=xy(vs[0][5]);back_target=p+xy(vs[0][4]-vs[0][0]);a=xy(vs[1][4]);u=xy(vs[1][5])-a;v=back_target-back_start;m=a+u*(cross(back_start-a,v)/cross(u,v));assert (m-p).length<1
for obj,verts,indices in [(obs[0],vs[0],[4,7]),(obs[1],vs[1],[5,6])]:
 for i in indices:verts[i]=Vector((m.x,m.y,verts[i].z))
for i in [0,3]:vs[0][i]=Vector((p.x,p.y,vs[0][i].z))
for obj,verts in zip(obs,vs):
 obj.data=obj.data.copy();inv=obj.matrix_world.inverted()
 for v,w in zip(obj.data.vertices,verts):v.co=inv@w
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update();obj['wall_end_revision']='R77 plan endpoint reconciliation; heights retained, roof-edge height unresolved'
r=dict(file=out.relative_to(R).as_posix(),base_scene=base,closed_objects=names,changed_inherited_objects=names,before_world_vertices=before,shared_front=list(p),shared_back=list(m),z_overlap=[0,min(max(v.z for v in a) for a in vs)],allowed_vertex_indices={names[0]:[0,3,4,7],names[1]:[5,6]},source_ids=['102','103','093','097'],front_endpoint_translation_m=(p-xy(Vector(before[names[0]][0]))).length,construction_acceptance=False,limits=['End face reaches existing canonical curve endpoint 862,161; no new survey measurement.','All heights retained. West roof/end-wall height and glass interface require the later dedicated roof stage.','Old thicknesses remain candidates; shared back faces mitered without changing the rest of the curve.'])
bpy.context.scene['stage']='R77 west end wall connection';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R77_SOURCE_AND_LIMITS').write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(B/'reports/R77_build_report.json').write_text(json.dumps(r,indent=2),encoding='utf8');print('R77 endpoint adjustment',r['front_endpoint_translation_m'])
