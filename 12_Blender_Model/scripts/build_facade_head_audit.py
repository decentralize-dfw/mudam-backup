"""R36: camera-supported head correction; no change to source room boundaries."""
from pathlib import Path
import bpy,bmesh,json,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model'
P=json.loads((B/'config/facade_head_audit.json').read_text());prior=json.loads((B/'reports/R27_build_report.json').read_text());surface=json.loads((B/'reports/R32_build_report.json').read_text());Q=json.loads((B/'config/gallery_reveals_revised.json').read_text())
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R36_CEPHE_BASLIK_KONTROL_{version}.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));changed=[];old=P['old_head_z'];new=P['new_head_z'];sill=P['sill_z'];fw=Q['frame_width_m'];a=Vector(prior['origin']);inside=Vector(prior['inside'])
for name in prior['closed_objects']:
 o=bpy.data.objects[name];o.data=o.data.copy()
 for v in o.data.vertices:
  z=v.co.z
  if abs(z-old)<1e-4:v.co.z=new
  elif abs(z-(old-fw))<1e-4:v.co.z=new-fw
  elif sill+fw+.001<z<old:v.co.z=sill+(z-sill)*(new-sill)/(old-sill)
 o.data.update();o['revision']='R36';o['head_z_candidate']=new;o['source_audit']='reports/R36_facade_camera_audit.json';o['assumption_note']='Head revised from conditional photo 116 rays. Deeper glazing trial rejected because it intersects PDF cloak wall; original XY depth preserved pending A01. Floor/room identity conflict A01 remains open; not metric survey.';changed.append(name)
# Preserve metric texel scale after height correction, using the R32 face bases.
for row in surface['surface_objects']:
 if row['name'] not in changed:continue
 o=bpy.data.objects[row['name']];uv=o.data.uv_layers.get(row['uv_map'])
 for face in row['faces']:
  u,v=Vector(face['u']),Vector(face['v'])
  for li in o.data.polygons[face['face']].loop_indices:
   q=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/3.2,q.dot(v)/2.4)
root=bpy.data.collections.new('P08_R36_WINDOW_THRESHOLDS');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];a=Vector(prior['origin']);axis=Vector(prior['axis']);inside=Vector(prior['inside']);up=Vector((0,0,1))
fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
for op in prior['openings']:
 op['head']=new;op['glass_center']=list(a+axis*((op['start']+op['end'])/2)+inside*Q['recess_depth_m']+up*((sill+new)/2))
bpy.context.scene['stage']='R36 conditional facade head audit';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R36_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
result=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=changed+made,changed_inherited_objects=changed,new_objects=made,openings=prior['openings'],origin=list(a),axis=list(axis),inside=list(inside),head_z=new,sill_z=sill,construction_acceptance=False)
(B/'reports/R36_build_report.json').write_text(json.dumps(result,indent=2),encoding='utf8')
