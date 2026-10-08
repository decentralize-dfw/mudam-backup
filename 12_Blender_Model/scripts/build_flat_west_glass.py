"""R12: planar glass inserts in the existing candidate west frame network."""
from pathlib import Path
import bpy,bmesh,json,sys,numpy as np
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';base='MUDAM_R11_DOGU_UC_CAM_v001.blend';version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R12_BATI_DUZ_CAM_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/base));rows=[];thickness=.018
for ob in bpy.context.scene.objects:
 if not ob.name.startswith('P11_WEST_') or ob.get('element_type')!='glass_panel':continue
 assert ob.type=='MESH' and len(ob.data.vertices)==8
 old=np.array([list(v.co) for v in ob.data.vertices],dtype=float);top=old[:4];center=top.mean(axis=0);normal=np.linalg.svd(top-center)[2][-1]
 if normal[2]<0:normal=-normal
 distances=(top-center)@normal;flat=top-distances[:,None]*normal;new=np.concatenate([flat,flat-normal*thickness]);shift=np.linalg.norm(new-old,axis=1)
 assert max(shift)<.012, (ob.name,max(shift))
 me=ob.data.copy();ob.data=me
 for v,p in zip(me.vertices,new):v.co=p
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
 ob['status']='conditional_planar_insert_in_unverified_frame_network';ob['source_ids']='093,119,102';ob['assumption_note']='R12 makes the glass insert planar. Original frame network, overall surface and module counts remain conditional; no fabrication rebate acceptance.';ob['plane_deviation_m']=0.;ob['R12_max_vertex_shift_m']=float(max(shift))
 rows.append(dict(name=ob.name,old_vertices=old.tolist(),plane_center=center.tolist(),plane_normal=normal.tolist(),before_best_fit_deviation_m=float(max(abs(distances))),max_vertex_shift_m=float(max(shift)),thickness=thickness))
assert len(rows)==108,len(rows)
S=bpy.context.scene;S['stage']='R12 planar west glass candidates; frame layout unchanged';S['current_file']=out.name;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report=dict(file=out.relative_to(R).as_posix(),base_scene=base,changed_inherited_objects=[r['name'] for r in rows],panels=rows,max_shift_m=max(r['max_vertex_shift_m'] for r in rows),max_previous_best_fit_deviation_m=max(r['before_best_fit_deviation_m'] for r in rows),source_ids=['093','119','102'],frame_network_modified=False,construction_acceptance=False);(B/'reports/R12_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('R12_PANELS',len(rows),report['max_shift_m'])
